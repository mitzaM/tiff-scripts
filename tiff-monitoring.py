import dropbox
import json
import io
import os
import subprocess
from os.path import expanduser

DEFAULT_PATH = expanduser('~')
APP_TOKEN = '07_anwjgBHsAAAAAAAAACovPLeHyqFRcu-rdruSJlhMbNGk1d7jyrIVJtBXFDX70'
SUBTIVALS_LOG_LOCATION = os.path.join(DEFAULT_PATH, 'subtivals_log.txt')

def main():
    """Main program.
    Get stats about the system and Subtivals and upload them in a folder
    corresponding to room number on Dropbox.

    """

    settings = get_settings()
    stats = {}
    stats['location'] = settings['location']
    stats.update(get_subtivals_stats())
    write_log(','.join(stats.values()))
    # TODO generate random string for filename
    file_path = 'unfortunate_test.txt'
    try:
        dbx = dropbox.Dropbox(APP_TOKEN)
        dbx.files_upload(stats, file_path)

        #TODO: Delete. Kept for debugging
        for entry in dbx.files_list_folder('').entries:
            print(entry.name)
    except:
        exit

def get_settings():
    default_settings = {'location': 'unknown'}
    msg, filename = '', ''
    config_file_path = os.path.join(DEFAULT_PATH, 'tiff-monitoring-config.json')

    try:
        with open(config_file_path, mode='r', encoding='utf-8') as config_file:
            try:
                settings = json.loads(config_file.read())
                if settings == default_settings or \
                   not set(settings).issuperset(default_settings):
                    msg='The location of this laptop is still unknown.'
            except ValueError:
                msg='The config file for tiff-monitoring is empty or invalid JSON and has to be rewritten.'
                settings = default_settings
    except FileNotFoundError:
            msg='The config file for tiff-monitoring doesn\'t exists and has to be created '
            settings = default_settings

    if msg:
        filename = retrieve_filename(msg)
        if filename: settings['location'] = filename

        with open(config_file_path, mode='w', encoding='utf-8') as config_file:
            config_file.write(json.dumps(settings))

    return settings

def retrieve_filename(msg):
    default_msg = ('{0}\nPlease provide the location name:')
    hint_msg = 'cinema room location'
    check_zenity = subprocess.Popen(['pidof', 'zenity'], stdout=subprocess.PIPE)
    pid, err = check_zenity.communicate()
    if not str(pid, 'utf-8').strip():
        file_dialog =  subprocess.Popen(['zenity', '--entry', '--title', 'Cinema Location',
                                         '--text', default_msg.format(msg),
                                         '--entry-text',hint_msg], stdout=subprocess.PIPE)
        user_input, err = file_dialog.communicate()
        if err:
            write_log('Got error "{0}" while retrieving filename.'.format(err))
            return
        else:
            return str(user_input,'utf-8').rstrip('\n') if user_input else 'unknown'

def write_log(msg):
    log_file_path = os.path.join(DEFAULT_PATH, 'tiff-monitoring.log')
    with open(log_file_path, mode='a', encoding='utf-8') as log_file:
        log_file.write(msg)
        log_file.write('\n')

def get_subtivals_stats():
    default_stats = {'subtitle': 'currently unavailable', 'remaining': '',
                     'last_updated': '', 'duration': ''}
    try:
        with open(SUBTIVALS_LOG_LOCATION, mode='r', encoding='utf-8') as subtivals_log:
            stats = {}
            for line in subtivals_log:
                value = line.split('->')
                stats[value[0]] = value[1]
            if not stats:
                stats = default_stats
    except Exception as e:
        write_log(e)
        return default_stats

    return stats


if __name__ == '__main__':
    main()
