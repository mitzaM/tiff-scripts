import csv
import re

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from config import *


def _rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_cinema_codes(filename):
    if not filename or not os.path.exists(filename):
        logging.info("File with cinema codes not found! "
                     "File format: \"<cinema_name> - <cinema_code>\"\n")
        return {}

    with open(filename) as f:
        codes = [line.rstrip('\n').split(" - ") for line in f]
    return {code: location for location, code in codes}


def get_text(text, xml_tag):
    if not text:
        logging.info("{}: Value not found.".format(xml_tag))
    return text


def get_date(date_string, xml_tag):
    if not date_string:
        logging.info("{}: Value not found.".format(xml_tag))
        return None
    try:
        dt = datetime.strptime(_rreplace(date_string, ":", "", 1), DATE_FORMAT)
        dt = dt.astimezone(tz=None)
        return datetime.strftime(dt, DATE_PRETTY)
    except ValueError:
        logging.info("Couldn't parse {} {}.".format(xml_tag, date_string))
        return date_string


def get_code(annotation_text, xml_tag):
    if not annotation_text:
        logging.info("{}: Value not found.".format(xml_tag))
        return None

    combined = "({})".format(")|(".join(list(CINEMAS.keys())))
    code_re = re.search(combined, annotation_text, re.IGNORECASE)

    if code_re:
        return CINEMAS.get(code_re.group(0).upper(), code_re.group(0))
    else:
        logging.info("Couldn't find cinema code in {}.".format(annotation_text))
        return None

CINEMAS = get_cinema_codes(CINEMA_CODES_PATH)
func = [get_text, get_code, get_date, get_date]


def get_parsed_files(filename):
    if not filename or not os.path.exists(filename):
        return []

    with open(filename) as f:
        done = [line.rstrip('\n') for line in f]
    return done


def set_parsed_files(filename, new_files):
    t = "file" if len(new_files) == 1 else "files"
    logging.info("Parsed {} new {}. Done!\n\n".format(len(new_files), t))

    if not filename or not new_files:
        return

    with open(filename, 'a+') as f:
        for fname in new_files:
            f.write(fname + '\n')


def write_to_csv(filename, parsed):
    if not filename:
        return

    header = False if os.path.exists(filename) else True
    with open(filename, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        header and writer.writeheader()
        for entry in parsed:
            writer.writerow(entry)


def parse(filename):
    logging.info("Parsing {}".format(filename))

    result = {key: None for key in CSV_FIELDS}
    tree = ET.ElementTree(file=os.path.join(XML_PATH, filename))
    tags_not_found = [True] * len(XML_TAGS)

    for e in tree.getroot().iter():
        tag_name = e.tag[e.tag.rindex("}")+1:]
        try:
            idx = XML_TAGS.index(tag_name)
            tags_not_found[idx] = False
            result[CSV_FIELDS[idx]] = func[idx](e.text, XML_TAGS[idx])
        except ValueError:
            pass
        
        if not any(tags_not_found):
            break

    for i, e in enumerate(tags_not_found):
        e and logging.info("{} not found.".format(XML_TAGS[i]))

    logging.info("\n")
    return result
