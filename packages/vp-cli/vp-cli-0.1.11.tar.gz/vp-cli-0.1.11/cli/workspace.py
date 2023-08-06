from cli.apiexternal import get_workspaces
from cli.util import Formatter, update_vp_config, get_vp_config


class Workspace:
    @staticmethod
    def list_():
        workspaces = get_workspaces()
        active_workspace = get_vp_config().get("workspace", None)
        headers = ["Active", "Workspace"]
        rows = [
            ["*" if row["name"] == active_workspace else "", row["name"]]
            for row in workspaces
        ]
        return Formatter.table(headers, rows)

    @staticmethod
    def set_(name):
        avaliable_workspaces = set([w["name"] for w in get_workspaces()])
        if name not in avaliable_workspaces:
            raise Exception(
                f'Can\'t set to use workspace "{name}". See vp-cli config get-workspaces.'
            )
        update_vp_config(workspace=name)
        return "Updated!"
