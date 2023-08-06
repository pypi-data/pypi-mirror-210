import sys
import os
import logging
import itertools
import re
from inspect import getdoc
from contextlib import suppress
from logging.config import fileConfig
from termcolor import colored
from functools import partial

from cli.util import get_version_info
from cli.apiexternal import configure
from cli.docopt_command import DocoptDispatcher, get_docopt_help
from cli.image import Image
from cli.reputation import Reputation
from cli.integration import DockerRegistryIntegration, CloudIntegration
from cli.workspace import Workspace
from cli.agent import Agent
from cli.collector import Collector
from cli.file_event_search import (
    CloudLogs,
    SysLog,
    LogFiles,
    VersionedFiles,
    WindowsEvents,
)
from cli.inspections import file_inspection


log = logging.getLogger()

############################# configure logger  ################################
fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logger.ini"))

logging.addLevelName(
    logging.INFO, colored(f"==>", "cyan", attrs=["bold"]),
)
logging.addLevelName(
    logging.WARNING,
    colored(
        f"[{logging.getLevelName(logging.WARNING).ljust(9)}]", "yellow", attrs=["bold"]
    ),
)
logging.addLevelName(
    logging.ERROR,
    colored(f"[{logging.getLevelName(logging.ERROR).ljust(9)}]", "red", attrs=["bold"]),
)

################################################################################


def main():
    dispatcher = DocoptDispatcher(
        TopLevelCommand, version=get_version_info(), options_first=True
    )
    handler, options = dispatcher.parse(sys.argv[1:])
    handler(TopLevelCommand(), options)


class TopLevelCommand:
    """
    Usage:
        vp-cli [COMMAND] [ARGS...] [OPTIONS]
        vp-cli -h |--help
        vp-cli --version

    Commands:
        image       Image scan services
        registry    Docker registry integrations
        feeds       Reputation feeds
        integration Cloud integrations
        search      File and event search
        deploy      Deploy agent, collector or falco
        uninstall   Uninstall agent and cleanup host
        configure   Configure the cli
        inspection  Infrastructure-as-Code inspection
    """

    def configure(self, options):
        """
        Configure the cli to interact with a the VantagePoint API

        Usage:
            configure

        """
        return configure()

    def image(self, options):
        """
        Image scan services

        Usage:
            image add <registry/repo:tag> [-s=SUBSCRIBE] [-d=<Dockerfile>] [-a=TEXT]
            image (list | ls)
            image analyze <registry/repo:tag> [-d=<Dockerfile>] [-t=TIMEOUT] [-o=OUTPUT_JSON] [-e=EXIT_CODE] [-f]
            image (delete | del) IMAGE_DIGEST [-f=FORCE]

        Options:
            -f, --force                         Force reanalysis of image
            -s, --autosubscribe                 Analyse updates to image tag
            -d, --dockerfile <Dockerfile>       Submit image's docker file for analysis
            -a, --annotations TEXT
            -t, --timeout TIMEOUT               Wait timeout
            -o, --output OUTPUT_JSON            Path to save scan output
            -e, --exit-code EXIT_CODE           Exit code
        """
        if options["add"]:
            command = partial(
                Image.add,
                options["<registry/repo:tag>"],
                options["--dockerfile"],
                options["--force"],
                options["--annotations"],
                options["--autosubscribe"],
            )

        if any([options["list"], options["ls"]]):
            command = Image.list_

        if options["analyze"]:
            with suppress(TypeError):
                options["--timeout"] = float(options["--timeout"])

            command = partial(
                Image.analyze,
                options["<registry/repo:tag>"],
                options["--timeout"] or 3600,
                options["--dockerfile"],
                options["--output"],
                options["--exit-code"],
                options["--force"],
            )

        if any([options["delete"], options["del"]]):
            command = partial(Image.delete, options["IMAGE_DIGEST"])

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def registry(self, options):
        """
        Docker registry integrations

        Usage:
            registry add NAME REGISTRY_ADDRESS REPOSITORY [-u=USERNAME] [-p=PASSWORD] [-t=TYPE] [-x=LOOKUP_TAG]
            registry (list | ls)
            registry (get | describe) ID
            registry edit ID
            registry (delete | del) ID

        Options:
            -u, --username USERNAME              Registry username
            -p, --password PASSWORD              Registry password
            -t, --type TYPE                      Docker registry type (docker_hub|aws|gcr|azure|docker_v2) [default: docker_v2]
            -x, --lookup-tag LOOKUP_TAG          Lookup tag [default: latest]
        """
        if options["add"]:
            command = partial(
                DockerRegistryIntegration.add,
                options["NAME"],
                options["REGISTRY_ADDRESS"],
                options["REPOSITORY"],
                username=options["--username"],
                password=options["--password"],
                type_=options["--type"],
                lookup_tag=options["--lookup-tag"],
            )

        if any([options["list"], options["ls"]]):
            command = partial(DockerRegistryIntegration.list_)

        if any([options["get"], options["describe"]]):
            command = partial(DockerRegistryIntegration.get, id_=options["ID"])

        if options["edit"]:
            command = partial(DockerRegistryIntegration.edit, id_=options["ID"])

        if any([options["delete"], options["del"]]):
            command = partial(DockerRegistryIntegration.delete, id_=options["ID"])

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def feeds(self, options):
        """
        Reputation feeds

        Usage:
            feeds add -f JSON_FILE
            feeds (list | ls)
            feeds (get | describe) ID
            feeds edit ID
            feeds (delete | del) ID

        Options:
            -f, --file JSON_FILE        Path to reputation feeds list JSON file
        """

        if options["add"]:
            command = partial(Reputation.add, json_file=options["--file"])

        if any([options["list"], options["ls"]]):
            command = Reputation.list_

        if any([options["get"], options["describe"]]):
            command = partial(Reputation.get, id_=options["ID"])

        if options["edit"]:
            command = partial(Reputation.edit, id_=options["ID"])

        if any([options["delete"], options["del"]]):
            command = partial(Reputation.delete, id_=options["ID"])

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def integration(self, options):
        """
        Integrations

        Usage:
            integration add NAME -t INTEGRATION_TYPES -p PROVIDER [--aws-role-arn=TEXT] [--flow-log-resource-type=TYPE] [--flow-log-resource-id=TEXT] [--azure-principal=TEXT] [--azure-password=PASSWORD] [--azure-tenant=TEXT]
            integration (list | ls)
            integration (get | describe) ID
            integration (delete | del) ID

        Options:
            -t, --types INTEGRATION_TYPES   Comma separated (security | cloud_log | network | flow_log)
            -p, --provider PROVIDER         Cloud provider (aws | azure)
            --aws-role-arn TEXT             AWS role arn
            --flow-log-resource-type TYPE   AWS flow log resource type (VPC | Subnet | NetworkInterface)
            --flow-log-resource-id TEXT     AWS flow log resource id
            --azure-principal TEXT          Azure principal
            --azure-password PASSWORD       Azure password
            --azure-tenant TEXT             Azure tenant
        """

        if options["add"]:
            command = partial(
                CloudIntegration.add,
                name=options["NAME"],
                provider=options["--provider"],
                types=options["--types"].split(","),
                aws_role_arn=options["--aws-role-arn"],
                flow_log_resource_type=options["--flow-log-resource-type"],
                flow_log_resource_id=options["--flow-log-resource-id"],
                azure_principal=options["--azure-principal"],
                azure_password=options["--azure-password"],
                azure_tenant=options["--azure-tenant"],
            )

        if any([options["list"], options["ls"]]):
            command = CloudIntegration.list_

        if any([options["get"], options["describe"]]):
            command = partial(CloudIntegration.get, id_=options["ID"])

        if any([options["delete"], options["del"]]):
            command = partial(CloudIntegration.delete, id_=options["ID"])

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def config(self, options):
        """
        Modify vp-cli configurations

        Usage:
            config SUBCOMMAND [OPTIONS]

        Subcommands:
            get-workspaces  Lists available workspaces
            set-workspace   Sets user workspace
        """

        if options["SUBCOMMAND"] == "get-workspaces":
            command = Workspace.list_

        elif options["SUBCOMMAND"] == "set-workspace":
            command = partial(Workspace.set_, name=options["OPTIONS"])

        else:
            log.error(
                f"SUBCOMMAND \"{options['SUBCOMMAND']}\" not found. See vp-cli config --help."
            )
            sys.exit(1)

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def search(self, options):
        """
        File and event search

        Usage:
            search <resource> [-q=QUERY]

        Subcommands:
            cloud_logs
            syslog
            logs
            windows_events
            versioned

        Options:
            -q, --query QUERY Search query
        """

        command_help = getdoc(self.search)
        resource = options["<resource>"]
        if resource is None:
            raise SystemExit(command_help)

        if not hasattr(Search, resource):
            print(f'Resource "{resource}" not found \n')
            raise SystemExit(command_help)

        handler = getattr(Search, resource)
        docstring = getdoc(handler)

        get_docopt_help(docstring, resource, options_first=False)

        try:
            print(handler(Search(), options["--query"]))
        except Exception as e:
            log.error(str(e))

    def deploy(self, options):
        """
        Deploy and configure agent, collector and falco

        Usage:
            deploy <resource> (linux | windows) [--computer-list=<user@hostname:port>] [--computer-list-file=<FILE>] [--use-ad] [--ad-ou-dn AD_AD] [--ad-server AD_SERVER] [--use-ssl]

        Resources:
            agent       Client agent
            collector   Client agent collector
            falco       Falco

        Options:
            --computer-list <user@hostname:port> Comma separated list. Computers on which to install agent.
            --use-ad
            --ad-ou-dn AD_AD
            --ad-server AD_SERVER
            --use-ssl
            -f, --computer-list-file <FILE> Computer list file
        """

        hosts = (
            options["--computer-list"].split(",") if options["--computer-list"] else []
        )
        if options["--computer-list-file"]:
            with open(options["--computer-list-file"], "r") as f:
                _hosts = f.read()
            hosts += _hosts.split("\n")

        for host in hosts:
            if not re.match(
                "^(?:(?:[\w.-]+@)(?:[\w-]+)(\.[\w.-]+)?(?::[0-9]{1,5})?)$", host
            ):
                log.error(
                    f'Invalid format "{host}". Host should be of format user@domain:port'
                )
                sys.exit(1)

        if options["<resource>"] == "agent":
            command = partial(
                Agent.deploy,
                "linux" if options["linux"] else "windows",
                hosts=hosts,
                use_ad=options["--use-ad"],
                ad_ou_dn=options["--ad-ou-dn"],
                ad_server=options["--ad-server"],
                use_ssl=options["--use-ssl"],
            )

        if options["<resource>"] == "collector":
            command = partial(
                Collector.deploy,
                "linux" if options["linux"] else "windows",
                hosts=hosts,
            )

        if options["<resource>"] == "falco":
            command = partial(
                Collector.deploy_falco,
                "linux" if options["linux"] else "windows",
                hosts=hosts,
            )

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def uninstall(self, options):
        """
        Uninstall and cleanup agent from host

        Usage:
            uninstall <resource> (linux | windows) [--computer-list=<user@hostname:port>] [--computer-list-file=<FILE>] [--use-ad] [--ad-ou-dn AD_AD] [--ad-server AD_SERVER] [--use-ssl]

        Resources:
            agent       Client agent

        Options:
            --computer-list <user@hostname:port> Comma separated list. Computers on which to install agent.
            --use-ad
            --ad-ou-dn AD_AD
            --ad-server AD_SERVER
            --use-ssl
            -f, --computer-list-file <FILE> Computer list file
        """

        hosts = (
            options["--computer-list"].split(",") if options["--computer-list"] else []
        )
        if options["--computer-list-file"]:
            with open(options["--computer-list-file"], "r") as f:
                _hosts = f.read()
            hosts += _hosts.split("\n")

        for host in hosts:
            if not re.match(
                "^(?:(?:[\w.-]+@)(?:[\w-]+)(\.[\w.-]+)?(?::[0-9]{1,5})?)$", host
            ):
                log.error(
                    f'Invalid format "{host}". Host should be of format user@domain:port'
                )
                sys.exit(1)

        if options["<resource>"] == "agent":
            command = partial(
                Agent.uninstall,
                "linux" if options["linux"] else "windows",
                hosts=hosts,
                use_ad=options["--use-ad"],
                ad_ou_dn=options["--ad-ou-dn"],
                ad_server=options["--ad-server"],
                use_ssl=options["--use-ssl"],
            )

        else:
            raise NotImplemented

        try:
            print(command())
        except Exception as e:
            log.error(str(e))

    def inspection(self, options):
        """
        Static inspection

        Usage:
            inspection POLICY PATH
        """
        status = file_inspection(options["POLICY"], options["PATH"])
        if status is None:
            print(colored("ERROR: NO POLICY OR WRONG PATH", "yellow", attrs=["bold"]))
            exit_code = 1
        elif status:
            print(colored("PASSED!", "green"))
            exit_code = 0
        else:
            print(colored("FAILED", "red"))
            exit_code = 1

        sys.exit(exit_code)


class Search:
    def cloud_logs(self, query=None):
        """
        Search cloud logs

        Usage:
            search cloud_logs [-q=QUERY]

        options:
            -q, --query QUERY   Search query
        """
        return CloudLogs().search(query)

    def syslog(self, query=None):
        """
        Search syslogs

        Usage:
            search syslog [-q=QUERY]

        options:
            -q, --query QUERY Search query
        """
        return SysLog().search(query)

    def logs(self, query=None):
        """
        Search log files

        Usage:
            search logs [-q=QUERY]

        options:
            -q, --query QUERY Search query
        """
        return LogFiles().search(query)

    def windows_events(self, query=None):
        """
        Search windows events

        Usage:
            search windows_events [-q=QUERY]

        options:
            -q, --query QUERY Search query
        """
        return WindowsEvents().search(query)

    def versioned(self, query=None):
        """
        Search integrity monitored files

        Usage:
            search versioned [-q=QUERY]

        options:
            -q, --query QUERY Search query
        """
        return VersionedFiles().search(query)
