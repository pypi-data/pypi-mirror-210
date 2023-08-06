import os
import json
import shutil
import itertools
import base64
import dateparser
import subprocess
import tempfile
import time
import getpass
import configparser
import stat
import logging
from pathlib import Path
from io import StringIO
from activedirectory import ActiveDirectory
from paramiko import ssh_exception
from pypsrp.client import Client as WinClient
from contextlib import contextmanager
from codecs import encode
from datetime import datetime
from cli.consts import VP_CLI_VERSION, VP_CLI_DEFAULT_EDITOR
from termcolor import colored
from texttable import Texttable

CREDENTIALS_FILE = f"{Path.home()}/.vantagepoint/config"

log = logging.getLogger()

def get_version_info():
    return f"vp_cli version {VP_CLI_VERSION}"


def get_vp_config():
    config = configparser.ConfigParser()
    config.read(CREDENTIALS_FILE)
    VP_TOKEN = config.get("default", "token")
    VP_SECRET_KEY = config.get("default", "secret_key")
    VP_PORTAL = config.get("default", "portal")
    VP_WORKSPACE = config.get("default", "workspace", fallback=None)
    return {
        "token": VP_TOKEN,
        "secret_key": VP_SECRET_KEY,
        "portal": VP_PORTAL,
        "workspace": VP_WORKSPACE,
    }


def ssh_connect(ssh_client, username, host_name, port):
    success = False
    password = None
    password_tries = 3
    passphrase = None

    def _connect(host_name, port, username):
        nonlocal password
        nonlocal passphrase
        ssh_client.connect(
            host_name,
            port=port,
            username=username,
            password=password,
            passphrase=passphrase,
        )

    while not success and password_tries > 0:
        try:
            _connect(host_name, port, username)
            break
        except ssh_exception.PasswordRequiredException as e:
            print(e)
            passphrase = getpass.getpass()
        except ssh_exception.AuthenticationException as e:
            password = getpass.getpass(
                f"Password for {username}@{host_name} ({password_tries} tries left): "
            )
            password_tries -= 1
    else:
        raise ssh_exception.AuthenticationException


def _exec_command_remote(ssh_client, command, host, env=None):
    transport = ssh_client.get_transport()
    chan = transport.open_session()
    chan.get_pty()
    stdin = chan.makefile("wb", -1)
    chan.setblocking(0)
    if env:
        chan.update_environment(env)
    chan.exec_command(command)
    while True:
        while chan.recv_ready():
            o = chan.recv(1000).decode("utf-8")
            print(o)
            if "[sudo] password for" in o:
                password = getpass.getpass()
                stdin.write(f"{password}\n")
                stdin.flush()
        while chan.recv_stderr_ready():
            print(chan.recv_stderr(1000).decode("utf-8"))
        if chan.exit_status_ready():
            break
        time.sleep(1)

    retcode = chan.recv_exit_status()
    if retcode != 0:
        raise Exception(f'Failed to installl agent on host "{host}"')


def _win_get_computer_list_ad(base_dn, ad_domain, username, password, use_ssl=False):
    ldap = "LDAP" if not use_ssl else "LDAPS"
    if ad_domain and base_dn:
        ldap_url = f"{ldap}://{ad_domain}/{base_dn}"
    elif ad_domain:
        ldap_url = f"{ldap}://{ad_domain}"
    elif base_dn:
        ldap_url = f"{ldap}://{base_dn}"
    else:
        ldap_url = ""

    log.debug("LDAP url is %s" % (ldap_url))

    ad = (
        ActiveDirectory(ldap_url)
        if not username or not password
        else ActiveDirectory(ldap_url, dn=username, secret=password)
    )
    return [
        str(computer.dNSHostName)
        for computer in ad.search_ext_s(filterstr="(&(objectClass=computer))")
    ]


def _win_execute_on_computer(
    computer_name,
    username,
    password,
    install_script_url,
    vp_install_key,
    port,
    use_ssl=False,
):
    log.info(f'Installing agent on "{computer_name}"')
    with WinClient(
        computer_name, username=username, password=password, port=port, ssl=use_ssl
    ) as client:

        output, streams, had_errors = client.execute_ps(
            """
        Set-ExecutionPolicy Bypass -Scope Process -Force; ((New-Object System.Net.WebClient).DownloadString('%s')) | Out-File $env:temp\\vantagepoint_installer.ps1; cd $env:temp; .\\vantagepoint_installer.ps1 -VPInstallKey %s
        cd 'C:\Program Files\\VantagePoint\\bin'; .\\nssm.exe start vantagepoint
                """
            % (install_script_url, vp_install_key)
        )

    if had_errors:
        for error in streams.error:
            print(error.message)
    if output:
        print(output)

def _win_uninstall_vp_agent(
    computer_name,
    username,
    password,
    uninstall_script_url,
    port,
    use_ssl=False,
):
    log.info(f'Uninstalling agent on "{computer_name}"')
    with WinClient(
        computer_name, username=username, password=password, port=port, ssl=use_ssl
    ) as client:

        output, streams, had_errors = client.execute_ps(
            """
        Set-ExecutionPolicy Bypass -Scope Process -Force; ((New-Object System.Net.WebClient).DownloadString('%s')) | Out-File $env:temp\\vantagepoint_uninstaller.ps1; cd $env:temp; .\\vantagepoint_uninstaller.ps1
                """
            % (uninstall_script_url)
        )

    if had_errors:
        for error in streams.error:
            print(error.message)
    if output:
        print(output)




def update_vp_config(**kwargs):
    _config = get_vp_config()
    for k, v in kwargs.items():
        _config[k] = v
    config = configparser.ConfigParser()
    config.readfp(StringIO("[default]"))

    for k, v in _config.items():
        config.set("default", k, v)
    with open(CREDENTIALS_FILE, "w+") as configfile:
        config.write(configfile)

    os.chmod(CREDENTIALS_FILE, stat.S_IRUSR | stat.S_IWUSR)


class Formatter:
    @staticmethod
    def table(headers, rows):
        term_width, _ = shutil.get_terminal_size(fallback=(100, 0))
        table = Texttable(max_width=term_width)
        table.add_rows([headers] + rows)
        table.set_cols_dtype(["t" for _ in headers])
        table.set_deco(Texttable.HEADER)
        table.set_chars(["-", "|", "+", "-"])
        return table.draw() + "\n"

    @staticmethod
    def image_evaluation(evaluation):
        latest_evaluation = next(iter(evaluation.values()))[0]
        problems_found = latest_evaluation["detail"]["result"]["evaluation_problems"]
        result = next(iter(latest_evaluation["detail"]["result"]["result"].values()))[
            "result"
        ]
        if result["final_action"] == "warn":
            result["final_action"] = colored(result["final_action"].upper(), "yellow")

        _formatted = f"""
Image Digest:       {latest_evaluation['detail']['result']['image_digest']}
Status:             {latest_evaluation['status']}
Last Analysis:      {latest_evaluation['last_evaluation']}
Policy:             {latest_evaluation['detail']['policy']['comment']}
Tag:                {latest_evaluation['detail']['result']['tag']}

Scan results:

{Formatter.table(result['header'], result['rows'])}

---------------------------
Final action:       {result['final_action']}
{len(problems_found)} Problems found
        """

        return _formatted

    @staticmethod
    def integration(data):
        return json.dumps(data, indent=4)

    @staticmethod
    def reputation(data):
        risk_levels = ["Informational", "Low", "Medium", "High", "Critical"]
        reputation = data
        reputation["id"] = reputation["id"]
        reputation["risk_score"] = risk_levels[reputation["risk_score"]]
        if reputation["type"] == "DYNAMIC":
            reputation.update({"url": reputation["source"]})
            del reputation["entries"]
        del reputation["source"]
        return json.dumps(reputation, indent=4)


def loadjson_schema(name, version="v1"):
    schema_dir = os.path.join(
        os.path.dirname(__file__), "schemas", f"{name}_schema_{version}.json"
    )
    with open(schema_dir, "r") as f:
        schema = json.load(f)
    return schema


@contextmanager
def edit_entry(entry, suffix=None):
    f = tempfile.NamedTemporaryFile(suffix=suffix)
    f.write(str.encode(entry))
    f.seek(0)
    subprocess.Popen([VP_CLI_DEFAULT_EDITOR, f.name]).wait()
    yield f
    f.close()


def pretty_date(time):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.utcnow()
    if isinstance(time, int):
        time = datetime.fromtimestamp(time)
    else:
        time = dateparser.parse(time)

    diff = now - time.replace(tzinfo=None)  # Assuming that time is UTC
    is_past = True if diff.total_seconds() > 0 else False

    second_diff = abs(diff.seconds)
    day_diff = abs(diff.days)
    if day_diff < 0 and is_past:
        return "just now"

    if day_diff == 0:
        if second_diff < 10:
            return "%s now" % ("just" if is_past else "from")
        if second_diff < 60:
            return str(second_diff) + " seconds %s" % ("ago" if is_past else "from now")
        if second_diff < 120:
            return "a minute %s" % ("ago" if is_past else "from now")
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour %s" % ("ago" if is_past else "from now")
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours %s" % (
                "ago" if is_past else "from now"
            )
    if day_diff == 1:
        return "%s" % ("Yesterday" if is_past else "Tomorrow")
    if day_diff < 7:
        return str(day_diff) + " days %s" % ("ago" if is_past else "from now")
    if day_diff < 31:
        return str(day_diff // 7) + " %s %s" % (
            "weeks" if day_diff > 1 else "week",
            "ago" if is_past else "from now",
        )
    if day_diff < 365:
        return str(day_diff // 30) + " %s %s" % (
            "months" if (day_diff // 30) > 1 else "month",
            "ago" if is_past else "from now",
        )
    return str(day_diff // 365) + " %s %s" % (
        "years" if (day_diff // 365) > 1 else "year",
        "ago" if is_past else "from now",
    )


spinner = itertools.cycle(["-", "/", "|", "\\"])
