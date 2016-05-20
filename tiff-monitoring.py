import dropbox
import json
import io
import os
import subprocess

APP_TOKEN = '07_anwjgBHsAAAAAAAAACovPLeHyqFRcu-rdruSJlhMbNGk1d7jyrIVJtBXFDX70'
LOG_PATH = '/home/g/tiff-monitoring.log'
SUBTIVALS_LOG_LOCATION = '/home/g/Documents/subtivals/build-subtivals-Desktop-Debug/log_file.json'

def main():
    """Main program.
    Get stats about the system and Subtivals and upload them in a folder
    corresponding to room number on Dropbox.

    """
    dbx = dropbox.Dropbox(APP_TOKEN)
    current_account = dbx.users_get_current_account()
    write_log('Connected to DropBox account: {0}'.format(current_account))



    settings = get_settings()
    stats = {'now': '23:00'}
    json_stats = json.dumps(stats)
    file_path = '/{0}/room_{1}.json'.format(settings['location'], settings['room_number'])
    dbx.files_upload(json_stats, file_path)

    for entry in dbx.files_list_folder('').entries:
        print(entry.name)


def get_filename():
    default_settings = {'room_number': 0,'location': 'unknown'}
    settings = default_settings
    config_file_path = os.path.join(DEFAULT_PATH, 'tiff-monitoring-config.json')

    try:
        with open(config_file_path, mode='r', encoding='utf-8') as config_file:
            try:
                settings = json.loads(config_file.read())
                if settings == default_settings:
                    msg='The config file for tiff-monitoring still has the default values.'
                    show_message(msg)
            except ValueError:
                with open(config_file_path, mode='a', encoding='utf-8') as config_file:
                    config_file.write(json.dumps(default_settings))
                msg='The config file for tiff-monitoring was empty or invalid JSON and has been rewritten.'
                show_message(msg)
    except FileNotFoundError:
        with open(config_file_path, mode='a', encoding='utf-8') as config_file:
            config_file.write(json.dumps(default_settings))
            msg='The config file for tiff-monitoring didn\'t exist and was created just now.'
            show_message(msg)

    return settings

def show_message(msg):
    default_message = ('{0}\nPlease open it at "/home/tiff/tiff-monitoring-config.json" '
                       'and update room name with something that identifies it(location+room_number*).')
    subprocess.call(['zenity', '--info', '--text', default_message.format(msg)])

def write_log(msg):
    with open(LOG_PATH, mode='a', encoding='utf-8') as log_file:
        log_file.write(msg)

def get_subtivals_stats():
    default_stats = {'subtitle': 'currently unavailable', 'remaining': '',
                     'last_updated': '', 'duration': ''}
    try:
        with open(SUBTIVALS_LOG_LOCATION, mode='r', encoding='utf-8') as subtivals_log:
            stats = json.loads(subtivals_log.read())
            if not stats:
                stats = default_stats
    except e:
        write_log(e.msg)
        return default_stats

    return stats


if __name__ == '__main__':
    main()
