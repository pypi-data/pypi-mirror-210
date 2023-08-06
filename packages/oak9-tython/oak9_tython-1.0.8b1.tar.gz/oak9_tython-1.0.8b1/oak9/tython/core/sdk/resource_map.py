from typing import Dict, Type
from google.protobuf.reflection import GeneratedProtocolMessageType

from models.azure.azure_microsoft_recoveryservices_backup_pb2 import Microsoft_RecoveryServices_Backup
from models.azure.azure_microsoft_network_privateendpoints_pb2 import Microsoft_Network_privateEndpoints
from models.azure.azure_microsoft_compute_pb2 import Microsoft_Compute
from models.azure.azure_microsoft_compute_virtualmachines_pb2 import Microsoft_Compute_VirtualMachines
from models.azure.azure_microsoft_compute_virtualmachinescalesets_pb2 import Microsoft_Compute_VirtualMachineScaleSets
from models.azure.azure_microsoft_recoveryservices_pb2 import Microsoft_RecoveryServices
from models.azure.azure_microsoft_servicebus_pb2 import Microsoft_ServiceBus
from models.azure.azure_microsoft_cdn_pb2 import Microsoft_Cdn
from models.azure.azure_microsoft_network_privatelinkservices_pb2 import Microsoft_Network_privateLinkServices
from models.azure.azure_microsoft_devices_pb2 import Microsoft_Devices
from models.azure.azure_microsoft_keyvault_pb2 import Microsoft_KeyVault
from models.azure.azure_microsoft_containerservice_pb2 import Microsoft_ContainerService
from models.azure.azure_microsoft_network_virtualnetworks_pb2 import Microsoft_Network_virtualNetworks
from models.azure.azure_microsoft_network_dnszones_pb2 import Microsoft_Network_dnsZones
from models.azure.azure_microsoft_apimanagement_pb2 import Microsoft_ApiManagement
from models.azure.azure_microsoft_web_pb2 import Microsoft_Web
from models.azure.azure_microsoft_sql_servers_pb2 import Microsoft_Sql_Servers
from models.azure.azure_microsoft_sql_databases_pb2 import Microsoft_Sql_Databases
from models.azure.azure_microsoft_sql_managedinstances_pb2 import Microsoft_Sql_ManagedInstances
from models.azure.azure_microsoft_network_routetables_pb2 import Microsoft_Network_routeTables
from models.azure.azure_microsoft_aad_pb2 import Microsoft_AAD
from models.azure.azure_microsoft_containerregistry_pb2 import Microsoft_ContainerRegistry
from models.azure.azure_microsoft_sql_pb2 import Microsoft_Sql
from models.azure.azure_microsoft_iotsecurity_pb2 import Microsoft_IoTSecurity
from models.azure.azure_microsoft_network_loadbalancers_pb2 import Microsoft_Network_loadBalancers
from models.azure.azure_microsoft_network_privatednszones_pb2 import Microsoft_Network_privateDnsZones
from models.azure.azure_microsoft_network_applicationgateways_pb2 import Microsoft_Network_applicationGateways
from models.azure.azure_microsoft_network_trafficmanager_pb2 import Microsoft_Network_TrafficManager
from models.azure.azure_microsoft_healthcareapis_pb2 import Microsoft_HealthcareApis
from models.azure.azure_microsoft_iotcentral_pb2 import Microsoft_IotCentral
from models.azure.azure_microsoft_network_frontdoor_pb2 import Microsoft_Network_FrontDoor
from models.azure.azure_microsoft_elastic_pb2 import Microsoft_Elastic
from models.azure.azure_microsoft_storage_pb2 import Microsoft_Storage
from models.azure.azure_microsoft_network_frontdoor_networkexperimentprofiles_pb2 import \
    Microsoft_Network_FrontDoor_NetworkExperimentProfiles
from models.azure.azure_microsoft_cache_pb2 import Microsoft_Cache
from models.azure.azure_microsoft_network_pb2 import Microsoft_Network
from models.azure.azure_microsoft_documentdb_pb2 import Microsoft_DocumentDB
from models.azure.azure_microsoft_streamanalytics_pb2 import Microsoft_StreamAnalytics
from models.azure.azure_microsoft_kubernetes_pb2 import Microsoft_Kubernetes
from models.azure.azure_microsoft_recoveryservices_siterecovery_pb2 import Microsoft_RecoveryServices_SiteRecovery
from models.azure.azure_microsoft_network_networksecuritygroups_pb2 import Microsoft_Network_networkSecurityGroups
from models.azure.azure_microsoft_eventgrid_pb2 import Microsoft_EventGrid
from models.azure.azure_microsoft_network_firewallpolicies_pb2 import Microsoft_Network_firewallPolicies
from models.azure.azure_microsoft_app_containerapps_pb2 import Microsoft_App_containerApps
from models.aws.aws_ec2_vpcendpoint_pb2 import EC2_VPCEndpoint
from models.aws.aws_ec2_subnet_pb2 import EC2_Subnet
from models.aws.aws_codepipeline_pb2 import CodePipeline
from models.aws.aws_kinesisfirehose_pb2 import KinesisFirehose
from models.aws.aws_workspaces_pb2 import WorkSpaces
from models.aws.aws_emr_pb2 import EMR
from models.aws.aws_cloudformation_pb2 import CloudFormation
from models.aws.aws_fms_pb2 import FMS
from models.aws.aws_codebuild_pb2 import CodeBuild
from models.aws.aws_eks_pb2 import EKS
from models.aws.aws_ec2_pb2 import EC2
from models.aws.aws_glue_pb2 import Glue
from models.aws.aws_greengrass_pb2 import Greengrass
from models.aws.aws_codeguruprofiler_pb2 import CodeGuruProfiler
from models.aws.aws_imagebuilder_pb2 import ImageBuilder
from models.aws.aws_route53resolver_pb2 import Route53Resolver
from models.aws.aws_config_pb2 import Config
from models.aws.aws_qldb_pb2 import QLDB
from models.aws.aws_chatbot_pb2 import Chatbot
from models.aws.aws_neptune_pb2 import Neptune
from models.aws.aws_ec2_instance_pb2 import EC2_Instance
from models.aws.aws_wafregional_pb2 import WAFRegional
from models.aws.aws_sso_pb2 import SSO
from models.aws.aws_autoscalingplans_pb2 import AutoScalingPlans
from models.aws.aws_eventschemas_pb2 import EventSchemas
from models.aws.aws_appflow_pb2 import AppFlow
from models.aws.aws_sdb_pb2 import SDB
from models.aws.aws_appsync_pb2 import AppSync
from models.aws.aws_gamelift_pb2 import GameLift
from models.aws.aws_waf_pb2 import WAF
from models.aws.aws_docdb_pb2 import DocDB
from models.aws.aws_datapipeline_pb2 import DataPipeline
from models.aws.aws_ecr_pb2 import ECR
from models.aws.aws_appconfig_pb2 import AppConfig
from models.aws.aws_amplify_pb2 import Amplify
from models.aws.aws_ssm_pb2 import SSM
from models.aws.aws_detective_pb2 import Detective
from models.aws.aws_ec2_dhcpoptions_pb2 import EC2_DHCPOptions
from models.aws.aws_iot1click_pb2 import IoT1Click
from models.aws.aws_apigatewayv2_pb2 import ApiGatewayV2
from models.aws.aws_globalaccelerator_pb2 import GlobalAccelerator
from models.aws.aws_elasticloadbalancingv2_pb2 import ElasticLoadBalancingV2
from models.aws.aws_backup_pb2 import Backup
from models.aws.aws_athena_pb2 import Athena
from models.aws.aws_apigateway_pb2 import ApiGateway
from models.aws.aws_ec2_vpc_pb2 import EC2_VPC
from models.aws.aws_elasticsearch_pb2 import Elasticsearch
from models.aws.aws_codegurureviewer_pb2 import CodeGuruReviewer
from models.aws.aws_lambda_pb2 import Lambda
from models.aws.aws_ram_pb2 import RAM
from models.aws.aws_rds_dbcluster_pb2 import RDS_DBCluster
from models.aws.aws_redshift_pb2 import Redshift
from models.aws.aws_cloudwatch_pb2 import CloudWatch
from models.aws.aws_dms_pb2 import DMS
from models.aws.aws_sqs_pb2 import SQS
from models.aws.aws_amazonmq_pb2 import AmazonMQ
from models.aws.aws_accessanalyzer_pb2 import AccessAnalyzer
from models.aws.aws_ecs_pb2 import ECS
from models.aws.aws_kinesisanalytics_pb2 import KinesisAnalytics
from models.aws.aws_elasticloadbalancing_pb2 import ElasticLoadBalancing
from models.aws.aws_dynamodb_pb2 import DynamoDB
from models.aws.aws_route53_pb2 import Route53
from models.aws.aws_msk_pb2 import MSK
from models.aws.aws_applicationinsights_pb2 import ApplicationInsights
from models.aws.aws_cognito_pb2 import Cognito
from models.aws.aws_appmesh_pb2 import AppMesh
from models.aws.aws_securityhub_pb2 import SecurityHub
from models.aws.aws_codestar_pb2 import CodeStar
from models.aws.aws_elasticache_cachecluster_pb2 import ElastiCache_CacheCluster
from models.aws.aws_elasticache_replicationgroup_pb2 import ElastiCache_ReplicationGroup
from models.aws.aws_alexa_ask_pb2 import Alexa_ASK
from models.aws.aws_stepfunctions_pb2 import StepFunctions
from models.aws.aws_ec2_networkacl_pb2 import EC2_NetworkACL
from models.aws.aws_opsworkscm_pb2 import OpsWorksCM
from models.aws.aws_s3_pb2 import S3
from models.aws.aws_kinesis_pb2 import Kinesis
from models.aws.aws_directoryservice_pb2 import DirectoryService
from models.aws.aws_efs_pb2 import EFS
from models.aws.aws_dlm_pb2 import DLM
from models.aws.aws_acmpca_pb2 import ACMPCA
from models.aws.aws_resourcegroups_pb2 import ResourceGroups
from models.aws.aws_synthetics_pb2 import Synthetics
from models.aws.aws_budgets_pb2 import Budgets
from models.aws.aws_batch_pb2 import Batch
from models.aws.aws_managedblockchain_pb2 import ManagedBlockchain
from models.aws.aws_rds_dbinstance_pb2 import RDS_DBInstance
from models.aws.aws_applicationautoscaling_pb2 import ApplicationAutoScaling
from models.aws.aws_servicecatalog_pb2 import ServiceCatalog
from models.aws.aws_macie_pb2 import Macie
from models.aws.aws_sns_pb2 import SNS
from models.aws.aws_guardduty_pb2 import GuardDuty
from models.aws.aws_logs_pb2 import Logs
from models.aws.aws_cloud9_pb2 import Cloud9
from models.aws.aws_sagemaker_pb2 import SageMaker
from models.aws.aws_codecommit_pb2 import CodeCommit
from models.aws.aws_lakeformation_pb2 import LakeFormation
from models.aws.aws_cloudtrail_pb2 import CloudTrail
from models.aws.aws_robomaker_pb2 import RoboMaker
from models.aws.aws_networkmanager_pb2 import NetworkManager
from models.aws.aws_rds_pb2 import RDS
from models.aws.aws_mediaconvert_pb2 import MediaConvert
from models.aws.aws_secretsmanager_pb2 import SecretsManager
from models.aws.aws_transfer_pb2 import Transfer
from models.aws.aws_wafv2_pb2 import WAFv2
from models.aws.aws_elasticbeanstalk_pb2 import ElasticBeanstalk
from models.aws.aws_autoscaling_pb2 import AutoScaling
from models.aws.aws_iam_pb2 import IAM
from models.aws.aws_cloudfront_pb2 import CloudFront
from models.aws.aws_kms_pb2 import KMS
from models.aws.aws_fsx_pb2 import FSx
from models.aws.aws_groundstation_pb2 import GroundStation
from models.aws.aws_codestarnotifications_pb2 import CodeStarNotifications
from models.aws.aws_events_pb2 import Events
from models.aws.aws_opsworks_pb2 import OpsWorks
from models.aws.aws_inspector_pb2 import Inspector
from models.aws.aws_ec2_route_pb2 import EC2_Route
from models.aws.aws_ec2_securitygroup_pb2 import EC2_SecurityGroup
from models.aws.aws_dynamodb_table_pb2 import DynamoDB_Table
from models.aws.aws_codedeploy_pb2 import CodeDeploy
from models.aws.aws_iotevents_pb2 import IoTEvents
from models.aws.aws_kinesisanalyticsv2_pb2 import KinesisAnalyticsV2
from models.aws.aws_servicediscovery_pb2 import ServiceDiscovery
from models.aws.aws_iot_pb2 import IoT
from models.aws.aws_iotanalytics_pb2 import IoTAnalytics
from models.aws.aws_codestarconnections_pb2 import CodeStarConnections
from models.aws.aws_certificatemanager_pb2 import CertificateManager
from models.aws.aws_cassandra_pb2 import Cassandra
from models.gcp.gcp_google_storage_bundle_pb2 import GoogleStorage
from models.gcp.gcp_google_app_engine_bundle_pb2 import GoogleAppEngine
from models.gcp.gcp_google_kms_bundle_pb2 import GoogleKms
from models.gcp.gcp_google_dns_bundle_pb2 import GoogleDns
from models.gcp.gcp_google_sql_bundle_pb2 import GoogleSql
from models.gcp.gcp_google_redis_bundle_pb2 import GoogleRedis
from models.gcp.gcp_google_container_bundle_pb2 import GoogleContainer
from models.gcp.gcp_google_pubsub_bundle_pb2 import GooglePubsub
from models.gcp.gcp_google_secret_manager_bundle_pb2 import GoogleSecretManager
from models.gcp.gcp_google_compute_firewall_bundle_pb2 import GoogleComputeFirewall
from models.gcp.gcp_google_compute_firewall_policy_bundle_pb2 import GoogleComputeFirewallPolicy
from models.gcp.gcp_google_compute_instance_bundle_pb2 import GoogleComputeInstance
from models.gcp.gcp_google_compute_network_bundle_pb2 import GoogleComputeNetwork
from models.gcp.gcp_google_compute_route_bundle_pb2 import GoogleComputeRoute
from models.gcp.gcp_google_compute_subnetwork_bundle_pb2 import GoogleComputeSubnetwork
from models.gcp.gcp_google_spanner_bundle_pb2 import GoogleSpanner
from models.gcp.gcp_google_cloud_tasks_bundle_pb2 import GoogleCloudTasks
from models.gcp.gcp_google_certificate_manager_bundle_pb2 import GoogleCertificateManager
from models.gcp.gcp_google_cloudfunctions_bundle_pb2 import GoogleCloudfunctions
from models.kubernetes.kubernetes_kubernetes_namespaced_bundle_pb2 import Kubernetes_Namespaced
from models.kubernetes.kubernetes_kubernetes_nonnamespaced_bundle_pb2 import Kubernetes_NonNamespaced

grpc_type_map: Dict[str, Type[GeneratedProtocolMessageType]] = {
    'type.googleapis.com/oak9.tython.azure.microsoft_recoveryservices_backup.Microsoft_RecoveryServices_Backup': Microsoft_RecoveryServices_Backup,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_privateendpoints.Microsoft_Network_privateEndpoints': Microsoft_Network_privateEndpoints,
    'type.googleapis.com/oak9.tython.azure.microsoft_compute_virtualmachines.Microsoft_Compute_VirtualMachines': Microsoft_Compute_VirtualMachines,
    'type.googleapis.com/oak9.tython.azure.microsoft_compute_virtualmachinescalesets.Microsoft_Compute_VirtualMachineScaleSets': Microsoft_Compute_VirtualMachineScaleSets,
    'type.googleapis.com/oak9.tython.azure.microsoft_recoveryservices.Microsoft_RecoveryServices': Microsoft_RecoveryServices,
    'type.googleapis.com/oak9.tython.azure.microsoft_servicebus.Microsoft_ServiceBus': Microsoft_ServiceBus,
    'type.googleapis.com/oak9.tython.azure.microsoft_cdn.Microsoft_Cdn': Microsoft_Cdn,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_privatelinkservices.Microsoft_Network_privateLinkServices': Microsoft_Network_privateLinkServices,
    'type.googleapis.com/oak9.tython.azure.microsoft_devices.Microsoft_Devices': Microsoft_Devices,
    'type.googleapis.com/oak9.tython.azure.microsoft_keyvault.Microsoft_KeyVault': Microsoft_KeyVault,
    'type.googleapis.com/oak9.tython.azure.microsoft_containerservice.Microsoft_ContainerService': Microsoft_ContainerService,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_virtualnetworks.Microsoft_Network_virtualNetworks': Microsoft_Network_virtualNetworks,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_dnszones.Microsoft_Network_dnsZones': Microsoft_Network_dnsZones,
    'type.googleapis.com/oak9.tython.azure.microsoft_apimanagement.Microsoft_ApiManagement': Microsoft_ApiManagement,
    'type.googleapis.com/oak9.tython.azure.microsoft_web.Microsoft_Web': Microsoft_Web,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_routetables.Microsoft_Network_routeTables': Microsoft_Network_routeTables,
    'type.googleapis.com/oak9.tython.azure.microsoft_aad.Microsoft_AAD': Microsoft_AAD,
    'type.googleapis.com/oak9.tython.azure.microsoft_containerregistry.Microsoft_ContainerRegistry': Microsoft_ContainerRegistry,
    'type.googleapis.com/oak9.tython.azure.microsoft_sql.Microsoft_Sql': Microsoft_Sql,
    'type.googleapis.com/oak9.tython.azure.microsoft_sql_servers.Microsoft_Sql_Servers': Microsoft_Sql_Servers,
    'type.googleapis.com/oak9.tython.azure.microsoft_sql_managedinstances.Microsoft_Sql_ManagedInstances': Microsoft_Sql_ManagedInstances,
    'type.googleapis.com/oak9.tython.azure.microsoft_sql_databases.Microsoft_Sql_Databases': Microsoft_Sql_Databases,
    'type.googleapis.com/oak9.tython.azure.microsoft_iotsecurity.Microsoft_IoTSecurity': Microsoft_IoTSecurity,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_loadbalancers.Microsoft_Network_loadBalancers': Microsoft_Network_loadBalancers,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_privatednszones.Microsoft_Network_privateDnsZones': Microsoft_Network_privateDnsZones,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_applicationgateways.Microsoft_Network_applicationGateways': Microsoft_Network_applicationGateways,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_trafficmanager.Microsoft_Network_TrafficManager': Microsoft_Network_TrafficManager,
    'type.googleapis.com/oak9.tython.azure.microsoft_healthcareapis.Microsoft_HealthcareApis': Microsoft_HealthcareApis,
    'type.googleapis.com/oak9.tython.azure.microsoft_iotcentral.Microsoft_IotCentral': Microsoft_IotCentral,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_frontdoor.Microsoft_Network_FrontDoor': Microsoft_Network_FrontDoor,
    'type.googleapis.com/oak9.tython.azure.microsoft_elastic.Microsoft_Elastic': Microsoft_Elastic,
    'type.googleapis.com/oak9.tython.azure.microsoft_storage.Microsoft_Storage': Microsoft_Storage,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_frontdoor_networkexperimentprofiles.Microsoft_Network_FrontDoor_NetworkExperimentProfiles': Microsoft_Network_FrontDoor_NetworkExperimentProfiles,
    'type.googleapis.com/oak9.tython.azure.microsoft_cache.Microsoft_Cache': Microsoft_Cache,
    'type.googleapis.com/oak9.tython.azure.microsoft_network.Microsoft_Network': Microsoft_Network,
    'type.googleapis.com/oak9.tython.azure.microsoft_documentdb.Microsoft_DocumentDB': Microsoft_DocumentDB,
    'type.googleapis.com/oak9.tython.azure.microsoft_streamanalytics.Microsoft_StreamAnalytics': Microsoft_StreamAnalytics,
    'type.googleapis.com/oak9.tython.azure.microsoft_kubernetes.Microsoft_Kubernetes': Microsoft_Kubernetes,
    'type.googleapis.com/oak9.tython.azure.microsoft_recoveryservices_siterecovery.Microsoft_RecoveryServices_SiteRecovery': Microsoft_RecoveryServices_SiteRecovery,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_networksecuritygroups.Microsoft_Network_networkSecurityGroups': Microsoft_Network_networkSecurityGroups,
    'type.googleapis.com/oak9.tython.azure.microsoft_eventgrid.Microsoft_EventGrid': Microsoft_EventGrid,
    'type.googleapis.com/oak9.tython.azure.microsoft_network_firewallpolicies.Microsoft_Network_firewallPolicies': Microsoft_Network_firewallPolicies,
    'type.googleapis.com/oak9.tython.azure.microsoft_app_containerapps.Microsoft_App_containerApps': Microsoft_App_containerApps,
    'type.googleapis.com/oak9.tython.aws.ec2_vpcendpoint.EC2_VPCEndpoint': EC2_VPCEndpoint,
    'type.googleapis.com/oak9.tython.aws.ec2_subnet.EC2_Subnet': EC2_Subnet,
    'type.googleapis.com/oak9.tython.aws.codepipeline.CodePipeline': CodePipeline,
    'type.googleapis.com/oak9.tython.aws.kinesisfirehose.KinesisFirehose': KinesisFirehose,
    'type.googleapis.com/oak9.tython.aws.workspaces.WorkSpaces': WorkSpaces,
    'type.googleapis.com/oak9.tython.aws.emr.EMR': EMR,
    'type.googleapis.com/oak9.tython.aws.cloudformation.CloudFormation': CloudFormation,
    'type.googleapis.com/oak9.tython.aws.fms.FMS': FMS,
    'type.googleapis.com/oak9.tython.aws.codebuild.CodeBuild': CodeBuild,
    'type.googleapis.com/oak9.tython.aws.eks.EKS': EKS,
    'type.googleapis.com/oak9.tython.aws.glue.Glue': Glue,
    'type.googleapis.com/oak9.tython.aws.greengrass.Greengrass': Greengrass,
    'type.googleapis.com/oak9.tython.aws.codeguruprofiler.CodeGuruProfiler': CodeGuruProfiler,
    'type.googleapis.com/oak9.tython.aws.imagebuilder.ImageBuilder': ImageBuilder,
    'type.googleapis.com/oak9.tython.aws.route53resolver.Route53Resolver': Route53Resolver,
    'type.googleapis.com/oak9.tython.aws.config.Config': Config,
    'type.googleapis.com/oak9.tython.aws.qldb.QLDB': QLDB,
    'type.googleapis.com/oak9.tython.aws.chatbot.Chatbot': Chatbot,
    'type.googleapis.com/oak9.tython.aws.neptune.Neptune': Neptune,
    'type.googleapis.com/oak9.tython.aws.ec2_instance.EC2_Instance': EC2_Instance,
    'type.googleapis.com/oak9.tython.aws.wafregional.WAFRegional': WAFRegional,
    'type.googleapis.com/oak9.tython.aws.sso.SSO': SSO,
    'type.googleapis.com/oak9.tython.aws.autoscalingplans.AutoScalingPlans': AutoScalingPlans,
    'type.googleapis.com/oak9.tython.aws.eventschemas.EventSchemas': EventSchemas,
    'type.googleapis.com/oak9.tython.aws.appflow.AppFlow': AppFlow,
    'type.googleapis.com/oak9.tython.aws.sdb.SDB': SDB,
    'type.googleapis.com/oak9.tython.aws.appsync.AppSync': AppSync,
    'type.googleapis.com/oak9.tython.aws.gamelift.GameLift': GameLift,
    'type.googleapis.com/oak9.tython.aws.waf.WAF': WAF,
    'type.googleapis.com/oak9.tython.aws.docdb.DocDB': DocDB,
    'type.googleapis.com/oak9.tython.aws.datapipeline.DataPipeline': DataPipeline,
    'type.googleapis.com/oak9.tython.aws.ecr.ECR': ECR,
    'type.googleapis.com/oak9.tython.aws.appconfig.AppConfig': AppConfig,
    'type.googleapis.com/oak9.tython.aws.amplify.Amplify': Amplify,
    'type.googleapis.com/oak9.tython.aws.ssm.SSM': SSM,
    'type.googleapis.com/oak9.tython.aws.detective.Detective': Detective,
    'type.googleapis.com/oak9.tython.aws.ec2_dhcpoptions.EC2_DHCPOptions': EC2_DHCPOptions,
    'type.googleapis.com/oak9.tython.aws.iot1click.IoT1Click': IoT1Click,
    'type.googleapis.com/oak9.tython.aws.apigatewayv2.ApiGatewayV2': ApiGatewayV2,
    'type.googleapis.com/oak9.tython.aws.globalaccelerator.GlobalAccelerator': GlobalAccelerator,
    'type.googleapis.com/oak9.tython.aws.elasticloadbalancingv2.ElasticLoadBalancingV2': ElasticLoadBalancingV2,
    'type.googleapis.com/oak9.tython.aws.backup.Backup': Backup,
    'type.googleapis.com/oak9.tython.aws.athena.Athena': Athena,
    'type.googleapis.com/oak9.tython.aws.apigateway.ApiGateway': ApiGateway,
    'type.googleapis.com/oak9.tython.aws.ec2_vpc.EC2_VPC': EC2_VPC,
    'type.googleapis.com/oak9.tython.aws.elasticsearch.Elasticsearch': Elasticsearch,
    'type.googleapis.com/oak9.tython.aws.codegurureviewer.CodeGuruReviewer': CodeGuruReviewer,
    'type.googleapis.com/oak9.tython.aws.lambda.Lambda': Lambda,
    'type.googleapis.com/oak9.tython.aws.ram.RAM': RAM,
    'type.googleapis.com/oak9.tython.aws.rds_dbcluster.RDS_DBCluster': RDS_DBCluster,
    'type.googleapis.com/oak9.tython.aws.redshift.Redshift': Redshift,
    'type.googleapis.com/oak9.tython.aws.cloudwatch.CloudWatch': CloudWatch,
    'type.googleapis.com/oak9.tython.aws.dms.DMS': DMS,
    'type.googleapis.com/oak9.tython.aws.sqs.SQS': SQS,
    'type.googleapis.com/oak9.tython.aws.amazonmq.AmazonMQ': AmazonMQ,
    'type.googleapis.com/oak9.tython.aws.accessanalyzer.AccessAnalyzer': AccessAnalyzer,
    'type.googleapis.com/oak9.tython.aws.ecs.ECS': ECS,
    'type.googleapis.com/oak9.tython.aws.kinesisanalytics.KinesisAnalytics': KinesisAnalytics,
    'type.googleapis.com/oak9.tython.aws.elasticloadbalancing.ElasticLoadBalancing': ElasticLoadBalancing,
    'type.googleapis.com/oak9.tython.aws.dynamodb.DynamoDB': DynamoDB,
    'type.googleapis.com/oak9.tython.aws.route53.Route53': Route53,
    'type.googleapis.com/oak9.tython.aws.msk.MSK': MSK,
    'type.googleapis.com/oak9.tython.aws.applicationinsights.ApplicationInsights': ApplicationInsights,
    'type.googleapis.com/oak9.tython.aws.cognito.Cognito': Cognito,
    'type.googleapis.com/oak9.tython.aws.appmesh.AppMesh': AppMesh,
    'type.googleapis.com/oak9.tython.aws.securityhub.SecurityHub': SecurityHub,
    'type.googleapis.com/oak9.tython.aws.codestar.CodeStar': CodeStar,
    'type.googleapis.com/oak9.tython.aws.elasticache_cachecluster.ElastiCache_CacheCluster': ElastiCache_CacheCluster,
    'type.googleapis.com/oak9.tython.aws.elasticache_replicationgroup.ElastiCache_ReplicationGroup': ElastiCache_ReplicationGroup,
    'type.googleapis.com/oak9.tython.aws.alexa_ask.Alexa_ASK': Alexa_ASK,
    'type.googleapis.com/oak9.tython.aws.stepfunctions.StepFunctions': StepFunctions,
    'type.googleapis.com/oak9.tython.aws.ec2_networkacl.EC2_NetworkACL': EC2_NetworkACL,
    'type.googleapis.com/oak9.tython.aws.opsworkscm.OpsWorksCM': OpsWorksCM,
    'type.googleapis.com/oak9.tython.aws.s3.S3': S3,
    'type.googleapis.com/oak9.tython.aws.kinesis.Kinesis': Kinesis,
    'type.googleapis.com/oak9.tython.aws.directoryservice.DirectoryService': DirectoryService,
    'type.googleapis.com/oak9.tython.aws.efs.EFS': EFS,
    'type.googleapis.com/oak9.tython.aws.dlm.DLM': DLM,
    'type.googleapis.com/oak9.tython.aws.acmpca.ACMPCA': ACMPCA,
    'type.googleapis.com/oak9.tython.aws.resourcegroups.ResourceGroups': ResourceGroups,
    'type.googleapis.com/oak9.tython.aws.synthetics.Synthetics': Synthetics,
    'type.googleapis.com/oak9.tython.aws.budgets.Budgets': Budgets,
    'type.googleapis.com/oak9.tython.aws.batch.Batch': Batch,
    'type.googleapis.com/oak9.tython.aws.managedblockchain.ManagedBlockchain': ManagedBlockchain,
    'type.googleapis.com/oak9.tython.aws.rds_dbinstance.RDS_DBInstance': RDS_DBInstance,
    'type.googleapis.com/oak9.tython.aws.applicationautoscaling.ApplicationAutoScaling': ApplicationAutoScaling,
    'type.googleapis.com/oak9.tython.aws.servicecatalog.ServiceCatalog': ServiceCatalog,
    'type.googleapis.com/oak9.tython.aws.macie.Macie': Macie,
    'type.googleapis.com/oak9.tython.aws.sns.SNS': SNS,
    'type.googleapis.com/oak9.tython.aws.guardduty.GuardDuty': GuardDuty,
    'type.googleapis.com/oak9.tython.aws.logs.Logs': Logs,
    'type.googleapis.com/oak9.tython.aws.cloud9.Cloud9': Cloud9,
    'type.googleapis.com/oak9.tython.aws.sagemaker.SageMaker': SageMaker,
    'type.googleapis.com/oak9.tython.aws.codecommit.CodeCommit': CodeCommit,
    'type.googleapis.com/oak9.tython.aws.lakeformation.LakeFormation': LakeFormation,
    'type.googleapis.com/oak9.tython.aws.cloudtrail.CloudTrail': CloudTrail,
    'type.googleapis.com/oak9.tython.aws.robomaker.RoboMaker': RoboMaker,
    'type.googleapis.com/oak9.tython.aws.networkmanager.NetworkManager': NetworkManager,
    'type.googleapis.com/oak9.tython.aws.rds.RDS': RDS,
    'type.googleapis.com/oak9.tython.aws.mediaconvert.MediaConvert': MediaConvert,
    'type.googleapis.com/oak9.tython.aws.secretsmanager.SecretsManager': SecretsManager,
    'type.googleapis.com/oak9.tython.aws.transfer.Transfer': Transfer,
    'type.googleapis.com/oak9.tython.aws.wafv2.WAFv2': WAFv2,
    'type.googleapis.com/oak9.tython.aws.elasticbeanstalk.ElasticBeanstalk': ElasticBeanstalk,
    'type.googleapis.com/oak9.tython.aws.autoscaling.AutoScaling': AutoScaling,
    'type.googleapis.com/oak9.tython.aws.iam.IAM': IAM,
    'type.googleapis.com/oak9.tython.aws.cloudfront.CloudFront': CloudFront,
    'type.googleapis.com/oak9.tython.aws.kms.KMS': KMS,
    'type.googleapis.com/oak9.tython.aws.fsx.FSx': FSx,
    'type.googleapis.com/oak9.tython.aws.groundstation.GroundStation': GroundStation,
    'type.googleapis.com/oak9.tython.aws.codestarnotifications.CodeStarNotifications': CodeStarNotifications,
    'type.googleapis.com/oak9.tython.aws.events.Events': Events,
    'type.googleapis.com/oak9.tython.aws.opsworks.OpsWorks': OpsWorks,
    'type.googleapis.com/oak9.tython.aws.inspector.Inspector': Inspector,
    'type.googleapis.com/oak9.tython.aws.ec2_route.RouteTable': EC2_Route,
    'type.googleapis.com/oak9.tython.aws.ec2_route.EC2_Route': EC2_Route,
    'type.googleapis.com/oak9.tython.aws.ec2_securitygroup.EC2_SecurityGroup': EC2_SecurityGroup,
    'type.googleapis.com/oak9.tython.aws.dynamodb_table.DynamoDB_Table': DynamoDB_Table,
    'type.googleapis.com/oak9.tython.aws.codedeploy.CodeDeploy': CodeDeploy,
    'type.googleapis.com/oak9.tython.aws.iotevents.IoTEvents': IoTEvents,
    'type.googleapis.com/oak9.tython.aws.kinesisanalyticsv2.KinesisAnalyticsV2': KinesisAnalyticsV2,
    'type.googleapis.com/oak9.tython.aws.servicediscovery.ServiceDiscovery': ServiceDiscovery,
    'type.googleapis.com/oak9.tython.aws.iot.IoT': IoT,
    'type.googleapis.com/oak9.tython.aws.iotanalytics.IoTAnalytics': IoTAnalytics,
    'type.googleapis.com/oak9.tython.aws.codestarconnections.CodeStarConnections': CodeStarConnections,
    'type.googleapis.com/oak9.tython.aws.certificatemanager.CertificateManager': CertificateManager,
    'type.googleapis.com/oak9.tython.aws.cassandra.Cassandra': Cassandra,
    'type.googleapis.com/oak9.tython.gcp.google_storage_bundle.GoogleStorage': GoogleStorage,
    'type.googleapis.com/oak9.tython.gcp.google_app_engine_bundle.GoogleAppEngine': GoogleAppEngine,
    'type.googleapis.com/oak9.tython.gcp.google_kms_bundle.GoogleKms': GoogleKms,
    'type.googleapis.com/oak9.tython.gcp.google_dns_bundle.GoogleDns': GoogleDns,
    'type.googleapis.com/oak9.tython.gcp.google_sql_bundle.GoogleSql': GoogleSql,
    'type.googleapis.com/oak9.tython.gcp.google_redis_bundle.GoogleRedis': GoogleRedis,
    'type.googleapis.com/oak9.tython.gcp.google_container_bundle.GoogleContainer': GoogleContainer,
    'type.googleapis.com/oak9.tython.gcp.google_pubsub_bundle.GooglePubsub': GooglePubsub,
    'type.googleapis.com/oak9.tython.gcp.google_secret_manager_bundle.GoogleSecretManager': GoogleSecretManager,
    'type.googleapis.com/oak9.tython.gcp.google_compute_firewall_bundle.GoogleComputeFirewall': GoogleComputeFirewall,
    'type.googleapis.com/oak9.tython.gcp.google_compute_firewall_policy_bundle.GoogleComputeFirewallPolicy': GoogleComputeFirewallPolicy,
    'type.googleapis.com/oak9.tython.gcp.google_compute_instance_bundle.GoogleComputeInstance': GoogleComputeInstance,
    'type.googleapis.com/oak9.tython.gcp.google_compute_network_bundle.GoogleComputeNetwork': GoogleComputeNetwork,
    'type.googleapis.com/oak9.tython.gcp.google_compute_route_bundle.GoogleComputeRoute': GoogleComputeRoute,
    'type.googleapis.com/oak9.tython.gcp.google_compute_subnetwork_bundle.GoogleComputeSubnetwork': GoogleComputeSubnetwork,
    'type.googleapis.com/oak9.tython.gcp.google_spanner_bundle.GoogleSpanner': GoogleSpanner,
    'type.googleapis.com/oak9.tython.gcp.google_cloud_tasks_bundle.GoogleCloudTasks': GoogleCloudTasks,
    'type.googleapis.com/oak9.tython.gcp.google_certificate_manager_bundle.GoogleCertificateManager': GoogleCertificateManager,
    'type.googleapis.com/oak9.tython.gcp.google_cloudfunctions_bundle.GoogleCloudfunctions': GoogleCloudfunctions,
    'type.googleapis.com/oak9.tython.kubernetes.kubernetes_namespaced_bundle.Kubernetes_Namespaced': Kubernetes_Namespaced,
    'type.googleapis.com/oak9.tython.kubernetes.kubernetes_nonnamespaced_bundle.Kubernetes_NonNamespaced': Kubernetes_NonNamespaced
}
