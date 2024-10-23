from pprint import pprint
import xml.etree.ElementTree as ET
import numpy as np
import copy
import json
from datetime import datetime


class LogEntry:
    statuses: tuple = ("WARNING", "INFO", "ERROR")

    logs_counter = {
        statuses[0]: 0,
        statuses[1]: 0,
        statuses[2]: 0,
    }

    def __init__(self, time_stamp: str, severity: str, message: str):
        if all(
            [
                time_stamp != "",
                isinstance(time_stamp, str),
                severity != "",
                isinstance(severity, str),
                message != "",
                isinstance(message, str),
            ]
        ):
            self.timestamp = self.get_time_stamp(time_stamp)
            self.severity = self.select_severity(severity)
            self.message = message
            self.increase_counter(self.severity)

    def get_time_stamp(self, iso_timestamp: str) -> str:
        """
        Parse ISO timestamp and return DD-MM-YYYY HH:MM:SS
        """
        _timestamp = ""
        if "T" in iso_timestamp:
            _date, _time = iso_timestamp.split("T")
            if len(_date) == 10:
                try:
                    _years, _months, _days = _date.split("-")
                except Exception as e:
                    pprint(f"Parsing failed possible reason: {e}")
                else:
                    if all([_years.isdigit(), _months.isdigit, _days.isdigit()]):
                        pass
                    else:
                        raise ValueError("Date contains wrong data")
            else:
                raise ValueError("Timestamp is in wrong format")
            if len(_time) == 8:
                try:
                    _hours, _minutes, _seconds = _time.split(":")
                except Exception as e:
                    pprint(f"Parsing failed possible reason: {e}")
                else:
                    if all([_hours.isdigit(), _minutes.isdigit, _seconds.isdigit()]):
                        pass
                    else:
                        raise ValueError("Time contains wrong data")
            else:
                raise ValueError("Timestamp is in wrong format")
        else:
            raise ValueError("Timestamp is in wrong format")
        _timestamp = _days + "-" + _months + "-" + _years + " " + _time
        return _timestamp

    def select_severity(self, severity: str) -> str:
        """
        Check given severity against constant data nad return it
        """
        
        if severity.upper() in self.statuses:
            return severity.upper()
        else:
            raise ValueError("Severity message is not understood")

    @classmethod
    def increase_counter(cls, severity):
        """
        Keep track of number of correctly parsed messages
        """
        cls.logs_counter[severity] += 1

    def get_dict_from_object(self) -> dict:
        new_dict = {
            "timestamp": self.timestamp,
            "severity": self.severity,
            "message": _message,
        }
        return new_dict


def read_string_from_file(file_name: str) -> str:
    """
    Read file contents and return string
    """
  
    with open(file_name, "r", encoding="utf-8") as f:
        read_data = f.read()
    return read_data if read_data != "" else "File is empty"


def wite_to_file(f_contents: str, file_name, extension):
    """
    Write to string to file adding timestamp of creation
    """
    current_time = datetime.now()
    _file_name = file_name + "_" + str(current_time.timestamp()) + extension
    with open(_file_name, "w", encoding="utf-8") as f:
        f.write(f_contents)


def get_xml_from_string(xml_file: str) -> ET.Element:
    """
    Parse string to XML element
    """
    if xml_file == "File is empty":
        raise ValueError("Check contents of input file as it appears to be empty")
    try:
        read_xml = ET.fromstring(xml_file)
    except Exception as e:
        pprint(f"Parsing failed possible reason: {e}")
    else:
        return read_xml


if __name__ == "__main__":
    f_contents = read_string_from_file("data_negative.xml")
    xml_tree = get_xml_from_string(f_contents)

    logs_dict = {
        LogEntry.statuses[0]: [],
        LogEntry.statuses[1]: [],
        LogEntry.statuses[2]: [],
    }
    for log in xml_tree:
        _timestamp = ""
        _severity = ""
        _message = ""
        for _str in log:

            if _str.tag == "timestamp":
                _timestamp = _str.text
            elif _str.tag == "severity":
                _severity = _str.text
            elif _str.tag == "message":
                _message = _str.text
            else:
                raise ValueError("Unrecognized tag in the XML")

        prev_log_cnt = copy.copy(LogEntry.logs_counter)
        new_log = LogEntry(_timestamp, _severity, _message)
        if LogEntry.logs_counter != prev_log_cnt:
            logs_dict[new_log.severity].append(new_log.get_dict_from_object())

    for key, value in logs_dict.items():
        json_str = json.dumps(value, indent=3)
        wite_to_file(json_str, key, ".json")
