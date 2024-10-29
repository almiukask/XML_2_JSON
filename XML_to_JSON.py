from pprint import pprint
import xml.etree.ElementTree as ET
import copy
import json
from datetime import datetime
from collections import namedtuple
from pathlib import Path

statusesType = namedtuple("Statuses", "warn, info, error")
TIMESTAMP = "timestamp"
SEVERITY = "severity"
MESSAGE = "message"


class LogEntry:

    statuses: tuple = statusesType(warn="WARNING", info="INFO", error="ERROR")

    logs_counter = {
        statuses.warn: 0,
        statuses.info: 0,
        statuses.error: 0,
    }

    def __init__(self, time_stamp: str, severity: str, message: str):
        if all(
            [
                time_stamp,
                isinstance(time_stamp, str),
                self.check_timestamp(time_stamp),
                severity,
                isinstance(severity, str),
                self.is_severity(severity),
                message,
                isinstance(message, str),
            ]
        ):
            self.timestamp = self.get_time_stamp(time_stamp)
            self.severity = severity
            self.message = message
            self.increase_counter(self.severity)

    def check_timestamp(self, timestamp: str) -> bool:
        try:
            _ = self.get_time_stamp(timestamp)
        except:
            return False

        return True

    def get_time_stamp(self, iso_timestamp: str) -> str:
        """
        Parse ISO timestamp and return DD-MM-YYYY HH:MM:SS
        """

        _date = datetime.fromisoformat(iso_timestamp)
        _timestamp = _date.strftime("%d-%m-%Y %H:%M:%S")
        return _timestamp

    def is_severity(self, severity: str) -> bool:
        """
        Check given severity against constant data
        """
        return severity in self.statuses

    @classmethod
    def increase_counter(cls, severity):
        """
        Keep track of number of correctly parsed messages
        """
        cls.logs_counter[severity] += 1

    def get_dict_from_object(self) -> dict:
        """
        Form a dictionary from object contents
        """
        new_dict = {
            TIMESTAMP: self.timestamp,
            SEVERITY: self.severity,
            MESSAGE: self.message,
        }
        return new_dict


def read_string_from_file(file_name: str) -> str:
    """
    Read file contents and return a string
    """

    with open(file_name, "r", encoding="utf-8") as f:
        read_data = f.read()
    return read_data


def write_to_file(f_contents: str, file_name: str, extension: str):
    """
    Write to string to file adding timestamp of creation
    """
    current_time = datetime.now()
    folder_path = Path(__file__).parent / "output"
    try:
        folder_path.mkdir()
    except FileExistsError:
        pass

    _file_name = file_name + "_" + str(current_time.timestamp()) + extension
    _file_path = folder_path / _file_name
    with open(_file_path, "w", encoding="utf-8") as f:
        f.write(f_contents)


def get_xml_from_string(xml_file: str) -> ET.Element:
    """
    Parse string to XML element
    """
    if not xml_file:
        raise ValueError("Check contents of input file as it appears to be empty")
    try:
        read_xml = ET.fromstring(xml_file)
    except Exception as e:
        pprint(f"Parsing failed possible reason: {e}")
    else:
        return read_xml


def handle_and_scan_input_folder() -> list:
    """
    Handles input folder for XMLs to be placed for parsing. If fodler exists retruns list of files
    """
    folder_path = Path(__file__).parent / "input"
    try:
        folder_path.mkdir()
    except FileExistsError:
        pass

    _files = list(folder_path.glob("**/*.xml"))
    if len(_files) < 1:
        raise FileExistsError("No files (XMLs) are present in input folder")
    return _files


if __name__ == "__main__":

    files = handle_and_scan_input_folder()
    file_counter = 0

    for file in files:
        f_contents = read_string_from_file(file)
        xml_tree = get_xml_from_string(f_contents)
        file_counter += 1

        logs_dict = {
            LogEntry.statuses.warn: [],
            LogEntry.statuses.info: [],
            LogEntry.statuses.error: [],
        }
        for log in xml_tree:
            _timestamp = ""
            _severity = ""
            _message = ""
            for _str in log:

                if _str.tag == TIMESTAMP:
                    _timestamp = _str.text
                elif _str.tag == SEVERITY:
                    _severity = _str.text
                elif _str.tag == MESSAGE:
                    _message = _str.text
                else:
                    raise ValueError("Unrecognized tag in the XML")

            prev_log_cnt = copy.copy(LogEntry.logs_counter)
            new_log = LogEntry(_timestamp, _severity, _message)
            if LogEntry.logs_counter != prev_log_cnt:
                logs_dict[new_log.severity].append(new_log.get_dict_from_object())

        for key, value in logs_dict.items():
            json_str = json.dumps({"messages": value}, indent=4)
            write_to_file(json_str, key + "_" + str(file_counter), ".json")
