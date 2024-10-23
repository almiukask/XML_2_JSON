from pprint import pprint
import xml.etree.ElementTree as ET
import numpy as np


class LogEntry:
    statuses: tuple = ("WARNING", "INFO", "ERROR")

    logs_counter = 0

    def __init__(self, time_stamp: str, severity: str, message: str):
        if all(
            [
                time_stamp != "",
                isinstance(time_stamp, type("")),
                severity != "",
                isinstance(severity, type("")),
                message != "",
                isinstance(message, type("")),
            ]
        ):
            self.timestamp = self.get_time_stamp(time_stamp)
            self.severity = self.select_severity(severity)
            self.message = message
            print("object contents: ", self.timestamp, self.severity, self.message)
            self.increase_counter()

    def get_time_stamp(self, iso_timestamp: str) -> str:
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
        if severity.upper() in self.statuses:
            return severity.upper()
        else:
            raise ValueError("Severity message is not understood")

    def increase_counter(cls):

        cls.logs_counter += 1


def read_string_from_file(file_name: str):
    with open(file_name, "r", encoding="utf-8") as f:
        read_data = f.read()
    return read_data if read_data != "" else "File is empty"


def get_xml_from_string(xml_file: str) -> ET.Element:

    if xml_file == "File is empty":
        raise ValueError("Check contents of input file as it appears to be empty")
    try:
        read_xml = ET.fromstring(xml_file)
    except Exception as e:
        pprint(f"Parsing failed possible reason: {e}")
    else:
        return read_xml


if __name__ == "__main__":
    f_contents = read_string_from_file("data.xml")
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
        for str in log:

            if str.tag == "timestamp":
                _timestamp = str.text
            elif str.tag == "severity":
                _severity = str.text
            elif str.tag == "message":
                _message = str.text
            else:
                raise ValueError("Unrecognized tag in the XML")

        # print(_timestamp, _severity, _message)
        new_log = LogEntry(_timestamp, _severity, _message)
        logs_dict[new_log.severity].append(new_log)
        print(logs_dict[new_log.severity][LogEntry.logs_counter - 1].message)

    pprint(logs_dict)
