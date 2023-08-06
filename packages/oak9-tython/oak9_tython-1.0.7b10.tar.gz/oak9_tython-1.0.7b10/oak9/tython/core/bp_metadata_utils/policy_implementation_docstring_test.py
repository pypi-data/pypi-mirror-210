import os
import unittest
from nose.tools import assert_equal
from parameterized import parameterized

from core.bp_metadata_utils.policy import Policy, PolicyProvider
from core.bp_metadata_utils.policy_implementation_docstring import PolicyImplementationDocstring

this_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(this_dir, 'testdata', 'oak9')


class TestPolicyImplementation(unittest.TestCase):
    @parameterized.expand([
        (
                'well_formed_implements_field_single_value_with_a_space_after_implements.py',
                [
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AZURE_POLICY,
                        url='https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Kubernetes/AKS_EncryptionAtHost_Deny.json',
                    ),
                ]
        ),
        (
                'well_formed_implements_field_single_value_with_a_space_after_implements.py',
                [
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AZURE_POLICY,
                        url='https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Kubernetes/AKS_EncryptionAtHost_Deny.json',
                    ),
                ]
        ),
        (
                'well_formed_aws_config_implementation.py',
                [
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AWS_CONFIG_POLICY,
                        url='https://github.com/awslabs/aws-config-rules/blob/master/python/API_GW_EXECUTION_LOGGING_ENABLED/API_GW_EXECUTION_LOGGING_ENABLED.py',
                    ),
                ]
        ),
        (
                'well_formed_implements_field_multiple_values.py',
                [


                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.AZURE_POLICY,
                        url='https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Kubernetes/AKS_EncryptionAtHost_Deny.json',
                    ),
                    Policy(
                        name='',
                        description='',
                        provider=PolicyProvider.KUBE_BENCH,
                        url='https://github.com/aquasecurity/blob/master/kube-bench/cfg/cis-1.6/master.yaml',
                    ),
                ]
        ),
        (
                'empty_implements_field.py',
                []
        ),
        (
                'no_implements_field.py',
                []
        ),
    ])
    def test_policy_implementations(self, source_file, want):
        with open(os.path.join(test_data_path, source_file)) as f:
            source = f.read()
            docstring = PolicyImplementationDocstring(source)

            assert_equal(list(docstring.implementations), want)
