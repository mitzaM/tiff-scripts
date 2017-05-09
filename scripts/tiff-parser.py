import sys

from helpers import *

if __name__ == "__main__":
    today = datetime.today()
    logging.info("Parser started on {}".format(
        datetime.strftime(today, DATE_PRETTY)))

    if not ALLOW_START < today < ALLOW_END:
        logging.info(AVAILABILITY_ERROR_MSG)
        sys.exit()

    if not os.path.exists(XML_PATH):
        logging.info("/xml folder not found. Quitting.\n\n")
        sys.exit()

    done = get_parsed_files(FILES_DONE_PATH)
    new_files, parsed = [], []
    cinemas = get_cinema_codes(CINEMA_CODES_PATH)

    for filename in os.listdir(XML_PATH):
        if filename.lower().endswith(".xml") and filename not in done:
            p = parse(filename, cinemas)
            parsed.append(p)
            new_files.append(filename)

    set_parsed_files(FILES_DONE_PATH, new_files)
    write_to_csv(OUTPUT_CSV_PATH, parsed)
