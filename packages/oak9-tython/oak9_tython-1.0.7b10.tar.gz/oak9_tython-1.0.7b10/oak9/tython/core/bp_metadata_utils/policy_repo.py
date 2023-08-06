from abc import ABC, abstractmethod
from glob import glob
import tempfile
import atexit
from typing import Iterator, AnyStr

from core.bp_metadata_utils.git_utils import sync_remote_repo_to_local
from core.bp_metadata_utils.policy import Policy


class PolicyRepo(ABC):
    """Class to hold the common functionality for policy repositories."""

    def __init__(self, url: str, local_path='', skip_sync=False) -> None:
        """
        Constructs a base class for the specialized repositories of policies.
        param url: Url to clone/pull policies from.
        param local_path: Path to where the repo should be cloned. If not supplied a temp directory will be created.
        param skip_sync: When set to True, the initialization of the repo will be skipped - use for testing purposes
        only (to speed-up tests).
        """
        self._url = url
        self._base_url = self._url.rstrip('.git')
        self._local_path = local_path

        if not self._local_path:
            self._working_dir = tempfile.TemporaryDirectory(prefix='repo-policies-')
            self._local_path = self._working_dir.name
            atexit.register(self._working_dir.cleanup)

        if not skip_sync:
            sync_remote_repo_to_local(repo_url=url, local_path=self._local_path)

    @property
    @abstractmethod
    def glob_pattern(self) -> str:
        """
        It is the responsibility of the specialized repositories to provide the
        pattern where the policies are stored - typically only a small section of the
        repo contains the policies. Hence, the need for a search pattern.
        """
        pass

    @abstractmethod
    def filter(self, policy: Policy) -> bool:
        """
        Determines whether a supplied policy has to be filtered-out.
        Some policies are not interesting to us (ex., Azure internal policies which customers
        have no control over). Hence, this function is used to allow the specialized repositories
        to indicate which policies should be ignored.
        param policy: Policy to examine.
        """
        pass

    @abstractmethod
    def pre_filter(self, policy_file_path: str) -> bool:
        """
        Determines whether a supplied policy file has to be filtered-out.
        Unlike the filter method, this method makes the decision solely based on the name of the file.
        param policy_file_path: Policy's file to examine.
        """
        pass

    @property
    def policy_file_paths(self) -> Iterator[AnyStr]:
        expanded_paths = []
        # for p in braceexpand(self.glob_pattern):
        # This was preventing the blueprint execution, is there a reason for this library?
        # Library removed 
        # expanded_paths.extend(glob(p, recursive=True))
        expanded_paths.extend(glob(self.glob_pattern, recursive=True))

        return expanded_paths

    def __str__(self):
        return f'URL {self._url},' \
               f' local_path: {self._local_path}, ' \
               f'glob_pattern: {self.glob_pattern}, ' \
               f'policy_file_paths: {list(self.policy_file_paths)}'
