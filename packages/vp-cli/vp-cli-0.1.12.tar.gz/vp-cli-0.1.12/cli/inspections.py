import orjson
import os

from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.runner_filter import RunnerFilter
from checkov.common.util.banner import banner as checkov_banner
from checkov.main import DEFAULT_RUNNERS

from cli.apiexternal import get_integration_check, push_integration_check


def file_inspection(policy_name, path):
    policy = get_integration_check(policy_name)
    if "error" in policy:
        return

    checks = policy["checks"] if "all" not in policy["checks"] else None
    skip_checks = policy["skip_checks"] if policy["skip_checks"] != [""] else None

    runner_filter = RunnerFilter(
        framework="all", checks=checks, skip_checks=skip_checks
    )
    runner_registry = RunnerRegistry(
        checkov_banner,
        runner_filter,
        *DEFAULT_RUNNERS,
    )
    if os.path.isdir(path):
        scan_reports = runner_registry.run(root_folder=path)
    elif os.path.isfile(path):
        scan_reports = runner_registry.run(files=[path])
    else:
        return

    report_jsons = []
    for report in scan_reports:
        report_jsons.append(report.get_dict())
    
    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError


    if len(report_jsons) == 1:
        push_integration_check(
            {
                "scan": orjson.dumps(report_jsons[0], default=set_default).decode(),
                "policy_id": policy["id"],
                "result": len(report_jsons[0]["results"]["failed_checks"]) <= 0,
            }
        )
        return len(report_jsons[0]["results"]["failed_checks"]) <= 0
    else:
        push_integration_check(
            {
                "scan": orjson.dumps(report_jsons, default=set_default).decode(),
                "policy_id": policy["id"],
                "result": all(
                    [
                        len(report["results"]["failed_checks"]) <= 0
                        for report in report_jsons
                    ]
                ),
            }
        )
        return all(
            [len(report["results"]["failed_checks"]) <= 0 for report in report_jsons]
        )
