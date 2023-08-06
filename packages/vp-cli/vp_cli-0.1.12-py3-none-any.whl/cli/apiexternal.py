import os
import requests
import logging
import base64
import boto3
from cli.util import Formatter, get_vp_config
from cli.consts import VP_CLI_VERSION
import stat
import sys
import re
import configparser
from pathlib import Path
from io import StringIO

VP_PORTAL = None
VP_TOKEN = None
VP_SECRET_KEY = None
VP_WORKSPACE = None
CREDENTIALS_FILE = f"{Path.home()}/.vantagepoint/config"

##########################################################################################################3


def load_credentials(report_err=True):
    global VP_PORTAL, VP_TOKEN, VP_SECRET_KEY, VP_WORKSPACE
    config = configparser.ConfigParser()

    VP_PORTAL = os.environ.get("VP_PORTAL", None)
    VP_TOKEN = os.environ.get("VP_TOKEN", None)
    VP_SECRET_KEY = os.environ.get("VP_SECRET_KEY", None)
    VP_WORKSPACE = os.environ.get("VP_WORKSPACE", None)

    if not all([VP_PORTAL, VP_TOKEN, VP_SECRET_KEY]):
        try:
            config.read(CREDENTIALS_FILE)
            VP_TOKEN = config.get("default", "token")
            VP_SECRET_KEY = config.get("default", "secret_key")
            VP_PORTAL = config.get("default", "portal")
            VP_WORKSPACE = config.get("default", "workspace", fallback=None)
            if not VP_PORTAL.endswith("/"):
                VP_PORTAL = "%s/" % (VP_PORTAL)
        except:
            pass

    if not all([VP_PORTAL, VP_TOKEN, VP_SECRET_KEY]) and report_err:
        raise Exception(
            "You must set configuration via 'vp_cli configure' or provide it as environment variables VP_PORTAL, VP_TOKEN, VP_SECRET_KEY."
        )


def configure():

    global VP_PORTAL, VP_TOKEN, VP_SECRET_KEY
    load_credentials(report_err=False)
    credentials = {"token": VP_TOKEN, "secret_key": VP_SECRET_KEY, "portal": VP_PORTAL}

    try:
        Path(os.path.dirname(CREDENTIALS_FILE)).mkdir(parents=True, exist_ok=True)
    except:
        pass

    VP_TOKEN = input(
        "Token [%s]: "
        % (
            "%s%s" % ("*" * 10, credentials["token"][-4:])
            if credentials["token"]
            else "*" * 14
        )
    )
    while not re.search("^[A-Za-z0-9\.\-\_]{60,140}$", VP_TOKEN):
        print("Invalid format. Try again.")
        VP_TOKEN = input(
            "Token [%s]: "
            % (
                "%s%s" % ("*" * 10, credentials["token"][-4:])
                if credentials["token"]
                else "*" * 14
            )
        )

    VP_SECRET_KEY = input(
        "Secret Key [%s]: "
        % (
            "%s%s" % ("*" * 10, credentials["secret_key"][-4:])
            if credentials["secret_key"]
            else "*" * 14
        )
    )
    while not re.search("^[a-f0-9]{48}$", VP_SECRET_KEY):
        print("Invalid format. Try again.")
        VP_SECRET_KEY = input(
            "Secret Key [%s]: "
            % (
                "%s%s" % ("*" * 10, credentials["secret_key"][-4:])
                if credentials["secret_key"]
                else "*" * 14
            )
        )

    VP_PORTAL = input(
        "Portal URL [%s]: "
        % ("%s" % (credentials["portal"]) if credentials["portal"] else "*" * 14)
    )
    while not VP_PORTAL.lower().startswith("https://"):
        print("Invalid format, must start with https://. Try again.")
        VP_PORTAL = input(
            "Portal URL [%s]: "
            % ("%s" % (credentials["portal"]) if credentials["portal"] else "*" * 14)
        )

    config = configparser.ConfigParser()
    config.readfp(StringIO("[default]"))
    config.set("default", "token", VP_TOKEN)
    config.set("default", "secret_key", VP_SECRET_KEY)
    config.set("default", "portal", VP_PORTAL)
    with open(CREDENTIALS_FILE, "w+") as configfile:
        config.write(configfile)

    os.chmod(CREDENTIALS_FILE, stat.S_IRUSR | stat.S_IWUSR)
    print("Configuration saved")


##########################################################################################################3

log = logging.getLogger()

if len(sys.argv) > 1 and not sys.argv[1].lower() == "configure":
    try:
        load_credentials()
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": f"vp-cli/v{VP_CLI_VERSION}",
                "X-VP-TOKEN": VP_TOKEN,
                "X-VP-SECRET": VP_SECRET_KEY,
                "X-VP-WORKSPACE": VP_WORKSPACE,
            }
        )
    except Exception as e:
        log.error(str(e))
        sys.exit(1)



##########################################################################################################3


def catch_exception(response):
    try:
        response.raise_for_status()
    except Exception as e:
        try:
            error_message = e.response.json()["message"]
            raise Exception(error_message)
        except:
            raise Exception("Failed!")


##########################################################################################################3


def get_integrations(type_, id_=None):
    endpoint = f"{VP_PORTAL}/api/ops_list_integrations"
    params = {"type": type_.value, "id": id_}
    response = session.get(endpoint, params=params)
    catch_exception(response)
    return response.json()["data"]


def add_registry(
    name,
    address,
    repository,
    username=None,
    password=None,
    type_=5,
    lookup_tag="latest",
):
    endpoint = f"{VP_PORTAL}/asynch_integration_items"
    integration_type = 4

    payload = {
        "name": name,
        "type_id": integration_type,
        "docker_registry_address": address,
        "docker_registry_uname": username if username else "",
        "docker_registry_password": password if password else "",
        "docker_repository_name": repository,
        "docker_registry_type": type_,
        "docker_repository_lookup_tag": lookup_tag,
    }
    response = session.post(endpoint, json=payload)
    catch_exception(response)
    return "Added!"


def update_registry(id_, registry, type_):
    endpoint = f"{VP_PORTAL}/asynch_integration_items"
    integration_type = 4

    payload = {
        "id": id_,
        "name": registry["name"],
        "type_id": type_,
        "docker_registry_address": registry["address"],
        "docker_registry_uname": registry["username"] if registry["username"] else "",
        "docker_registry_password": registry["password"]
        if registry["password"]
        else "",
        "docker_registry_type": type_,
        "docker_repository_name": registry["repository"],
        "docker_repository_lookup_tag": registry["lookup_tag"],
    }
    response = session.post(endpoint, json=payload)
    catch_exception(response)
    return "Updated!"


def delete_integration(id_, type_):
    endpoint = f"{VP_PORTAL}/integration/delete"
    response = session.delete(endpoint, params={"id": id_, "type": type_.value})
    catch_exception(response)
    return "Success"


def add_cloud_integration(
    name,
    types,
    provider,
    aws_role_arn=None,
    flow_log_resource_type=None,
    flow_log_resource_id=None,
    azure_principal=None,
    azure_password=None,
    azure_tenant=None,
):
    endpoint = f"{VP_PORTAL}/asynch_cloud_integration_items"
    payload = {
        "name": name,
        "integration_types": types,
        "cloud_provider": provider,
        "aws_role_arn": aws_role_arn,
        "flow_log_resource_type": flow_log_resource_type,
        "flow_log_resource_id": flow_log_resource_id,
        "azure-principal-name": azure_principal,
        "azure-principal-password": azure_password,
        "azure-principal-tenant": azure_tenant,
    }
    response = session.post(endpoint, json=payload)
    catch_exception(response)
    return "Added!"


def check_aws_credentials(aws_role_arn, integration_types=[]):
    endpoint = f"{VP_PORTAL}/asynch_cloud_credentials"
    payload = {"integration_types": integration_types, "aws_role_arn": aws_role_arn}
    response = session.post(endpoint, json=payload)
    catch_exception(response)
    return True if response.json()["result"] == "success" else False


def create_cloudformation_template(
    integration_types, flow_log_resource_type, flow_log_resource_id
):
    endpoint = f"{VP_PORTAL}/cloudformation/templates/integrations"
    payload = {
        "integration_types": integration_types,
        "flow_log_resource_type": flow_log_resource_type,
        "flow_log_resource_id": flow_log_resource_id,
    }
    response = session.post(endpoint, json=payload)
    catch_exception(response)
    return response.json()["cloud_formation_url"]


def create_cloudformation_stack(template_url, stack_name, external_id):
    client = boto3.client("cloudformation")
    response = client.create_stack(
        StackName=stack_name,
        TemplateURL=template_url,
        Parameters=[{"ParameterKey": "ExternalId", "ParameterValue": external_id}],
        Capabilities=["CAPABILITY_IAM"],
    )
    return response


def describe_cloudformation_stack(stack_name):
    client = boto3.client("cloudformation")
    waiter = client.get_waiter("stack_create_complete")
    waiter.wait(StackName=stack_name, WaiterConfig={"Delay": 30, "MaxAttempts": 120})
    return client.describe_stacks(StackName=stack_name)["Stacks"][0]


##########################################################################################################3


def get_images(input_image=None):
    endpoint = f"{VP_PORTAL}/api/ops_list_images"
    response = session.get(endpoint)
    catch_exception(response)
    images = response.json()["data"]
    if input_image:
        registry = input_image.split("/")[0]
        repo, tag = input_image.split("/")[-1].split(":")

        filtered = list(
            filter(
                lambda img: img["registry"] == registry
                and img["repo"] == repo
                and img["tag"] == tag,
                images,
            )
        )

        return filtered[0] if filtered else None

    else:
        return images


def add_image(
    input_image, dockerfile=None, force=False, annotations="", autosubscribe=False
):
    endpoint = f"{VP_PORTAL}/api/image_scan"
    if dockerfile:
        with open(dockerfile, "r") as f:
            dockerfile = base64.encodestring(f.read().encode())
    payload = {
        "input_image": input_image,
        "dockerfile": dockerfile.decode("utf-8") if dockerfile else "",
        "annotations": annotations,
    }
    response = session.post(
        endpoint,
        json=payload,
        params={
            "force": str(force).lower(),
            "autosubscribe": str(autosubscribe).lower(),
        },
    )
    catch_exception(response)
    return "Success"


def delete_image(input_image, force=True):
    endpoint = f"{VP_PORTAL}/api/image_scan"
    payload = {"input_image": input_image}
    response = session.delete(endpoint, json=payload, params={"force": force})
    catch_exception(response)
    return "Success"


##########################################################################################################3


def get_image_vulnerabilities(digest):
    endpoint = f"{VP_PORTAL}/ops/containers/image/{digest}/vuln"
    response = session.get(endpoint)
    response.raise_for_status()
    return response.json()["data"]


##########################################################################################################3


def evaluate_image(image_digest, tag):
    endpoint = f"{VP_PORTAL}/api/image_scan/{image_digest}/evaluate"
    response = session.post(endpoint, params={"tag": tag})
    catch_exception(response)
    _data = response.json()["data"]
    return _data, next(iter(_data.values()))[0]["status"]


##########################################################################################################3


def get_reputation_feeds(id_=None):
    endpoint = f"{VP_PORTAL}/api/intel/reputation/feeds"
    response = session.get(endpoint, params={"id": id_})
    catch_exception(response)
    return response.json()["data"]


def add_reputation_feed(feed):
    endpoint = f"{VP_PORTAL}/api/intel/reputation/feeds/form/"
    response = session.post(endpoint, data=feed)
    catch_exception(response)
    return "Saved successfully" in response.text


def update_reputaiton_feed(id_, feed):
    endpoint = f"{VP_PORTAL}/api/intel/reputation/feeds/form/"
    payload = {
        "id_": id_,
        "name": feed["name"],
        "risk_score": feed["risk_score"],
        "entry_type": feed["type"],
        "entries": ",".join(feed.get("entries", [])),
        "url": feed.get("url", ""),
    }
    feed["id"] = id_
    response = session.post(endpoint, data=payload)
    catch_exception(response)
    return "Saved successfully" in response.text


def delete_reputation_feed(id_):
    endpoint = f"{VP_PORTAL}/api/intel/reputation/custom_feed/delete"
    payload = {"id": id_}
    response = session.delete(endpoint, json=payload)
    catch_exception(response)
    return "Success"


##########################################################################################################3


def get_workspaces():
    response = session.get(f"{VP_PORTAL}/api/workspaces")
    catch_exception(response)
    return response.json()["data"]


##########################################################################################################3


def file_and_event_search(endpoint, query):
    response = session.get(f"{VP_PORTAL}{endpoint}", params={"query": query})
    catch_exception(response)
    return response.json()["data"]


##########################################################################################################3


def get_vp_install_key():
    endpoint = f"{VP_PORTAL}/api/deploy/vp_install_key"
    response = session.get(endpoint)
    catch_exception(response)
    return response.json()["data"]


########################################################################################

def push_integration_check(data):
    session.post(f"{VP_PORTAL}/api/inspection/push", json=data)
    return True


def get_integration_check(policy):
    response = session.get(f"{VP_PORTAL}/api/inspection/get/{policy}")
    return response.json()
