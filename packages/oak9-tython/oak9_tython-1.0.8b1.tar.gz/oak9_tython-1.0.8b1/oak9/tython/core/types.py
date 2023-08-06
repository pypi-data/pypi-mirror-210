import uuid
from models.shared.shared_pb2 import Blueprint as BP
from models.shared.shared_pb2 import Graph
from models.shared.shared_pb2 import Context as Ctx
from core.sdk.resource_map import grpc_type_map
from dataclasses import dataclass, field
from enum import Enum
from typing import List, ClassVar, Callable, Union, Set, Any
from core.bp_metadata_utils.blueprint_meta_data import BlueprintMetaData

ValidationFunction = Callable[[any], any]


class OrderedEnum(Enum):

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Csp(Enum):
    Aws = 1
    Azure = 2


class DataSensitivity(OrderedEnum):
    Sensitive = 2
    NonSensitive = 1


class BusinessImpact(OrderedEnum):
    High = 3
    Medium = 2
    Low = 1


class DeploymentModel(OrderedEnum):
    Private = 3
    Hybrid = 2
    Public = 1


@dataclass
class ResourceMetadata:
    resource_id: str
    resource_name: str
    resource_type: str
    
    def __json__(self):
        return {
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type
        }

class Context:

    def __init__(self, context: Ctx = None):
        """
        Business context of the architecture being secured 
                  
        Args:
            context (context_pb2): The proto context object is passed in and converted into a python object
        """

        #  Default context
        if not context:
            self.business_impact: BusinessImpact = BusinessImpact.High
            self.data_sensitivity: DataSensitivity = DataSensitivity.Sensitive
            self.deployment_model: DeploymentModel = DeploymentModel.Public
            self.internal_access = True
            self.external_access = False
            self.remote_access = False
            self.wireless_access = False
            self.outbound_access = False
            self.workforce = True
            self.consumers = True
            self.business_partners = True
            self.physical = False
            self.open = False
            self.limited_sensitive_data = False
            self.broad_sensitive_data = True
            self.security_privileged = True
            self.component_core = True
            self.user_interface = True
            self.management_interface = True
            return

    def is_externally_accessible(self):
        if self.external_access and not self.internal_access:
            return True

        return False

    def is_data_sensitive(self):
        if self.data_sensitivity == DataSensitivity.Sensitive:
            return True
        return False

    def is_impact_high(self):

        if self.business_impact == BusinessImpact.High:
            return True

        return False

    def is_impact_moderate(self):

        if self.business_impact == BusinessImpact.Medium:
            return True

        return False

    def is_impact_low(self):

        if self.business_impact == BusinessImpact.Low:
            return True

        return False

    def is_business_critical(self):

        if self.business_impact == BusinessImpact.High and self.data_sensitivity == DataSensitivity.Sensitive:
            return True
        else:
            return False

    def is_impact_high_or_data_sensitive(self):

        if self.business_impact == BusinessImpact.High or self.data_sensitivity == DataSensitivity.Sensitive:
            return True
        else:
            return False

    def is_sensitive(self):
        if self.data_sensitivity == DataSensitivity.Sensitive:
            return True
        else:
            return False

    def is_sensitive_and_external(self):

        if self.data_sensitivity == DataSensitivity.Sensitive and self.external_access:
            return True
        else:
            return False

    def is_sensitive_and_internal(self):
        if self.data_sensitivity == DataSensitivity.Sensitive and self.internal_access:
            return True
        else:
            return False

    def determine_severity(self):

        if self.business_impact == BusinessImpact.High:
            config_violation_severity = Severity.High

        elif self.business_impact == BusinessImpact.Medium:
            config_violation_severity = Severity.Moderate

        else:
            config_violation_severity = Severity.Low

        return config_violation_severity


Default_Context = Context()


class BlueprintType(Enum):
    Component = 1
    Reference = 2
    Solution = 3
    Resource = 4
    Customer = 5


@dataclass
class Resource:
    id: str
    name: str
    csp: Csp
    resource_type: ClassVar[str]
    id: str
    name: str
    blueprint_id: str


class WellDoneRating(OrderedEnum):
    Amazing = 4
    Great = 3
    Good = 2
    Ok = 1


class Severity(OrderedEnum):
    Critical = 4
    High = 3
    Moderate = 2
    Low = 1


class RelatedConfig:
    """
    Related Configs allows the Violation to bundle additional configurations that don't need a separate violation
    and should be remediated together
    """
    config_id: str = ""
    config_value: Union[List, int, str] = ""
    preferred_value: Union[List, int, str] = ""
    comment: str = ""


class Violation:
    """
    Defines a violation object.
    This object is DEPRECATED and is only there for backwards compatibility
    Note that there are required and optional fields
    """

    def __init__(
            self,
            severity: Severity = Severity.Low,
            adjusted_severity: Severity = None,
            config_id: str = "",
            config_value: str = "",
            config_gap: str = "",
            config_impact: str = "",
            config_fix: str = "",
            preferred_value: Union[List, str, int] = "",
            additional_guidance: str = "",
            documentation: str = "",
            related_configs: List[RelatedConfig] = None,
            capability_id: str = "",
            capability_name: str = "",
            resource_id: str = "",
            resource_type: str = "",
            resource_name: str = "",
            priority: int = 0
    ):

        # Severity of the violation.  Default to low. Severity should be determined based on the business context
        self._severity = severity

        # Adjusted severity of the violation. This field is used to adjust the severity for a mitigating design
        self._adjusted_severity = adjusted_severity

        # the unique id (full path) of the configuration that has the issue
        self.config_id = config_id

        # currently configured value of this configuration
        if type(config_value) != str:
            self.config_value = str(config_value)

        else:
            self.config_value = config_value

        # Description of the gap 
        self.config_gap = config_gap

        # Impact of not fixing this violation
        self.config_impact = config_impact

        # Guidance on how to fix the issue
        self.config_fix = config_fix

        # The preferred value
        # Preferred values can be strings, integers, bools, lists, dictionaries
        if type(preferred_value) == list:
            self.preferred_value = ', '.join(preferred_value)

        elif type(preferred_value) != str:
            self.preferred_value = str(preferred_value)

        else:
            self.preferred_value = preferred_value

        # Additional guidance 
        self.additional_guidance = additional_guidance

        # Related configurations that should be remediated together 
        self.related_configs: List[RelatedConfig] = related_configs

        # oak9 security capability requirement id
        self._capability_id = capability_id

        # oak9 detailed requirement name
        self._capability_name = capability_name

        # documentation link
        self._documentation = documentation

        # Unique id of the resource
        self._resource_id = resource_id

        # Type of resource
        self._resource_type = resource_type

        # resource name
        self._resource_name = resource_name

        # Priority of finding (1-100)
        # This helps relatively prioritize across qualitative ratings
        self._priority = priority

    def __json__(self):
        return {
            'severity': self.severity.name,
            'configGap': self.config_gap,
            'capabilityId': self.capability_id,
            'configId': self.config_id,
            'configValue': self.config_value,
            'oak9Guidance': self.additional_guidance,
            'prefferedValue': self.preferred_value,
            'capabilityName': self.capability_name,
            'configFix': self.config_fix,
            'configImpact': self.config_impact,
            'resourceId': self.resource_id,
            'resourceType': self.resource_type,
            'resourceName': self.resource_name
        }

    @property
    def severity(self) -> Severity:
        return self._severity

    @severity.setter
    def severity(self, value):
        if self._adjusted_severity:
            self._severity = self._adjusted_severity
        else:
            self._severity = value

    @property
    def adjusted_severity(self):
        return self._adjusted_severity

    @adjusted_severity.setter
    def adjusted_severity(self, value):
        self._adjusted_severity = value

    @property
    def documentation(self):
        return self._documentation

    @property
    def capability_id(self):
        return self._capability_id

    @capability_id.setter
    def capability_id(self, value):
        self._capability_id = value

    @property
    def capability_name(self):
        return self._capability_name

    @capability_name.setter
    def capability_name(self, value):
        self._capability_name = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if isinstance(value, int) and 101 > value > 0:
            self._priority = value

    @property
    def resource_id(self):
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value):
        self._resource_id = value

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value):
        self._resource_type = value

    @property
    def resource_name(self):
        return self._resource_name
    
    @resource_name.setter
    def resource_name(self, value):
        self._resource_name = value

@dataclass
class DesignGap:
    """
    Defines the design gap object, which is a collection of violations
    This object is DEPRECATED and is only there for backwards compatibility
    Note that there are required and optional fields
    """
    # What is the  gap
    capability_gap: str = ""

    # What is the impact
    capability_impact: str = ""

    # severity of the design gap
    _severity: Severity = Severity.Low

    # List of violations
    violations: List[Violation] = field(default_factory=list)

    def add_violation(self, violations: List[Violation]):
        self.violations.extend(violations)
        self._update_severity()

    def _update_severity(self):
        for viol in self.violations:
            if viol.severity > self._severity:
                self._severity = viol.severity


class FindingType(Enum):
    DesignGap = 1
    Kudos = 2
    Warning = 3
    Task = 4
    ResourceGap = 5


class Finding:
    """
    Defines a Finding object.
    """

    def __init__(
            self,
            resource: Any,
            resource_metadata: ResourceMetadata,
            finding_type: FindingType,
            desc: str,
            rating: Union[Severity, WellDoneRating] = Severity.Low,
            adjusted_severity: Severity = None,
            config_id: str = "",
            current_value: Any = "",
            fix: str = "",
            preferred_value="",
            additional_guidance: str = "",
            related_configs: List[RelatedConfig] = None,
            related_findings: List[uuid.UUID] = None,
            req_id: str = "",
            req_name: str = "",
            priority: int = 0,
            documentation_url="",
            cost_consideration: bool = False,
            env: str = ""
    ):
        """
        Type of observation
        """

        self._id = uuid.uuid4()

        """
        Subresource of the object being validated
        """
        if hasattr(resource, "resource_info"):
            self._resource: Any = resource 
        else:
            raise TypeError("Cannot create Finding object, the resource attribute must be a subresource of the object being validated.")

        """
        Metadata of the resource that this finding relates to
        """
        self._resource_metadata: ResourceMetadata = resource_metadata

        """
        Findings can be of type Design Gap, Resource Gap, Kudos, Task or Warning
        """
        self._finding_type: FindingType = finding_type

        """
        For Design Gaps and Tasks: 
            Severity of the gap or task.  Default to low. 
            Severity should be determined based on the business context
            Resource blueprints can also specify adjusted severity. When an adjusted severity is specified, it does
            not allow the Component blueprint to set the severity for this violation.
        
        For Kudos: 
            Well done rating. Should be determined based on the business context
        
        For Warnings: N/A
        """
        self._rating = rating

        """
        Currently N/A to Tython
        This field is meant to provide an adjusted severity rating for mitigating designs
        """
        self._adjusted_severity = adjusted_severity

        """
        the unique id (full path) of the configuration that we want to call out
        e.g. LoadBalancer.listeners[0].listenerCertificates[2].certificate[1].name
        This field should be auto-populated using a utility function (get_config_id)
        """

        self._config_id = config_id

        # currently configured value of this configuration
        if type(current_value) != str:
            self._current_value = str(current_value)
        else:
            self._current_value = current_value

        """
        For design gaps - Description of the gap, framed neutrally as a recommendation.
            Guidance on language - This field should be framed in a neutral way (as opposed to a negative framing).
            This field should focus on explicitly defining "What is the recommendation" and implicitly defining "What is the gap"
            The Fix field will define the How do I fix it

            Examples:
            
                Instead of "Encryption is not configured" we focus on the recommendation "Enable Encryption"
            
                For lists: instead of "[configId] contains insecure origin values" say 
                "Remove origins from CORS rules that allow broad access"
            
                Instead of "SSL Protocol is not set to TLS.v1.2" we should say "SSL protocol should use latest protocol version"
                
                Instead of "Encryption is not enabled" we should say "Enable encryption"

        For Kudos - Description of the passed check
        
        For Tasks - Description of the task
        
        For Warnings - Description of the warnings
        """

        self._desc = desc

        # Specific details on the gap (for cases where the gap gets displayed separately)
        self._fix = fix

        # oak9's preferred value
        # preferred values can be strings, integers, bools, lists, dictionaries
        # the platform is responsible for checking type to use-cases like remediation
        # or displaying design gaps
        # (Required for remediation)
        if type(preferred_value) == list:
            self._preferred_value = ', '.join(preferred_value)

        elif type(preferred_value) != str:
            self._preferred_value = str(preferred_value)

        else:
            self._preferred_value = preferred_value

        # Additional guidance
        self._additional_guidance = additional_guidance

        # Related configurations that should be remediated together or
        # are better presented bundled together
        self._related_configs: List[RelatedConfig] = related_configs or []

        # add documentation link
        # Currently this is auto-populated on the platform side
        self._documentation_url = documentation_url

        # Requirement id
        # Could be oak9 or customer provided requirement id
        self._req_id = req_id

        # oak9 detailed requirement name
        # This is automatically populated on the platform side
        self._req_name = req_name

        # Priority of finding to relatively prioritize across
        # qualitative ratings.  Can be any number from 0-100
        self._priority = priority

        # Related findings
        # List of UUIDs for related findings
        self._related_findings = related_findings or []

        # Note if the finding will lead to higher costs for the customers if they follow our guidance
        self._cost_consideration = cost_consideration

        # environment as defined by customer
        self._env = env

    @property
    def id(self):
        return self._id

    @property
    def resource(self):
        return self._resource

    @property
    def resource_metadata(self):
        return self._resource_metadata

    @property
    def finding_type(self):
        return self._finding_type

    @finding_type.setter
    def finding_type(self, value):
        self._finding_type = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    @property
    def config_id(self):
        return self._config_id

    @config_id.setter
    def config_id(self, value):
        self._config_id = value

    @property
    def current_value(self):
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        self._current_value = value

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def fix(self):
        return self._fix

    @fix.setter
    def fix(self, value):
        self._fix = value

    @property
    def preferred_value(self):
        return self._preferred_value

    @preferred_value.setter
    def preferred_value(self, value):
        if type(value) == list:
            self._preferred_value = ', '.join(value)
        elif type(value) != str:
            self._preferred_value = str(value)
        else:
            self._preferred_value = value

    @property
    def additional_guidance(self):
        return self._additional_guidance

    @additional_guidance.setter
    def additional_guidance(self, value):
        self._additional_guidance = value

    @property
    def severity(self) -> Severity:
        return self._rating

    @severity.setter
    def severity(self, value):
        if self._adjusted_severity:
            self._rating = self._adjusted_severity
        else:
            self._rating = value

    @property
    def adjusted_severity(self):
        return self._adjusted_severity

    @adjusted_severity.setter
    def adjusted_severity(self, value):
        self._adjusted_severity = value

    @property
    def capability_id(self):
        return self._req_id

    @capability_id.setter
    def capability_id(self, value):
        self._req_id = value

    @property
    def capability_name(self):
        return self._req_name

    @capability_name.setter
    def capability_name(self, value):
        self._req_name = value

    @property
    def req_id(self):
        return self._req_id

    @req_id.setter
    def req_id(self, value):
        # TODO: add checks for user provided ids vs oak9 ids
        self._req_id = value

    @property
    def req_name(self):
        return self._req_name

    @req_name.setter
    def req_name(self, value):
        # TODO: add checks for user provided reqs vs oak9 reqs
        self._req_name = value

    @property
    def related_configs(self):
        return self._related_configs

    def add_related_config(self, related_config: RelatedConfig):
        self._related_configs.append(related_config)

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def env(self) -> str:
        return self._env

    @env.setter
    def env(self, value: str):
        self._env = value

    @priority.setter
    def priority(self, value: int):
        if isinstance(value, int):
            if self.severity == Severity.Critical:
                self._priority = value if value > 75 else 75
            elif self.severity == Severity.High:
                self._priority = value if (50 < value < 74) else 74 if value > 50 else 50
            elif self.severity == Severity.Moderate:
                self._priority = value if (25 < value < 49) else 49 if value > 25 else 25
            elif self.severity == Severity.Low:
                self._priority = value if (0 < value < 24) else 24 if value > 0 else 0

    @property
    def related_findings(self):
        return self._related_findings

    @property
    def documentation_url(self):
        return self._documentation_url

    @documentation_url.setter
    def documentation_url(self, value):
        self._documentation_url = value

    @property
    def cost_consideration(self) -> bool:
        return self._cost_consideration

    @cost_consideration.setter
    def cost_consideration(self, value: bool):
        self._cost_consideration = value

    def add_related_findings(self, related_findings: Union[uuid.UUID, List]):
        if isinstance(related_findings, uuid.UUID):
            self._related_findings.append(related_findings)
        elif isinstance(related_findings, list):
            for finding in related_findings:
                if isinstance(related_findings, uuid.UUID):
                    self._related_findings.append(finding)

    @classmethod
    def from_violation(cls, viol: Violation):
        self = cls.__new__(cls)
        self._finding_type = FindingType.DesignGap
        self._desc = viol.config_gap
        self._rating = viol.severity
        self._adjusted_severity = viol.adjusted_severity
        self._config_id = viol.config_id
        self._current_value = viol.config_value
        self._desc = viol.config_fix
        self._preferred_value = viol.preferred_value
        self._additional_guidance = viol.additional_guidance
        self._documentation_url = viol.documentation
        self._related_configs = viol.related_configs or []
        self._req_id = viol.capability_id
        self._req_name = viol.capability_name
        self.priority = viol.priority
        return self

    def to_violation(self):
        viol = Violation()
        if self.finding_type not in [FindingType.DesignGap, FindingType.ResourceGap]:
            return None

        viol.config_gap = self.desc
        viol.severity = self.rating
        viol.adjusted_severity = self.adjusted_severity
        viol.config_id = self.config_id
        viol.config_value = self.current_value
        viol.config_fix = self.fix
        viol.preferred_value = self.preferred_value
        viol.additional_guidance = self.additional_guidance
        viol._documentation = self.documentation_url
        viol.related_configs = self.related_configs
        viol.capability_id = self.req_id
        viol.capability_name = self.req_name
        viol.priority = self.priority
        viol.resource_id = "" if not self.resource else self.resource.resource_info.id
        viol.resource_type = "" if not self.resource else self.resource.resource_info.resource_type
        viol.resource_name = "" if not self.resource else self.resource.resource_info.name
        
        return viol

    def __json__(self):
        resource_metadata_json = {}
        if self.resource_metadata:
            resource_metadata_json = self.resource_metadata.__json__()
        else:
            resource_metadata_json = ResourceMetadata("", "", "").__json__()

        return {
            "resource_metadata": resource_metadata_json,
            "finding_type": self.finding_type.name,
            "desc": self.desc,
            "rating": self.rating.name,
            "adjusted_severity": "" if not self.adjusted_severity else self.adjusted_severity,
            "config_id": self.config_id,
            "current_value": self.current_value,
            "fix": self.fix,
            "preferred_value": self.preferred_value,
            "additional_guidance": self.additional_guidance,
            "related_configs": self.related_configs,
            "related_findings": self.related_findings,
            "req_id": self.req_id,
            "req_name": self.req_name,
            "priority": self.priority,
            "documentation_url": self.documentation_url,
            "resource_id" : "" if not self.resource else self.resource.resource_info.id,
            "resource_type" : "" if not self.resource else self.resource.resource_info.resource_type,
            "resource_name" : "" if not self.resource else self.resource.resource_info.name
        }

    def __str__(self):
        ret_str = ''
        ret_str += f"Finding Type: {self.finding_type}\n"
        if self.finding_type in [FindingType.DesignGap, FindingType.ResourceGap, FindingType.Task]:
            ret_str += f"Severity: {self.severity}\n"
            ret_str += f"Action Required: {self.desc}\n"
            ret_str += f"Fix: {self.fix}\n" if self.fix else ''
        elif self.finding_type == FindingType.Kudos:
            ret_str += f"Rating: {self.rating}\n"
            ret_str += f"Description: {self.desc}\n"
        elif self.finding_type == Warning:
            ret_str += f"Description: {self.desc}\n"
        return ret_str


@dataclass
class ValidationMetaInfo:
    caller: str
    request_id: str
    resource_type: str
    blueprint_id: str
    resource_name: str
    resource_id: str


class DesignPref:
    pass


class Blueprint:
    """
    Base class for Tython Blueprints
    """
    display_name: ClassVar[str] = None
    blueprint_type: ClassVar[BlueprintType] = BlueprintType.Customer
    id: ClassVar[str] = None
    parent_blueprint_id: ClassVar[str] = None
    version: ClassVar[str] = None

    def __init__(self, graph: Graph, context: Context = None) -> None:
        self._graph = graph
        self._context = context
        self._meta_info = None

    @property
    def context(self):
        return self._context

    @property
    def meta_info(self):
        return self._meta_info

    @meta_info.setter
    def meta_info(self, value):
        pass

    @property
    def graph(self):
        return self._graph

    def validate(self) -> Set[Finding]:
        pass

    def find_by_resource(self, resource_type):
        """
        Filters the graph for the given resource_type
        """
        resources = []

        for input in self._graph:
            for root_node in input.graph.root_nodes:
                mapped = grpc_type_map.get(root_node.node.resource.data.type_url)
                if mapped == resource_type:
                    resource = resource_type()
                    root_node.node.resource.data.Unpack(resource)

                    resource_metadata = ResourceMetadata(
                        resource_id=input.meta_info.resource_id,
                        resource_name=input.meta_info.resource_name,
                        resource_type=input.meta_info.resource_type
                    )

                    resources.append((resource, resource_metadata))

        return resources


@dataclass
class Configuration:
    api_key: str = None
    org_id: str = None
    project_id: str = None
    blueprint_package_path: str = None
    data_endpoint: str = None
    mode: str = None

    def __init__(self, api_key: str, org_id: str, project_id: str, blueprint_package_path: str,
                 data_endpoint: str = None, mode: str = None, **kwargs):
        self.api_key = api_key
        self.org_id = org_id
        self.project_id = project_id
        self.blueprint_package_path = blueprint_package_path
        self.data_endpoint = "https://api.oak9.io/console/" if not data_endpoint else data_endpoint
        self.mode = "test" if not mode else mode
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class RunnerReport:
    blueprint_metadata: List[BlueprintMetaData]
    blueprint_output: List[str]
    blueprint_problems: List[str]
    findings: List[Finding]
