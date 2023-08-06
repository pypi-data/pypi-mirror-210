# Copyright 2020 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from grpc import StatusCode
import itertools
import logging
import os
import re
import shutil
import tempfile

from mercurial import (
    archival,
    pycompat,
    scmutil,
    hg,
    node,
)
from mercurial.commands import (
    bundle,
)

from heptapod.gitlab.branch import gitlab_branch_from_ref
from hgext3rd.heptapod import (
    backup_additional,
    restore_additional,
)
from hgext3rd.heptapod.branch import set_default_gitlab_branch
from hgext3rd.heptapod.special_ref import write_gitlab_special_ref
from hgext3rd.heptapod.keep_around import (
    create_keep_around,
    parse_keep_around_ref,
)

from .. import (
    manifest,
    message,
)
from ..branch import (
    iter_gitlab_branches,
)
from ..errors import (
    ServiceError,
    not_implemented,
)
from ..gitlab_ref import (
    parse_special_ref,
    ensure_special_refs,
)
from ..logging import LoggerAdapter
from ..path import (
    InvalidPath,
    validate_relative_path,
)
from ..repository import (
    get_gitlab_project_full_path,
    set_gitlab_project_full_path,
    unbundle,
)
from ..revision import (
    ALL_CHANGESETS,
    CHANGESET_HASH_BYTES_REGEXP,
    gitlab_revision_changeset,
    resolve_revspecs_positive_negative,
)
from ..servicer import HGitalyServicer
from ..stream import (
    WRITE_BUFFER_SIZE,
    streaming_request_tempfile_extract,
)
from ..util import (
    chunked,
)
from ..stub.repository_pb2 import (
    BackupCustomHooksRequest,
    BackupCustomHooksResponse,
    CreateBundleRequest,
    CreateBundleResponse,
    CreateBundleFromRefListRequest,
    CreateBundleFromRefListResponse,
    CreateRepositoryRequest,
    CreateRepositoryResponse,
    CreateRepositoryFromBundleRequest,
    CreateRepositoryFromBundleResponse,
    FetchBundleRequest,
    FetchBundleResponse,
    FindMergeBaseRequest,
    FindMergeBaseResponse,
    FullPathRequest,
    FullPathResponse,
    GetRawChangesRequest,
    GetRawChangesResponse,
    RepositoryExistsRequest,
    RepositoryExistsResponse,
    GetArchiveRequest,
    GetArchiveResponse,
    HasLocalBranchesRequest,
    HasLocalBranchesResponse,
    RemoveRepositoryRequest,
    RemoveRepositoryResponse,
    RestoreCustomHooksRequest,
    RestoreCustomHooksResponse,
    SearchFilesByContentRequest,
    SearchFilesByContentResponse,
    SearchFilesByNameRequest,
    SearchFilesByNameResponse,
    SetFullPathRequest,
    SetFullPathResponse,
    WriteRefRequest,
    WriteRefResponse,
    ApplyGitattributesRequest,
    ApplyGitattributesResponse,
)
from ..stub.repository_pb2_grpc import RepositoryServiceServicer
from ..stub.shared_pb2 import (
    Repository,
)


base_logger = logging.getLogger(__name__)
DEFAULT_BRANCH_FILE_NAME = b'default_gitlab_branch'
ARCHIVE_FORMATS = {
    GetArchiveRequest.Format.Value('ZIP'): b'zip',
    GetArchiveRequest.Format.Value('TAR'): b'tar',
    GetArchiveRequest.Format.Value('TAR_GZ'): b'tgz',
    GetArchiveRequest.Format.Value('TAR_BZ2'): b'tbz2',
}
SEARCH_FILES_FILTER_MAX_LENGTH = 1000
"""Maximum size of regular expression in SearchFiles methods.

Value taken from Gitaly's `internal/gitaly/service/repository/search_files.go'
"""


class RepositoryCreationError(ServiceError):
    """Specific exception for creation problems."""


class RepositoryServicer(RepositoryServiceServicer, HGitalyServicer):
    """RepositoryServiceService implementation.
    """

    STATUS_CODE_STORAGE_NOT_FOUND = StatusCode.INVALID_ARGUMENT

    def FindMergeBase(self,
                      request: FindMergeBaseRequest,
                      context) -> FindMergeBaseResponse:
        repo = self.load_repo(request.repository, context)
        if len(request.revisions) < 2:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          'FindMergeBase: at least 2 revisions are required')

        ctxs = []
        for rev in request.revisions:
            ctx = gitlab_revision_changeset(repo, rev)
            if ctx is None:
                return FindMergeBaseResponse()
            ctxs.append(ctx)

        # Some of the changesets may be obsolete (if addressed by SHAs).
        # The GCA may be obsolete as well (meaning that one of ctxs is
        # also obsolete). TODO add test for obsolete cases
        repo = repo.unfiltered()
        gca = repo.revs(b"ancestor(%ld)", ctxs).first()
        base = repo[gca].hex() if gca is not None else ''
        return FindMergeBaseResponse(base=base)

    def RepositoryExists(self,
                         request: RepositoryExistsRequest,
                         context) -> RepositoryExistsResponse:
        try:
            self.load_repo_inner(request.repository, context)
            exists = True
        except KeyError as exc:
            if exc.args[0] == 'storage':
                context.abort(
                    StatusCode.INVALID_ARGUMENT,
                    f'GetStorageByName: no such storage: "{exc.args[1]}"'
                )
            exists = False
        except ValueError as exc:
            context.abort(StatusCode.INVALID_ARGUMENT, exc.args[0])

        return RepositoryExistsResponse(exists=exists)

    def GetArchive(self,
                   request: GetArchiveRequest,
                   context) -> GetArchiveResponse:
        repo = self.load_repo(request.repository, context)
        ctx = repo[request.commit_id]

        patterns = []
        path = request.path
        if path:
            try:
                path = validate_relative_path(repo, path)
            except InvalidPath:
                context.abort(StatusCode.INVALID_ARGUMENT,
                              "Invalid path: '%s'" % path)

            patterns.append(b"path:" + path)

        match = scmutil.match(ctx, pats=patterns, opts={})

        # using an anonymous (not linked) temporary file
        # TODO OPTIM check if archive is not by any chance
        # using a tempfile already…
        with tempfile.TemporaryFile(
                mode='wb+',  # the default, but let's insist on binary here
                buffering=WRITE_BUFFER_SIZE) as tmpf:
            archival.archive(
                repo,
                tmpf,
                ctx.node(),
                ARCHIVE_FORMATS[request.format],
                True,  # decode (TODO this is the default but what is this?)
                match,
                request.prefix.encode(),
                subrepos=False  # maybe later, check what GitLab's standard is
            )

            tmpf.seek(0)
            while True:
                data = tmpf.read(WRITE_BUFFER_SIZE)
                if not data:
                    break
                yield GetArchiveResponse(data=data)

    def HasLocalBranches(self,
                         request: HasLocalBranchesRequest,
                         context) -> HasLocalBranchesResponse:
        repo = self.load_repo(request.repository, context)
        # the iteration should stop as soon at first branchmap entry which
        # has a non closed head (but all heads in that entry would be checked
        # to be non closed)
        return HasLocalBranchesResponse(value=any(iter_gitlab_branches(repo)))

    def WriteRef(
            self,
            request: WriteRefRequest,
            context) -> WriteRefResponse:
        """Create or update a GitLab ref.

        The reference Gitaly implementation treats two cases, ``HEAD`` being
        the only supported symbolic ref. Excerpt as of GitLab 13.9.0::

          func (s *server) writeRef(ctx context.Context,
                                    req *gitalypb.WriteRefRequest) error {
            if string(req.Ref) == "HEAD" {
              return s.updateSymbolicRef(ctx, req)
            }
            return updateRef(ctx, s.cfg, s.gitCmdFactory, req)
          }

        On the other hand, the target revision is fully resolved, even
        when setting a non-symbolic ref.
        """
        logger = LoggerAdapter(base_logger, context)
        ref, target = request.ref, request.revision
        repo = self.load_repo(request.repository, context)

        try:
            special_ref_name = parse_special_ref(ref)
            if special_ref_name is not None:
                target_sha = gitlab_revision_changeset(repo, target)
                ensure_special_refs(repo)
                write_gitlab_special_ref(repo, special_ref_name, target_sha)
                return WriteRefResponse()

            keep_around = parse_keep_around_ref(ref)
            if keep_around is not None:
                if (CHANGESET_HASH_BYTES_REGEXP.match(keep_around) is None
                        or target != keep_around):
                    context.abort(
                        StatusCode.INVALID_ARGUMENT,
                        "Invalid target %r for keep-around %r. Only full "
                        "changeset ids in hexadecimal form are accepted and "
                        "target must "
                        "match the ref name" % (target, ref)
                    )

                create_keep_around(repo, target)
                return WriteRefResponse()
        except Exception:
            logger.exception(
                "WriteRef failed for Repository %r on storage %r",
                request.repository.relative_path,
                request.repository.storage_name)
            return WriteRefResponse()

        if ref != b'HEAD':
            context.abort(
                StatusCode.INVALID_ARGUMENT,
                "Setting ref %r is not implemented in Mercurial (target %r) "
                "Does not make sense in the case of branches and tags, "
                "except maybe for bookmarks." % (ref, target))

        target_branch = gitlab_branch_from_ref(target)
        if target_branch is None:
            context.abort(StatusCode.INVALID_ARGUMENT,
                          "The default GitLab branch can only be set "
                          "to a branch ref, got %r" % target)

        set_default_gitlab_branch(repo, target_branch)
        return WriteRefResponse()

    def ApplyGitattributes(self, request: ApplyGitattributesRequest,
                           context) -> ApplyGitattributesResponse:
        """Method used as testing bed for the `not_implemented` helper.

        It is unlikely we ever implement this one, and if we do something
        similar, we'll probably end up defining a ApplyHgAttributes anyway.
        """
        not_implemented(context, issue=1234567)

    def CreateRepository(self, request: CreateRepositoryRequest,
                         context) -> CreateRepositoryResponse:
        try:
            self.hg_init_repository(request.repository, context)
        finally:
            # response is the same in case of error or success
            return CreateRepositoryResponse()

    def GetRawChanges(self, request: GetRawChangesRequest,
                      context) -> GetRawChangesResponse:
        not_implemented(context, issue=79)  # pragma no cover

    def SearchFilesByName(self, request: SearchFilesByNameRequest,
                          context) -> SearchFilesByNameResponse:
        repo = self.load_repo(request.repository, context)
        changeset = gitlab_revision_changeset(repo, request.ref)
        if changeset is None:
            yield SearchFilesByNameResponse()
            return

        query = request.query
        if not query:
            context.abort(StatusCode.INVALID_ARGUMENT, "no query given")

        subdir = b'' if query == '.' else query.encode('utf8')

        miner = manifest.miner(changeset)

        filt = request.filter
        if not filt:
            rx = None
        else:
            if len(filt) > SEARCH_FILES_FILTER_MAX_LENGTH:
                context.abort(
                    StatusCode.INVALID_ARGUMENT,
                    "SearchFilesByName: filter exceeds maximum length")
            # TODO what to do for invalid Regexp? Especially with incoming
            # format being Golang's
            try:
                rx = re.compile(filt.encode('utf8'))
            except re.error as exc:
                context.abort(
                    StatusCode.INVALID_ARGUMENT,
                    f"SearchFilesByName: filter did not compile: {exc})"
                )

        start = request.offset
        end = None if request.limit == 0 else start + request.limit

        for paths in chunked(
                itertools.islice(
                    miner.file_names_by_regexp(rx, subdir),
                    start, end)
        ):
            yield SearchFilesByNameResponse(files=paths)

    def SearchFilesByContent(self, request: SearchFilesByContentRequest,
                             context) -> SearchFilesByContentResponse:
        not_implemented(context, issue=80)  # pragma no cover

    def RestoreCustomHooks(self, request: RestoreCustomHooksRequest,
                           context) -> RestoreCustomHooksResponse:
        def load_repo(req, context):
            return self.load_repo(req.repository, context)

        try:
            with streaming_request_tempfile_extract(
                    request, context,
                    first_request_handler=load_repo
            ) as (repo, tmpf):
                tmpf.flush()
                try:
                    restore_additional(repo.ui, repo,
                                       tmpf.name.encode('ascii'))
                except Exception as exc:
                    context.abort(StatusCode.INTERNAL,
                                  "Error in tarball application: %r" % exc)
        finally:
            return RestoreCustomHooksResponse()

    def BackupCustomHooks(self, request: BackupCustomHooksRequest,
                          context) -> BackupCustomHooksResponse:
        repo = self.load_repo(request.repository, context)
        with tempfile.NamedTemporaryFile(
                mode='wb+',
                buffering=WRITE_BUFFER_SIZE) as tmpf:

            # TODO we should simply have backup_additional()
            # accept a file object rather than a path.
            save_path = pycompat.sysbytes(tmpf.name)
            backup_additional(repo.ui, repo, save_path)
            tmpf.seek(0)
            while True:
                data = tmpf.read(WRITE_BUFFER_SIZE)
                if not data:
                    break
                yield BackupCustomHooksResponse(data=data)

    def RemoveRepository(self, request: RemoveRepositoryRequest,
                         context) -> RemoveRepositoryResponse:
        # The protocol comment says, as of Gitaly 14.8:
        #     RemoveRepository will move the repository to
        #     `+gitaly/tmp/<relative_path>_removed` and
        #     eventually remove it.
        # In that sentence, the "eventually" could imply that it is
        # asynchronous (as the Rails app does), but it is not in the
        # Gitaly server implementation. The renaming is done for
        # atomicity purposes.
        try:
            repo_path = self.repo_disk_path(request.repository, context)
        except KeyError as exc:
            self.handle_key_error(context, exc.args)
        except ValueError as exc:
            self.handle_value_error(context, exc.args)

        if not os.path.exists(repo_path):
            # same error message as Gitaly (probably no need to repeat
            # repo details, since request often logged client-side)
            context.abort(StatusCode.NOT_FOUND, "repository does not exist")

        trash_path = os.path.join(
            self.temp_dir(request.repository.storage_name, context),
            os.path.basename(repo_path) + b'+removed')
        # The rename being atomic, it avoids leaving a crippled repo behind
        # in case of problem in the removal.
        # TODO Gitaly also performs some kind of locking (not clear
        # if Mercurial locks would be appropriate because of the renaming)
        # and lengthy rechecks to safeguard against race conditions,
        # and finally the vote related to the multi-phase commit for praefect
        os.rename(repo_path, trash_path)

        shutil.rmtree(trash_path)  # not atomic
        return RemoveRepositoryResponse()

    def SetFullPath(self, request: SetFullPathRequest,
                    context) -> SetFullPathResponse:
        repo = self.load_repo(request.repository, context)

        if not request.path:
            context.abort(StatusCode.INVALID_ARGUMENT, "no path provided")

        set_gitlab_project_full_path(repo, request.path.encode('utf-8'))
        return SetFullPathResponse()

    def FullPath(self, request: FullPathRequest,
                 context) -> FullPathResponse:
        repo = self.load_repo(request.repository, context)

        path = get_gitlab_project_full_path(repo)
        if not path:  # None or (not probable) empty string
            # Gitaly simply returns the `git config` stderr output for now.
            # Pretty ridiculous to mimick it, we can hope not much to
            # depend on it.
            context.abort(StatusCode.INTERNAL, "Full path not set")
        return FullPathResponse(path=path)

    def CreateBundle(self, request: CreateBundleRequest,
                     context) -> CreateBundleResponse:
        repo = self.load_repo(request.repository, context).unfiltered()
        yield from self.gen_bundle_responses(CreateBundleResponse, repo,
                                             all=True)

    def gen_bundle_responses(self, response_class, repo, **bundle_opts):
        """Create bundle and generate gRPC responses"""
        # overrides makes sure that 1) phases info 2) obsmarkers are bundled
        overrides = {
            (b'experimental', b'bundle-phases'): True,
            (b'experimental', b'evolution.bundle-obsmarker'): True,
        }
        # also bundle the hidden changesets unless explicitely excluded
        bundle_opts.setdefault('hidden', True)
        with tempfile.NamedTemporaryFile(
                mode='wb+',
                buffering=WRITE_BUFFER_SIZE) as tmpf:
            with repo.ui.configoverride(overrides, b'CreateBundle'):
                bundle(repo.ui, repo, pycompat.sysbytes(tmpf.name),
                       **bundle_opts)
            tmpf.seek(0)
            while True:
                data = tmpf.read(WRITE_BUFFER_SIZE)
                if not data:
                    break
                yield response_class(data=data)

    def CreateBundleFromRefList(self, request: CreateBundleFromRefListRequest,
                                context) -> CreateBundleFromRefListResponse:
        # TODO Notes (probably for discussion only, before merging):
        # 1) Get it working for `git bundle create my.bundle master ^master~1`
        logger = LoggerAdapter(base_logger, context)
        first_req = next(request)
        repo_msg = first_req.repository
        if not (repo_msg.storage_name or repo_msg.relative_path):
            context.abort(StatusCode.INVALID_ARGUMENT, 'empty Repository')

        repo = self.load_repo(first_req.repository, context)
        patterns = itertools.chain(
            first_req.patterns,
            (pat for req in request for pat in req.patterns))

        incl_shas, excl_shas = resolve_revspecs_positive_negative(
            repo, patterns, ignore_unknown=True)
        logger.info("CreateBundleFromRefList repo=%r "
                    "included nodes=%r excluded nodes=%r",
                    message.Logging(first_req.repository),
                    incl_shas, excl_shas)

        # For info, in `hg bundle` one of the option from ('all', 'base')
        # is required, otherwise hg assumes that dest has all the nodes present
        incl_opts = {}
        if incl_shas is ALL_CHANGESETS:
            if not excl_shas:
                # underlying bundle command ignores --base if --all
                # is specified, but accepts --base without --rev, meaning
                # exactly what we need
                incl_opts['all'] = True
        else:
            incl_opts['rev'] = incl_shas

        if not excl_shas:
            excl_shas = [node.nullrev]

        yield from self.gen_bundle_responses(CreateBundleFromRefListResponse,
                                             repo.unfiltered(),
                                             base=excl_shas,
                                             **incl_opts)

    def FetchBundle(self, request: FetchBundleRequest,
                    context) -> FetchBundleResponse:
        logger = LoggerAdapter(base_logger, context)

        def load_or_init_repo(req, context):
            # TODO this should move to hgitaly.repository
            repo_path = self.repo_disk_path(req.repository, context)
            if os.path.lexists(repo_path):
                logger.info("FetchBundle: no need to create repo %r",
                            repo_path)
            else:
                self.hg_init_repository(req.repository, context)

            return self.load_repo(req.repository, context)

        try:
            with streaming_request_tempfile_extract(
                    request, context,
                    first_request_handler=load_or_init_repo
            ) as (repo, tmpf):
                unbundle(repo, tmpf.name)
        finally:
            return CreateRepositoryFromBundleResponse()

    def CreateRepositoryFromBundle(
            self, request: CreateRepositoryFromBundleRequest,
            context) -> CreateRepositoryFromBundleResponse:
        """Create repository from bundle.

        param `request`: is an iterator streaming sub-requests where first
        sub-request contains repository+data and subsequent sub-requests
        contains only data (i.e. the actual bundle sent in parts).
        """
        def init_repo(req, context):
            # TODO should move to hgitaly.repository
            self.hg_init_repository(req.repository, context)
            return self.load_repo(req.repository, context)

        with streaming_request_tempfile_extract(
                request, context,
                first_request_handler=init_repo
        ) as (repo, tmpf):
            try:
                unbundle(repo, tmpf.name)
            except Exception as exc:
                # same cleanup as Gitaly does, which gives later attempts
                # perhaps with a better bundle, chances to succeed.
                shutil.rmtree(repo.root)
                context.abort(StatusCode.INTERNAL,
                              "error in bundle application: %r" % exc)
        return CreateRepositoryFromBundleResponse()

    def hg_init_repository(self, repository: Repository, context):
        """Initialize a mercurial repository from a request object.

        :return: ``None``: the resulting repository has to be loaded in the
           standard way, using its path.
        :raises RepositoryCreationError: and updates context with error
           code and details.
        """
        logger = LoggerAdapter(base_logger, context)
        try:
            repo_path = self.repo_disk_path(repository, context)
        except KeyError:
            msg = "no such storage: %r" % repository.storage_name
            context.set_details(msg)
            logger.error(msg)
            context.set_code(StatusCode.INVALID_ARGUMENT)
            raise RepositoryCreationError(repository)

        if os.path.lexists(repo_path):
            msg = ("creating repository: repository exists already")
            context.set_details(msg)
            context.set_code(StatusCode.ALREADY_EXISTS)
            raise RepositoryCreationError(repository)

        try:
            logger.info("Creating repository at %r", repo_path)
            hg.peer(self.ui, opts={}, path=repo_path, create=True)
        except OSError as exc:
            context.set_code(StatusCode.INTERNAL)
            context.set_details("hg_init_repository(%r): %r" % (repo_path,
                                                                exc))
            raise RepositoryCreationError(repository)
