from os import PathLike
from typing import Union
from git import Repo, exc


def sync_remote_repo_to_local(repo_url: Union[str, PathLike], local_path: Union[str, PathLike]) -> None:
    """
    When the supplied local_path is an empty directory, this function will clone the repo
    identified by the repo_url.
    When the local_path is a non-empty directory, the function attempts to pull the changes to
    the local repo.
    param repo_url: URL of the GitHub repository
    param local_path: Local path (must exist) where to clone or pull the code
    """
    try:
        repo = Repo(local_path)
        # TODO: If we accidentally modified vendor's repos, we would need to do a hard reset.
        # See https://stackoverflow.com/questions/1125968/how-do-i-force-git-pull-to-overwrite-local-files
        repo.remotes.origin.pull()
    except exc.InvalidGitRepositoryError:
        # Assuming that the program runs for the fist time - attempting to clone.
        Repo.clone_from(repo_url, local_path)
