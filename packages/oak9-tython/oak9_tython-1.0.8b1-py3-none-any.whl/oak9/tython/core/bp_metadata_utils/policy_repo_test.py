import os
import unittest

from core.bp_metadata_utils.policy import Policy
from core.bp_metadata_utils.policy_repo import PolicyRepo

this_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(this_dir, 'testdata', 'oak9')


class TestRepo(PolicyRepo):
    def __init__(self, url: str, local_path: str, skip_sync: bool, glob_pattern: str):
        super().__init__(url=url, local_path=local_path, skip_sync=skip_sync)
        self._glob_pattern = glob_pattern

    @property
    def glob_pattern(self) -> str:
        return self._glob_pattern

    def filter(self, policy: Policy) -> bool:
        pass

    def pre_filter(self, policy_file_path: str) -> bool:
        pass


class PolicyRepoTest(unittest.TestCase):
    def test_path_expansion(self):
        glob_pattern = os.path.join(test_data_path, '{azure,aws}', '*.py')
        want = [
            os.path.join(test_data_path, 'azure/well_formed_implements_field_multiple_values.py'),
            os.path.join(test_data_path, 'aws/well_formed_aws_config_implementation.py'),
        ]
        fixture = TestRepo(url='foo', local_path=test_data_path, skip_sync=True, glob_pattern=glob_pattern)
        got = fixture.policy_file_paths
        self.assertEqual(got, want)
