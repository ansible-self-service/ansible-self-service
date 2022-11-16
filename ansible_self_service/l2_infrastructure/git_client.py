import shutil
from pathlib import Path
from typing import List, Optional

from git import Repo, InvalidGitRepositoryError  # type: ignore

from ansible_self_service.l4_core.protocols import GitClientProtocol


class GitPythonGitClient(GitClientProtocol):
    """Implementation of GitClientProtocol via GitPython.

    See: https://gitpython.readthedocs.io
    """

    def get_origin_url(self, directory: Path) -> str:
        return str(list(Repo(directory).remote().urls)[0])

    def get_revision(self, directory: Path) -> str:
        return str(Repo(directory).head.commit)

    def clone_repo(self, url: str, target_dir: Path):
        Repo.clone_from(url=url, to_path=target_dir)

    def remove_repo(self, directory: Path):
        shutil.rmtree(directory)

    def list_revisions(self, directory: Path) -> List:
        raise NotImplementedError()

    def update(self, directory: Path, revision: Optional[str] = None):
        repo = Repo(directory)
        repo.remote().fetch()
        if revision:
            repo.git.checkout(revision, force=True)
        else:
            if "master" in repo.remote().refs:
                branch = "master"
            elif "main" in repo.remote().refs:
                branch = "main"
            else:
                raise Exception('Either "master" or "main" branch must exist in origin')
            if repo.head.is_detached:
                if branch in repo.refs:  # type: ignore
                    repo.git.checkout(branch)
                else:
                    repo.git.checkout("-b", branch)
            if not repo.head.ref.tracking_branch():
                repo.head.ref.set_tracking_branch(repo.remote().refs[branch])
            repo.remote().pull(force=True)

    def is_git_directory(self, directory: Path) -> bool:
        try:
            Repo(directory)
        except InvalidGitRepositoryError:
            return False
        return True
