import dropbox
import json
import io
import os
import subprocess
import time

DEFAULT_PATH = os.path.expanduser('~')
SUBTIVALS_LOG_LOCATION = os.path.join(DEFAULT_PATH, 'subtivals_log.txt')

def main():
    """Main program.
    Get stats about the system and Subtivals and upload them in a folder
    corresponding to room number on Dropbox.

    """

    settings = get_settings()
    stats = get_subtivals_stats()
    stats.update(get_batery_stats())
    stats['location'] = settings['location']
    stats['laptop_on'] = 'YES'
    stats['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    stats['subtivals_on'] = subtivals_on()
    file_path = '/{0}.txt'.format(stats['location'])
    try:
        dbx = dropbox.Dropbox(os.environ['DROPBOX_TOKEN'])
        current_account = dbx.users_get_current_account()
        dbx.files_upload(make_stats_string(stats), file_path, mode=dropbox.files.WriteMode('overwrite', value=None))
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

def subtivals_on():
    subtivals_process = subprocess.Popen(['pidof', 'subtivals'], stdout=subprocess.PIPE)
    pid, err = subtivals_process.communicate()
    return 'YES' if str(pid, 'utf-8').strip() else 'NO'

def get_batery_stats():
    stats = {}
    get_batery_status = subprocess.Popen(['acpi', '-a'], stdout=subprocess.PIPE)
    get_batery_level = subprocess.Popen(['acpi', '-b'], stdout=subprocess.PIPE)
    batery_status, err = get_batery_status.communicate()
    batery_level, err = get_batery_level.communicate()

    if err:
        write_log('Got error "{0}" while retrieving batery_status.'.format(err))
        stats =  {'batery_level': '', 'batery_status': ''}
    else:
        status =  str(batery_status,'utf-8').rstrip('\n').split(':')[1]
        stats['batery_status'] = 'YES' if status.strip() == 'on-line' else 'NO'
        stats['batery_level'] = str(batery_level,'utf-8').rstrip('\n').split(', ')[1]

    return stats

def get_subtivals_stats():
    default_stats = {'subtitle': '', 'remaining': '',
                     'last_updated': '', 'duration': ''}
    try:
        with open(SUBTIVALS_LOG_LOCATION, mode='r', encoding='utf-8') as subtivals_log:
            stats = {}
            for line in subtivals_log:
                value = line.split('->')
                stats[value[0]] = value[1].strip()
            if not stats:
                stats = default_stats
    except:
        return default_stats

    return stats

def make_stats_string(stats):
    fields_order = ['location', 'laptop_on', 'subtivals_on', 'subtitle', 'duration',
             'remaining', 'batery_level', 'batery_status', 'last_updated']

    ordered = list(stats.get(key) for key in fields_order)
    string_values = [str(val) for val in ordered]
    return '\r\n'.join(ordered)

if __name__ == '__main__':
    main()
