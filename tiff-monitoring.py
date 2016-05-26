import dropbox
import json
import io
import os
import subprocess

DEFAULT_PATH = os.path.expanduser('~')
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
    # TODO generate random string for filename
    file_path = 'unfortunate_test.txt'
    try:
        dbx = dropbox.Dropbox(os.environ['DROPBOX_TOKEN'])
        current_account = dbx.users_get_current_account()
        write_log('Connected to DropBox account: {0}'.format(current_account))
        dbx.files_upload(stats, file_path)

        for entry in dbx.files_list_folder('').entries:
            print(entry.name)
    except:
        exit

def get_settings():
    default_settings = {'room_name': 'unknown'}
    msg, filename = '', ''
    config_file_path = os.path.join(DEFAULT_PATH, 'tiff-monitoring-config.json')

    try:
        with open(config_file_path, mode='r', encoding='utf-8') as config_file:
            try:
                settings = json.loads(config_file.read())
                if settings == default_settings:
                    msg='The room name for your location is still unknown.'
            except ValueError:
                msg='The config file for tiff-monitoring is empty or invalid JSON and has to be rewritten.'
                settings = default_settings
    except FileNotFoundError:
            msg='The config file for tiff-monitoring doesn\'t exists and has to be created '
            settings = default_settings

    if msg:
        filename = retrieve_filename(msg)
        if filename: settings['room_name'] = filename

        with open(config_file_path, mode='w', encoding='utf-8') as config_file:
            config_file.write(json.dumps(settings))

    return settings

def retrieve_filename(msg):
    default_msg = ('{0}\nPlease provide a room name:')
    hint_msg = 'some unique identificator (ex: location+room_number*)'
    check_kdialog = subprocess.Popen(['pidof', 'kdialog'], stdout=subprocess.PIPE)
    pid, err = check_kdialog.communicate()
    if not str(pid, 'utf-8').strip():
        file_dialog =  subprocess.Popen(['kdialog', '--inputbox', default_msg.format(msg),
                                         hint_msg], stdout=subprocess.PIPE)
        user_input, err = file_dialog.communicate()
        write_log('user_input: {0}, err: {1}'.format(user_input, err))
        if err:
            write_log('Got error "{0}" while retrieving filename.'.format(err))
            return
        else:
            return str(user_input,'utf-8').rstrip('\n') if user_input else 'unknown'

def write_log(msg):
    log_file_path = os.path.join(DEFAULT_PATH, 'tiff-monitoring.log')
    with open(log_file_path, mode='a', encoding='utf-8') as log_file:
        log_file.write(msg + '\n')

def get_subtivals_stats():
    default_stats = {'subtitle': 'currently unavailable', 'remaining': '',
                     'lastUpdated': '', 'duration': ''}
    try:
        with open(SUBTIVALS_LOG_LOCATION, mode='r', encoding='utf-8') as subtivals_log:
            stats = json.loads(subtivals_log.read())
            if not stats:
                stats = default_stats
    except:
        return default_stats

    return stats


if __name__ == '__main__':
    main()
