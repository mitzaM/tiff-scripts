import os
import logging
from datetime import datetime

cwd = os.getcwd()

CINEMA_CODES_PATH = os.path.join(cwd, "cinema_codes")
FILES_DONE_PATH = os.path.join(cwd, "files_done")
OUTPUT_CSV_PATH = os.path.join(cwd, "output.csv")
LOG_FILE_PATH = os.path.join(cwd, "info.log")
XML_PATH = os.path.join(cwd, "xml")

ALLOW_START = datetime(year=2017, month=5, day=1)
ALLOW_END = datetime(year=2017, month=6, day=30)
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_PRETTY = "%A, %d %B - %X"
CSV_FIELDS = ["Title", "Cinema", "Start Date", "End Date"]
XML_TAGS = ["ContentTitleText", "AnnotationText",
            "ContentKeysNotValidBefore", "ContentKeysNotValidAfter"]
AVAILABILITY_ERROR_MSG = (
    "Cannot run, out of availability date ({} - {}).\n\n".format(
        datetime.strftime(ALLOW_START, format="%d %B %Y"),
        datetime.strftime(ALLOW_END, format="%d %B %Y")))

logging.basicConfig(filename=LOG_FILE_PATH, filemode='a+',
                    format="%(message)s", level=logging.INFO)
