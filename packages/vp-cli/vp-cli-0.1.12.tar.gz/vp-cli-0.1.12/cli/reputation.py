import os
import json
import tempfile
import subprocess
import json
from jsonschema.validators import Draft4Validator
from cli.apiexternal import (
    get_reputation_feeds,
    add_reputation_feed,
    update_reputaiton_feed,
    delete_reputation_feed,
)
from cli.util import Formatter, loadjson_schema, pretty_date, edit_entry

class Reputation:
    def validate(self, json_file):
        schema = loadjson_schema("reputation")
        validator = Draft4Validator(schema=schema)

        with open(json_file, "r") as f:
            feeds = json.load(f)

        errors = [e.message for e in validator.iter_errors(instance=feeds)]
        if errors:
            raise Exception(
                "\n".join([f'Failed to validate "{json_file}" \n'] + errors)
            )

        return feeds

    @classmethod
    def add(cls, json_file):
        feeds = cls().validate(json_file)

        failed = []
        for feed in feeds["reputation_feeds"]:
            feed["entries"] = ",".join(feed.get("entries", []))
            added = add_reputation_feed(feed)
            if not added:
                failed.append(feed["name"])

        return f"Added {len(feeds) - len(failed)} entries! {len(failed)} failed"

    @staticmethod
    def list_():
        feeds = get_reputation_feeds()
        headers = [
            "Id",
            "Name",
            "Source",
            "Type",
            "Number of indicators",
            "Risk score",
            "Last updated",
            "Status",
        ]

        risk_levels = ["Informational", "Low", "Medium", "High", "Critical"]
        rows = [
            [
                feed["id"],
                feed["name"],
                feed["source"],
                feed["type"],
                feed["number_of_indicators"],
                risk_levels[feed["risk_score"]],
                pretty_date(feed["last_updated"]),
                "Ok"
                if feed["number_of_indicators"] > 0
                else (
                    "No indicators" if feed["number_of_indicators"] == 0 else "Error"
                ),
            ]
            for feed in feeds
        ]
        return Formatter.table(headers, rows)

    @staticmethod
    def get(id_):
        feed = get_reputation_feeds(id_=id_)[0]
        return Formatter.reputation(feed)

    @staticmethod
    def edit(id_):
        feed_formated = json.loads(Formatter.reputation(get_reputation_feeds(id_=id_)[0]))
        for key in ("last_updated", "number_of_indicators", "error"):
            del feed_formated[key]

        with edit_entry(json.dumps(feed_formated, indent=4), suffix=".json") as f:
            edited = json.load(f)

        if edited == feed_formated:
            return "No changes detected!"

        updated = update_reputaiton_feed(id_, edited)
        if updated:
            return "Updated!"
        else:
            raise Exception("Failed!")

    @staticmethod
    def delete(id_):
        return delete_reputation_feed(id_)
