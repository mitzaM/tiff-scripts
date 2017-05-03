import os
import re
import csv
from datetime import datetime

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

CINEMA_CODES_PATH = os.path.join(os.getcwd(), "cinema_codes")
FILES_DONE_PATH = os.path.join(os.getcwd(), "files_done")
OUTPUT_CSV_PATH = os.path.join(os.getcwd(), "output.csv")
XML_PATH = os.path.join(os.getcwd(), "XML")

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_PRETTY = "%A, %d %B - %X"
CSV_FIELDS = ["Title", "Cinema", "Start Date", "End Date"]
XML_TAGS = ["ContentTitleText", "AnnotationText", "ContentKeysNotValidBefore", "ContentKeysNotValidAfter"]

def _get_cinema_codes(filename):
    if not filename or not os.path.exists(filename):
        print("File with cinema codes not found!")
        return {}
    
    with open(filename) as f:
        codes = [line.rstrip('\n').split(" - ") for line in f]
    return {code: location for location, code in codes}

CINEMAS = _get_cinema_codes(CINEMA_CODES_PATH)

def _rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def _get_date(date_string, xml_tag):
    if not date_string:
        print("{} not found.".format(xml_tag))
        return None
    try:
        dt = datetime.strptime(_rreplace(date_string, ":", "", 1), DATE_FORMAT)
        dt = dt.astimezone(tz=None)
        return datetime.strftime(dt, DATE_PRETTY)
    except ValueError:
        print("Couldn't parse {} {}.".format(xml_tag, date_string))
        return date_string

def _get_code(annotation_text, xml_tag):
    if not annotation_text:
        print("{} not found.".format(xml_tag))
        return None

    regexes = list(CINEMAS.keys())
    combined = "({})".format(")|(".join(regexes))
    code_re = re.search(combined, annotation_text, re.IGNORECASE)
    if code_re:
        return CINEMAS.get(code_re.group(0).upper(), code_re.group(0))
    else:
        print("Couldn't find cinema code in {}.".format(annotation_text))
        return None

def _get_parsed_files(filename):
    if not filename or not os.path.exists(filename):
        return []
    
    with open(filename) as f:
        done = [line.rstrip('\n') for line in f]
    return done

def _set_parsed_files(filename, new_files):
    if not filename or not new_files:
        return
    
    with open(filename, 'a+') as f:
        for fname in new_files:
            f.write(fname + '\n')
    t = "file" if len(new_files) == 1 else "files"
    print("Parsed {} new {}.".format(len(new_files), t))

def _write_to_csv(filename, parsed):
    if not filename:
        return
    
    header = False if os.path.exists(filename) else True
    with open(filename, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        header and writer.writeheader()
        for entry in parsed:
            writer.writerow(entry)

def parse(filename):
    print('^' * 100)
    print("Parsing {}".format(filename))

    result = {key: None for key in CSV_FIELDS}
    tree = ET.ElementTree(file=os.path.join(XML_PATH, filename))

    for e in tree.getroot().iter():
        if XML_TAGS[0] in e.tag:
            result[CSV_FIELDS[0]] = e.text
            if not e.text:
                print("{} not found.".format(XML_TAGS[0]))
        elif XML_TAGS[1] in e.tag:
            result[CSV_FIELDS[1]] = _get_code(e.text, XML_TAGS[1])
        elif XML_TAGS[2] in e.tag:
            result[CSV_FIELDS[2]] = _get_date(e.text, XML_TAGS[2])
        elif XML_TAGS[3] in e.tag:
            result[CSV_FIELDS[3]] = _get_date(e.text, XML_TAGS[3])

    print('.' * 100)
    return result


if __name__ == "__main__":
    done = _get_parsed_files(FILES_DONE_PATH)
    new_files, parsed = [], []
    
    for filename in os.listdir(XML_PATH):
        if filename.lower().endswith(".xml") and filename not in done:
            p = parse(filename)
            parsed.append(p)
            new_files.append(filename)

    _set_parsed_files(FILES_DONE_PATH, new_files)
    _write_to_csv(OUTPUT_CSV_PATH, parsed)
