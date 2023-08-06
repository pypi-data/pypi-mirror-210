import os
import unittest
from parameterized import parameterized

from core.bp_metadata_utils.policy import PolicyProvider
from core.bp_metadata_utils.customer_blueprint_repo import CustomerBlueprintRepo
from core.bp_metadata_utils.policy import Policy

this_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(this_dir, 'testdata', 'oak9')


class TestCustomerBlueprintRepo(unittest.TestCase):

    @parameterized.expand([
        (
                'sparce_implementation_class.py',
                [
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AZURE_POLICY,
                        url='https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Kubernetes/AKS_EncryptionAtHost_Deny.json'),
                ],
        ),
        (
                'well_formed_aws_config_implementation.py',
                [
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AWS_CONFIG_POLICY,
                        url='https://github.com/awslabs/aws-config-rules/blob/master/python/API_GW_EXECUTION_LOGGING_ENABLED/API_GW_EXECUTION_LOGGING_ENABLED.py'),
                ],
        ),
    ])
    def test_parse_implementations(self, policy_file, want):
        fixture = CustomerBlueprintRepo(token='foo', local_path="/", skip_sync=True)
        policy_path = os.path.join(test_data_path, policy_file)
        got = list(fixture.parse_policy_file(policy_path=policy_path))
        self.assertEqual(want, got)
