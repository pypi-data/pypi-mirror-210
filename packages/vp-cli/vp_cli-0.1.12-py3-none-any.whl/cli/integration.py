import enum
import json
import logging
from urllib.parse import urlparse, parse_qs
from cli.util import Formatter, pretty_date, edit_entry

from cli.apiexternal import (
    get_integrations,
    add_registry,
    update_registry,
    delete_integration,
    add_cloud_integration,
    check_aws_credentials,
    create_cloudformation_template,
    create_cloudformation_stack,
    describe_cloudformation_stack,
)

log = logging.getLogger()


@enum.unique
class IntegrationTypes(enum.IntEnum):
    ANY = 0
    DOCKER_REGISTRY = 4


class DockerRegistryIntegration:
    TYPE = IntegrationTypes.DOCKER_REGISTRY

    @staticmethod
    def add(
        name,
        address,
        repository,
        username=None,
        password=None,
        type_="docker_v2",
        lookup_tag="latest",
    ):
        try:
            type_ = {"docker_hub": 1, "ecr": 2, "ecr": 3, "acr": 4, "docker_v2": 5,}[
                type_
            ]
        except KeyError:
            raise Exception(
                f"Registry type {type_} not part of (docker_hub|aws|gcr|azure|docker_v2)"
            )

        return add_registry(
            name,
            address,
            repository,
            username=username,
            password=password,
            type_=type_,
            lookup_tag=lookup_tag,
        )

    @staticmethod
    def list_():
        registries = get_integrations(type_=DockerRegistryIntegration.TYPE)
        headers = [
            "Id",
            "Name",
            "Registry Address",
            "Repository",
            "Lookup Tag",
            "Created",
            "Last Updated",
            "Status",
        ]
        rows = [
            [
                registry["id"],
                registry["name"],
                registry["address"],
                registry["repository"],
                registry["lookup_tag"],
                pretty_date(registry["created_time"]),
                pretty_date(registry["modified_time"]),
                registry["status"],
            ]
            for registry in registries
        ]
        return Formatter.table(headers, rows)

    @staticmethod
    def get(id_):
        integration = get_integrations(type_=DockerRegistryIntegration.TYPE, id_=id_)[0]
        return Formatter.integration(integration)

    @staticmethod
    def edit(id_):
        registry = get_integrations(type_=DockerRegistryIntegration.TYPE, id_=id_)[0]
        type_ = registry["type_id"]
        for key in (
            "created_by_user_id",
            "created_time",
            "added_to_anchore",
            "status",
            "failreason",
            "modified_by_user_id",
            "modified_time",
            "type_id",
            "registry_type",
        ):
            del registry[key]

        with edit_entry(json.dumps(registry, indent=4), suffix=".json") as f:
            edited = json.load(f)

        if edited == registry:
            return "No changes detected!"

        updated = update_registry(id_, edited, type_=type_)
        if updated:
            return "Updated!"
        else:
            return "Failed"

    @staticmethod
    def delete(id_):
        return delete_integration(id_, type_=DockerRegistryIntegration.TYPE)


class CloudIntegration:
    @staticmethod
    def _add_aws_integration(
        name,
        types,
        flow_log_resource_type=None,
        flow_log_resource_id=None,
        aws_role_arn=None,
    ):
        if not aws_role_arn:
            input_ = input(
                "VantagePoint will create new IAM role for this integration, do you want to proceed [Y/N]: "
            )
            if not input_.lower() == "y":
                return "Aborting!"

            log.info("Creating cloudformation template")
            cloudformation_url = create_cloudformation_template(
                integration_types=types,
                flow_log_resource_type=flow_log_resource_type,
                flow_log_resource_id=flow_log_resource_id,
            )
            template_url = cloudformation_url.split("templateURL=")[-1]
            path = template_url.split("&")[0]
            qs = parse_qs(template_url)
            log.info("Creating stack")
            # create_cloudformation_stack(path, qs["stackName"][0], qs["param_ExternalId"][0])
            stack = describe_cloudformation_stack(qs["stackName"][0])
            for output in stack["Outputs"]:
                if output["OutputKey"] == "RoleARN":
                    aws_role_arn = output["OutputValue"]
                    break
            else:  # no-break
                raise Exception("Error creating aws role")

        log.info("Checking credentials")
        if not check_aws_credentials(aws_role_arn):
            raise Exception(f'Check credentials failed on resource "{aws_role_arn}"')

        log.info("Adding integration")
        return add_cloud_integration(
            name,
            types,
            provider="aws",
            aws_role_arn=aws_role_arn,
            flow_log_resource_type=flow_log_resource_type,
            flow_log_resource_id=flow_log_resource_id,
        )

    @staticmethod
    def _add_azure_integraiton(
        name, types, azure_principal, azure_password, azure_tenant
    ):
        return add_cloud_integration(
            name,
            types,
            provider="azure",
            azure_principal=azure_principal,
            azure_password=azure_password,
            azure_tenant=azure_tenant,
        )

    @staticmethod
    def add(
        name,
        provider,
        types=[],
        aws_role_arn=None,
        flow_log_resource_type=None,
        flow_log_resource_id=None,
        azure_principal=None,
        azure_password=None,
        azure_tenant=None,
    ):
        try:
            types = [
                {"security": 1, "cloud_log": 2, "network": 5, "flow_log": 3,}[type_]
                for type_ in types
            ]
        except KeyError:
            raise Exception("Unknown integration type")

        if provider == "aws":
            # resource type and id required for flow log
            if 3 in types and not (flow_log_resource_type and flow_log_resource_id):
                raise Exception("Resource type and id is required for integration type flow_log. See --help")

            allowed_resource_types = ["VPC", "Subnet", "NetworkInterface"]
            if flow_log_resource_type and flow_log_resource_type not in allowed_resource_types:
                raise Exception(f"Resource type should be one of {str(allowed_resource_types)}")

            return CloudIntegration._add_aws_integration(name, types, flow_log_resource_type, flow_log_resource_id, aws_role_arn)

        if provider == "azure":
            return CloudIntegration._add_azure_integraiton(
                name, types, azure_principal, azure_password, azure_tenant
            )

    @staticmethod
    def list_():
        integrations = get_integrations(type_=IntegrationTypes.ANY)
        headers = ["Id", "Name", "Cloud Provider", "Created", "Last Updated", "Status"]
        rows = [
            [
                integration["id"],
                integration["name"],
                integration["cloud_provider"].title(),
                pretty_date(integration["created_time"]),
                pretty_date(integration["modified_time"]),
                "DISABLED" if integration["is_deleted"] else "ENABLED",
            ]
            for integration in integrations
            if not integration["is_deleted"]
        ]
        return Formatter.table(headers, rows)

    @staticmethod
    def get(id_):
        integration = get_integrations(type_=IntegrationTypes.ANY, id_=id_)
        return Formatter.integration(integration)

    @staticmethod
    def delete(id_):
        return delete_integration(id_, type_=IntegrationTypes.ANY)
