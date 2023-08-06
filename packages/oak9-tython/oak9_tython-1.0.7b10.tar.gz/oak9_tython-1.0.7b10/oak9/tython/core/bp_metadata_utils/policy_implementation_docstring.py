import re
from typing import Iterator
from core.bp_metadata_utils.policy import Policy, PolicyProvider, SourceProvider

# implements_pattern = re.compile('^\s+Implements:\s*[\r\n](?P<desc>[\S\s]+)Returns', re.MULTILINE)
# desc_pattern = re.compile('^\s+Desc:\s*[\r\n](?P<desc>[\S\s]+)Implements', re.MULTILINE)

implements_pattern = re.compile('(Implements:\n\s+((((?P<implements>.+(?:\n.*?|\Z)+(\s*)))(Coverage:|Partial:|Desc:|References:|Implements|Returns:|\Z))))', re.MULTILINE)
desc_pattern = re.compile('Desc:\n\s+((((?P<desc>.+(?:\n.*?|\Z)+(\s*)))(Coverage:|Partial:|Desc:|References:|Implements|Returns:|\Z)))', re.MULTILINE)
no_desc_pattern = re.compile('(((((?P<nodesc>.+(?:\n.*?|\Z)+(\s*)))(Name:|Author:|\Z))))', re.MULTILINE)
coverage_pattern = re.compile('Coverage:\n\s+((?P<coverage>.+(?:\n.*?|\Z)+(\s*))(Coverage:|Partial:|Desc:|References:|Implements|Returns:|\Z))', re.MULTILINE)
references_pattern = re.compile('References:\n\s+(((?P<references>.+(?:\n.*?|\Z)+(\s*))(Coverage:|Partial:|Desc:|References:|Implements|Returns:|\Z)))', re.MULTILINE)
partial_pattern = re.compile('(Partial:\n\s+((((?P<partial>.+(?:\n.*?|\Z)+(\s*)))(Coverage:|Partial:|Desc:|References:|Implements|Returns:|\Z))))', re.MULTILINE)


class PolicyImplementationDocstring:
    """Representation of a docstring that links a use-case implementation to a vendor's policy/standard.

    References:
        AWS: https://aws.com

    Implements:
        AZURE_POLICY: https://github.com/Azure/azure-policy/blob/master/built-in-policies/policyDefinitions/Kubernetes/AKS_EncryptionAtHost_Deny.json
        AQUA_SECURITY_KUBE_BENCH: https://github.com/aquasecurity/kube-bench/cfg/cis-1.6/master.yaml
    Coverage:
        Partial:
            TODO (atcherniakhovski): Validate that this handles the case of multiple node-pools.
    """
    def __init__(self, docstring_raw: str) -> None:
        self._docstring_raw = docstring_raw


    @property
    def implementations(self) -> Iterator[Policy]:
        """
        Returns Policies that were implemented by the method to which the docstring is attached, an empty list otherwise.
        """
        matches = re.search(implements_pattern, self._docstring_raw)
        if not matches:
            return []

        for implementation in matches.group('implements').strip().split('\n'):
            # TODO: Refactor this to a regex and throw exceptions when the expected patter is not found.
            provider = implementation.split(':', 1)[0].strip()
            try:
                policy_provider = PolicyProvider[provider]
            except KeyError:
                policy_provider = PolicyProvider['OTHER']

            url = implementation.split(':', 1)[1].strip()

            # TODO: We only need the url to match this to a policy, but (for debugging purposes)
            # construct the name and description parameters. Consider, getting them from the docstring of the
            # implementing method.
            yield Policy(name='', description='', provider=policy_provider, url=url)

    @property
    def desc(self) -> str:
        """
        Returns blueprint name
        """
        empty_msg = "No description provided in docstring"
        desc = self._get_str_field(desc_pattern, 'desc', empty_msg)
        if desc == empty_msg:
            desc = self._get_str_field(no_desc_pattern, 'nodesc', empty_msg)

        return desc

    @property
    def coverage(self) -> str:
        """
        Returns blueprint name
        """
        empty_msg = "No coverage information provided in docstring"
        coverage = self._get_str_field(coverage_pattern, 'coverage', empty_msg)
        return coverage

    @property
    def references(self) -> Iterator[Policy]:
        """
        Returns blueprint name
        """
        matches = re.search(references_pattern, self._docstring_raw)
        if not matches:
            return []

        for reference in matches.group('references').strip().split('\n'):
            # TODO: Refactor this to a regex and throw exceptions when the expected patter is not found.
            source = reference.split(':', 1)[0].strip()
            try:
                policy_provider = SourceProvider[source]
            except KeyError:
                policy_provider = SourceProvider.OTHER

            url = reference.split(':', 1)[1].strip()

            # TODO: We only need the url to match this to a policy, but (for debugging purposes)
            # construct the name and description parameters. Consider, getting them from the docstring of the
            # implementing method.
            yield Policy(name='', description='', provider=policy_provider, url=url)

    def _get_str_field(self, pattern: re, group: str, empty_msg: str) -> str:
        """
        Returns string value for simple fields defined in the blueprint or function docstring
        """
        matches = re.search(pattern, self._docstring_raw)
        if not matches:
            return empty_msg

        # Assume first item is what we want
        result = matches.group(group).strip().split('\n')[0]

        return result
