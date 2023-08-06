import os
import logging
import sys
import requests
import subprocess
import base64
import json
import time
import getpass
from paramiko import ssh_exception
from termcolor import colored
from paramiko import client, AutoAddPolicy
from cli.apiexternal import get_vp_install_key
from cli.util import _exec_command_remote, ssh_connect


log = logging.getLogger()


class Collector:
    AGENT_NAME = "vp-collector"
    AGENT_HOME = "/opt/vantagepoint/collector"

    def _deploy_linux(self, hosts=[]):
        log.info("Setting up environment...")
        env = os.environ.copy()
        # get install key
        key = get_vp_install_key()
        env["VP_INSTALL_KEY"] = key
        # get install script
        install_script = requests.get(
            "https://artifactory.build.vantagepoint.co/artifactory/tools/collector-install.sh"
        ).text

        if hosts:
            ssh_client = client.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            for host in hosts:
                log.info(
                    colored(
                        f'Installing collector on "{host}"', "white", attrs=["bold"]
                    )
                )
                _host, port = host.split(":") if ":" in host else (host, 22)
                user, host_name = _host.split("@")
                ssh_connect(ssh_client, user, host_name, port)
                sftp_client = ssh_client.open_sftp()
                _install_script = sftp_client.open("/tmp/vp_collector_install.sh", "w")
                _install_script.write(install_script)
                _install_script.close()
                _exec_command_remote(
                    ssh_client,
                    "chmod +x /tmp/vp_collector_install.sh && /tmp/vp_collector_install.sh",
                    host,
                    env=env,
                )
                self._update_agent_config(
                    vp_install_key=key, host=host, ssh_client=ssh_client
                )
                ssh_client.close()
        else:
            if not sys.platform != "linux":
                raise Exception("OS not supported")

            log.info("Installing collector...")
            with open("/tmp/vp_collector_install.sh", "w") as f:
                f.write(install_script)

            process = subprocess.Popen(
                "chmod +x /tmp/vp_collector_install.sh && /tmp/vp_collector_install.sh",
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                env=env,
            )
            process.wait()

            # update config
            self._update_agent_config(key)

        return "Success!"

    def _deploy_windows(self, hosts=[]):
        raise Exception("OS not supported")

    def _deploy_falco_linux(self, hosts=[]):
        log.info("Setting up environment...")
        env = os.environ.copy()
        # get install key
        key = get_vp_install_key()
        env["VP_INSTALL_KEY"] = key
        # get install script
        install_script = requests.get(
            "https://artifactory.build.vantagepoint.co/artifactory/falco/install.sh"
        ).text

        if hosts:
            ssh_client = client.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            for host in hosts:
                log.info(
                    colored(f'Installing falco on "{host}"', "white", attrs=["bold"])
                )
                _host, port = host.split(":") if ":" in host else (host, 22)
                user, host_name = _host.split("@")
                ssh_connect(ssh_client, user, host_name, port)
                sftp_client = ssh_client.open_sftp()
                _install_script = sftp_client.open("/tmp/vp_falco_install.sh", "w")
                _install_script.write(install_script)
                _install_script.close()
                _exec_command_remote(
                    ssh_client,
                    "chmod +x /tmp/vp_falco_install.sh && /tmp/vp_falco_install.sh",
                    host,
                    env=env,
                )
                ssh_client.close()
        else:
            if not sys.platform != "linux":
                raise Exception("OS not supported")

            log.info("Installing falco...")
            with open("/tmp/vp_falco_install.sh", "w") as f:
                f.write(install_script)

            process = subprocess.Popen(
                "chmod +x /tmp/vp_falco_install.sh && /tmp/vp_falco_install.sh",
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                env=env,
            )
            process.wait()

    def _deploy_falco_windows(self, hosts=[]):
        raise Exception("OS not supported.")

    def _update_agent_config(self, vp_install_key, host=None, ssh_client=None):
        settings_file = f"{Collector.AGENT_HOME}/conf/settings.json"
        customer_id = base64.b64decode(vp_install_key).decode("utf-8").split("::::")[0]
        encryption_key = (
            base64.b64decode(vp_install_key).decode("utf-8").split("::::")[1]
        )
        portal_host = base64.b64decode(vp_install_key).decode("utf-8").split("::::")[2]
        workspace_id = base64.b64decode(vp_install_key).decode("utf-8").split("::::")[3]

        log.info("Updating agent config ...")

        if host:
            sftp_client = ssh_client.open_sftp()
            _config = sftp_client.open(settings_file, "r")
            config = json.loads(_config.read())
        else:
            with open(settings_file, "r") as f:
                config = json.loads(f.read())

        for k, v in {
            "customer_id": customer_id,
            "customer_encryption_key": encryption_key,
            "portal_host": portal_host,
            "workspace_id": workspace_id,
        }.items():
            config[k] = v

        if host:
            _config = sftp_client.open("/tmp/vp_collector_settings.json", "w")
            _config.write(json.dumps(config))
            _config.close()
            _exec_command_remote(
                ssh_client,
                '/bin/bash -c "%s"'
                % (
                    """
                sudo service vp-collector stop
                sleep 5s
                sudo mv /tmp/vp_collector_settings.json %s
                set -x
                sudo service vp-collector start
                        """
                    % (settings_file)
                ),
                host,
            )
        else:
            with open("/tmp/vp_collector_settings.json", "w") as f:
                f.write(json.dumps(config))

            process = subprocess.Popen(
                [
                    "bash",
                    "-c",
                    """
                sudo service vp-collector stop
                sleep 5s
                sudo mv /tmp/vp_collector_settings.json %s
                set -x
                sudo service vp-collector start
                sleep 5s
                    """
                    % (settings_file),
                    Collector.AGENT_NAME,
                ],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            process.wait()

            for line in iter(process.stdout.readline, b""):
                sys.stdout.write(line.decode("utf-8"))

    @staticmethod
    def deploy(os, hosts=[]):
        try:
            deploy = {
                "linux": Collector()._deploy_linux,
                "windows": Collector()._deploy_windows,
            }[os]
        except KeyError:
            raise Exception('Unknown os "{os}"')

        return deploy(hosts)

    @staticmethod
    def deploy_falco(os, hosts=[]):
        try:
            deploy = {
                "linux": Collector()._deploy_falco_linux,
                "windows": Collector()._deploy_falco_windows,
            }[os]
        except KeyError:
            raise Exception('Unknown os "{os}"')

        return deploy(hosts)
