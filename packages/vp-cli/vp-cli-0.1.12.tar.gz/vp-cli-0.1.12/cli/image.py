import sys
import logging
import time
import json
from termcolor import colored
from cli.util import Formatter, spinner, pretty_date
from cli.integration import IntegrationTypes

from cli.apiexternal import (
    get_integrations,
    add_registry,
    get_images,
    add_image,
    delete_image,
    get_image_vulnerabilities,
    evaluate_image,
)

log = logging.getLogger()


class Image:
    @staticmethod
    def add(
        input_image, dockerfile=None, force=False, annotations="", autosubscribe=False
    ):
        registry = input_image.split("/")[0]
        integrations = get_integrations(type_=IntegrationTypes.DOCKER_REGISTRY)

        for integration in integrations:
            if registry != integration["address"]:
                continue

            if integration["status"] == "ACTIVE":
                break
            else:
                log.warn(
                    f"Integration \"{integration['name']}\" is still in {integration['status']} state. Images that require authorisation may fail."
                )
                break

        else:  # no-break
            log.warn(
                f'No integration for registry "{registry}" found. Images that require authorisation may fail.'
            )

        added = add_image(input_image, dockerfile, force, annotations, autosubscribe)

        return added

    @staticmethod
    def list_():
        images = get_images()
        headers = ["Image Tag(s)", "Image Digest", "Status", "Added", "Last Updated"]
        rows = [
            [
                f"{img['registry']}/{img['repo']}:{img['tag']}",
                img["digest"],
                img["analysis_status"],
                pretty_date(img["created_at"]),
                pretty_date(img["last_updated"]),
            ]
            for img in images
        ]
        return Formatter.table(headers, rows)

    @staticmethod
    def analyze(
        input_image, timeout, dockerfile=None, output=None, exit_code=None, force=False
    ):
        log.info(f'Analysing image "{input_image}" ...')
        tag = input_image.split(":")[-1]

        image = get_images(input_image)
        if not image or force:
            log.info(f'Adding image "{input_image}"')
            Image.add(input_image, dockerfile, force)
            image = get_images(input_image)
        else:
            if dockerfile:
                log.warn("Skipping docker file, image already exists")

        while timeout > 0:
            image = get_images(input_image)
            status = image["analysis_status"]
            if status == "analysing":
                continue
            elif status == "analysis_failed":
                raise Exception("Analysis failed")
            elif status == "analyzed":
                break
            time.sleep(3)
            timeout -= 3
        else:  # no-break
            raise Exception("Operation timed out")

        evaluation, status = evaluate_image(image["imageDigest"], tag)
        log.info("Finished analysing image")
        print(Formatter.image_evaluation(evaluation))

        if output:
            with open(output, "w") as f:
                f.write(json.dumps(evaluation, indent=2))

        if status == "pass":
            print(colored("PASSED!", "green"))
            if not exit_code:
                exit_code = 0
        else:
            print(colored("FAILED", "red"))
            if not exit_code:
                exit_code = 1

        sys.exit(exit_code)

    @staticmethod
    def delete(input_image, force=True):
        return delete_image(input_image, force)
