from abc import ABCMeta, abstractstaticmethod
from cli.apiexternal import file_and_event_search
from cli.util import Formatter


class FileEventSearchMeta(ABCMeta):
    def __new__(cls, name, bases, attr):
        if (
            "FileEventSearch" in [c.__qualname__ for c in bases]
            and "ENDPOINT" not in attr
        ):
            raise AttributeError(f'ENDPOINT not defined for class "{name}"')
        return super().__new__(cls, name, bases, attr)


class FileEventSearch(metaclass=FileEventSearchMeta):
    def search(self, query):
        return self._format_output(file_and_event_search(self.ENDPOINT, query))

    @abstractstaticmethod
    def _format_output(data):
        pass


class CloudLogs(FileEventSearch):
    ENDPOINT = "/api/search/logs/cloud"

    @staticmethod
    def _format_output(data):
        headers = [
            "Id",
            "Aws Region",
            "Event Type",
            "Event Name",
            "Event Time",
            "User Agent",
            "Source IPAddress",
            "Event Source",
            "Event Version",
        ]
        rows = [
            [
                row["meta"]["id"],
                row["awsRegion"],
                row["eventType"],
                row["eventName"],
                row["eventTime"],
                row["userAgent"],
                row["sourceIPAddress"],
                row["eventSource"],
                row["eventVersion"],
            ]
            for row in data["results"]
        ]
        return Formatter.table(headers, rows)


class SysLog(FileEventSearch):
    ENDPOINT = "/api/search/syslog"

    @staticmethod
    def _format_output(data):
        headers = [
            "Id",
            "Host Uuid",
            "Host Name",
            "IPV4 Address",
            "Host OS",
            "Text",
        ]

        rows = [
            [
                row["meta"]["id"],
                row["host_uuid"],
                row["hostname"],
                row["ipv4_addr"],
                row["host_os"],
                (row["text"][:75] + "...") if len(row["text"]) > 75 else row["text"],
            ]
            for row in data["results"]
        ]
        return Formatter.table(headers, rows)


class LogFiles(FileEventSearch):
    ENDPOINT = "/api/search/logs"

    @staticmethod
    def _format_output(data):
        headers = [
            "Id",
            "File",
            "Host UUID",
            "Directory",
            "Date Created",
            "Created By",
            "Last Modified",
        ]

        rows = [
            [
                row["meta"]["id"],
                f"{row['directory']}/{row['file_name']}",
                row["host_uuid"],
                row["directory"],
                row["created_on"],
                row["created_by"],
                row["last_modified_on"],
            ]
            for row in data["results"]
        ]
        return Formatter.table(headers, rows)


class VersionedFiles(FileEventSearch):
    ENDPOINT = "/api/search/versioned"

    @staticmethod
    def _format_output(data):
        headers = [
            "Id",
            "File",
            "Host UUID",
            "Directory",
            "Date Created",
            "Created By",
            "Last Modified",
        ]

        rows = [
            [
                row["meta"]["id"],
                f"{row['directory']}/{row['file_name']}",
                row["host_uuid"],
                row["directory"],
                row["created_on"],
                row["created_by"],
                row["last_modified_on"],
            ]
            for row in data["results"]
        ]
        return Formatter.table(headers, rows)


class WindowsEvents(FileEventSearch):
    ENDPOINT = "/api/search/windows"

    @staticmethod
    def _format_output(data):
        headers = [
            "Id",
            "Generated From",
            "Log Type",
            "Username",
            "User Domain",
            "Message",
            "Host UUID",
            "Host Name",
            "Host OS",
            "OS Version",
            "IPV4 Address",
            "Date Created",
        ]

        rows = [
            [
                row["meta"]["id"],
                row["generated_from"],
                row["log_type"],
                row["username"],
                row["user_domain"],
                (row["message"][:75] + "...").replace("\t", "")
                if len(row["message"]) > 75
                else row["message"].replace("\t", ""),
                row["host_uuid"],
                row["hostname"],
                row["os"],
                row["os_version"],
                row["ipv4_addr"],
                row["created_on"],
            ]
            for row in data["results"]
        ]
        return Formatter.table(headers, rows)
