from abc import abstractmethod
from typing import Iterator, Dict

from core.bp_metadata_utils.policy import Policy
from core.bp_metadata_utils.policy_repo import PolicyRepo


class MultiplePoliciesPerFileRepo(PolicyRepo):

    def __init__(self, url: str, local_path='', skip_sync=False) -> None:
        """
        Constructs a repo for PolicyPerFileRepo Policies.
        """
        super(MultiplePoliciesPerFileRepo, self).__init__(
            url=url,
            local_path=local_path,
            skip_sync=skip_sync,
        )

    @abstractmethod
    def parse_policy_file(self, policy_path: str) -> Iterator[Policy]:
        """
        This method is responsible for parsing the SaC policy and converting it into a Policy object.
        param policy_path: Path to the policy stored in a repo.
        """
        pass

    @property
    def policies(self) -> Dict[str, Policy]:
        """
        Iterate over the policies in a given repo and converts them to a Policy object.
        return: A list of policies
        """
        result = {}
        for policy_path in self.policy_file_paths:
            if self.pre_filter(policy_path):
                continue

            policies = self.parse_policy_file(policy_path)
            for policy in policies:
                if not self.filter(policy):
                    result[policy.url] = policy

        return result
