from dataclasses import dataclass
from enum import Enum
from typing import Union, List


class PolicyProvider(Enum):
    AZURE_POLICY = 1
    AWS_CONFIG_POLICY = 2
    KUBE_BENCH = 3
    OTHER = 4


class SourceProvider(Enum):
    AWS = 1
    AZURE = 2
    KUBERNETES = 3
    GCP = 4
    NIST = 5
    CSA = 6
    CIS = 7
    OTHER = 8


@dataclass
class Policy:
    """Class to represent a Policy and reference metadata"""
    name: str
    description: str
    provider: Union[PolicyProvider, SourceProvider]
    url: str

    def __json__(self):
        return {
            'name': self.name,
            'description': self.description,
            'provider': self.provider.name,
            'url': self.url
        }


@dataclass()
class Validation:
    """Class to represent Validation metadata."""
    name: str
    description: str
    implements: List[Policy]
    references: List[Policy]
    coverage: str

    def __json__(self):
        implements_json_list = []
        references_json_list = []

        if self.implements:
            for implement in self.implements:
                if implement:
                    implements_json_list.append(implement.__json__())

        if self.references:
            for reference in self.references:
                if reference:
                    references_json_list.append(reference.__json__())

        return {
            'name': self.name,
            'description': self.description,
            'implements': implements_json_list,
            'references': references_json_list,
            'coverage': self.coverage
        }
