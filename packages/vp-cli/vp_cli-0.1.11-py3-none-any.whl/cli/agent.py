import os
import logging
import sys
import requests
import subprocess
import base64
import json
import time
import getpass
import tempfile
from functools import partial
from termcolor import colored
from paramiko import client, AutoAddPolicy
from cli.apiexternal import get_vp_install_key
from cli.util import (
    ssh_connect,
    _exec_command_remote,
    _win_execute_on_computer,
    _win_uninstall_vp_agent,
    _win_get_computer_list_ad,
)


log = logging.getLogger()


class Agent:
    AGENT_NAME = "vp-agent"
    AGENT_HOME = "/opt/vantagepoint"

    def _deploy_linux(self, hosts=[], username=None, password=None):
        log.info("Setting up environment...")
        env = os.environ.copy()
        # get install key
        key = get_vp_install_key()
        env["VP_INSTALL_KEY"] = key
        # get install script
        install_script = requests.get(
            "https://artifactory.build.vantagepoint.co/artifactory/tools/client-agent-install.sh"
        ).text

        if hosts:
            ssh_client = client.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            for host in hosts:
                log.info(
                    colored(f'Installing agent on "{host}"', "white", attrs=["bold"])
                )
                _host, port = host.split(":") if ":" in host else (host, 22)
                user, host_name = _host.split("@")
                ssh_connect(ssh_client, user, host_name, port)
                sftp_client = ssh_client.open_sftp()
                _install_script = sftp_client.open("/tmp/vp_agent_install.sh", "w")
                _install_script.write(install_script)
                _install_script.close()
                _exec_command_remote(
                    ssh_client,
                    "chmod +x /tmp/vp_agent_install.sh && /tmp/vp_agent_install.sh",
                    host,
                    env=env,
                )
                self._update_agent_config(
                    vp_install_key=key, host=host, ssh_client=ssh_client
                )
                ssh_client.close()

        else:
            if sys.platform != "linux":
                raise Exception("OS not supported")

            log.info("Installing agent...")
            with open("./vp_agent_install.sh", "w") as f:
                f.write(install_script)

            os.chmod("./vp_agent_install.sh", 755)
            process = subprocess.Popen(
                "sudo ./vp_agent_install.sh",
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                env=env,
            )

            process.wait()

            # update config
            self._update_agent_config(key)

        return "Success!"

    def _uninstall_linux(self, hosts=[], username=None, password=None):
        log.info("Setting up environment...")
        uninstall_script = requests.get(
            "https://artifactory.build.vantagepoint.co/artifactory/tools/client-agent-uninstall.sh"
        ).text

        if hosts:
            ssh_client = client.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            for host in hosts:
                log.info(
                    colored(
                        f'Uninstalling agent from "{host}"', "white", attrs=["bold"]
                    )
                )
                _host, port = host.split(":") if ":" in host else (host, 22)
                user, host_name = _host.split("@")
                ssh_connect(ssh_client, user, host_name, port)
                sftp_client = ssh_client.open_sftp()
                _install_script = sftp_client.open("/tmp/vp_agent_uninstall.sh", "w")
                _install_script.write(uninstall_script)
                _install_script.close()
                _exec_command_remote(
                    ssh_client,
                    "chmod +x /tmp/vp_agent_uninstall.sh && /tmp/vp_agent_uninstall.sh",
                    host,
                )
                ssh_client.close()

        else:
            if sys.platform != "linux":
                raise Exception("OS not supported")

            log.info("Installing agent...")
            with open("./vp_agent_uninstall.sh", "w") as f:
                f.write(uninstall_script)

            os.chmod("./vp_agent_uninstall.sh", 755)
            process = subprocess.Popen(
                "sudo ./vp_agent_uninstall.sh",
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            process.wait()

        return "Successfully uninstalled agent from host!"

    def _update_agent_config(self, vp_install_key, host=None, ssh_client=None):
        settings_file = f"{Agent.AGENT_HOME}/conf/settings.json"
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
            _config = sftp_client.open("/tmp/vp_agent_settings.json", "w")
            _config.write(json.dumps(config))
            _config.close()
            _exec_command_remote(
                ssh_client,
                '/bin/bash -c "%s"'
                % (
                    """
                sudo systemctl stop vp-agent
                sleep 5s
                sudo mv /tmp/vp_agent_settings.json %s
                set -x
                sudo systemctl start vp-agent
                        """
                    % (settings_file)
                ),
                host,
            )
        else:
            with open("./vp_agent_settings.json", "w") as f:
                f.write(json.dumps(config))

            process = subprocess.Popen(
                [
                    "bash",
                    "-c",
                    """
                sudo systemctl stop vp-agent
                sleep 5s
                sudo mv ./vp_agent_settings.json %s
                set -x
                sudo systemctl start vp-agent
                    """
                    % (settings_file),
                    Agent.AGENT_NAME,
                ],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

            process.wait()

            for line in iter(process.stdout.readline, b""):
                sys.stdout.write(line.decode("utf-8"))

    def _deploy_windows(
        self, hosts=[], use_ad=False, ad_server=None, ad_ou_dn=None, use_ssl=False
    ):
        log.info("Setting up environment...")
        env = os.environ.copy()
        # get install key
        key = get_vp_install_key()
        env["VP_INSTALL_KEY"] = key
        # get install script
        install_script_url = "https://artifactory.build.vantagepoint.co/artifactory/tools/client-agent-install.ps1"
        install_script = requests.get(install_script_url).text

        if use_ad or hosts:
            password = getpass.getpass()

            if use_ad:
                ad_user = input("AD user: ")

        if use_ad:
            log.info("Getting computer list from domain")
            l = _win_get_computer_list_ad(
                base_dn=ad_ou_dn,
                ad_domain=ad_server,
                username=ad_user,
                password=password,
            )
            hosts.append(f"{username}@{computer}" for computer in l)
        if hosts:
            for h in hosts:
                username, computer = h.split("@")
                computer = computer.split(":")
                computer_name, port = (
                    computer[0],
                    computer[1] if len(computer) > 1 else 5985,
                )
                _win_execute_on_computer(
                    computer_name,
                    username,
                    password,
                    install_script_url,
                    port=port,
                    vp_install_key=key,
                )
        else:
            if not sys.platform.startswith("win"):
                raise Exception("OS not supported")
            log.info("Installing agent...")
            with tempfile.TemporaryDirectory() as td:
                fname = os.path.join(td, "vp_agent_install.ps1")
                with open(fname, "w") as f:
                    f.write(install_script)

                process = subprocess.Popen(
                    ["powershell.exe", fname, "-VPInstallKey", key],
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    env=env,
                )
                process.wait()

            for line in iter(process.stdout.readline, b""):
                sys.stdout.write(line.decode("utf-8"))

    def _uninstall_windows(
        self, hosts=[], use_ad=False, ad_server=None, ad_ou_dn=None, use_ssl=False
    ):
        log.info("Setting up environment...")
        # get uninstall script
        uninstall_script_url = "https://artifactory.build.vantagepoint.co/artifactory/tools/client-agent-uninstall.ps1"
        uninstall_script = requests.get(uninstall_script_url).text

        if use_ad or hosts:
            password = getpass.getpass()

            if use_ad:
                ad_user = input("AD user: ")

        if use_ad:
            log.info("Getting computer list from domain")
            l = _win_get_computer_list_ad(
                base_dn=ad_ou_dn,
                ad_domain=ad_server,
                username=ad_user,
                password=password,
            )
            hosts.append(f"{username}@{computer}" for computer in l)
        if hosts:
            for h in hosts:
                username, computer = h.split("@")
                computer = computer.split(":")
                computer_name, port = (
                    computer[0],
                    computer[1] if len(computer) > 1 else 5985,
                )
                _win_uninstall_vp_agent(
                    computer_name,
                    username,
                    password,
                    uninstall_script_url,
                    port=port,
                )
        else:
            if not sys.platform.startswith("win"):
                raise Exception("OS not supported")
            log.info("Installing agent...")
            with tempfile.TemporaryDirectory() as td:
                fname = os.path.join(td, "vp_agent_uninstall.ps1")
                with open(fname, "w") as f:
                    f.write(uninstall_script)

                process = subprocess.Popen(
                    ["powershell.exe", fname],
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )
                process.wait()

            for line in iter(process.stdout.readline, b""):
                sys.stdout.write(line.decode("utf-8"))

    @staticmethod
    def deploy(os, hosts, use_ad, ad_server, ad_ou_dn, use_ssl):
        try:
            deploy = {
                "linux": partial(Agent()._deploy_linux, hosts),
                "windows": partial(
                    Agent()._deploy_windows, hosts, use_ad, ad_server, ad_ou_dn, use_ssl
                ),
            }[os]
        except KeyError:
            raise Exception('Unknown os "{os}"')

        return deploy()

    @staticmethod
    def uninstall(os, hosts, use_ad, ad_server, ad_ou_dn, use_ssl):
        try:
            func = {
                "linux": partial(Agent()._uninstall_linux, hosts),
                "windows": partial(
                    Agent()._uninstall_windows,
                    hosts,
                    use_ad,
                    ad_server,
                    ad_ou_dn,
                    use_ssl,
                ),
            }[os]
        except KeyError:
            raise Exception('Unknown os "{os}"')

        return func()
