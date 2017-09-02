#!/usr/bin/env python

REGEX_HTTP_LOC = 'http://pac.uku.im/regex'
REGEX_LIST_LOC = '/opt/crx_url_list.txt'

import requests
import subprocess
import datetime
import time
# from raven import Client
# raven_client = Client('...')


operation_failed = False
backup_file_loc = None


def main():
    global operation_failed
    global backup_file_loc

    print 'Obtain the regex list...'
    regex_file_content = requests.get(REGEX_HTTP_LOC).text
    assert '\\.youku\\.com\\/' in regex_file_content
    assert '\\.tudou\\.com\\/' in regex_file_content
    assert '\\.qq\\.com\\/' in regex_file_content
    # print regex_file_content
    # return

    print 'Compare the new file with the old one...'
    with open(REGEX_LIST_LOC, 'r') as f:
        old_content = f.read()
    assert '\\.youku\\.com\\/' in regex_file_content
    assert '\\.tudou\\.com\\/' in regex_file_content
    assert '\\.qq\\.com\\/' in regex_file_content

    if old_content == regex_file_content:
        print 'Already use the latest version...'
    else:
        print 'Back up the old config file...'
        date_str = datetime.datetime.now().strftime('%Y-%b-%d')
        backup_file_loc = REGEX_LIST_LOC + '.bak.' + date_str
        assert 0 == subprocess.call(
            ['cp', '-fv', REGEX_LIST_LOC, backup_file_loc])
        time.sleep(3)

        print 'Write new config content into a file...'
        with open(REGEX_LIST_LOC, 'w') as new_file:
            new_file.write(regex_file_content)
        time.sleep(3)

        print 'Reload Squid service...'
        try:
            output = subprocess.check_output(
                # ['/sbin/reload', 'squid3'])
                ['/sbin/service', 'squid', 'reload'])
            print output
        except subprocess.CalledProcessError as err:
            print 'Error code:', err.returncode
            print err.output
            operation_failed = True
            # raven_client.captureException()
        time.sleep(3)

    if old_content != regex_file_content and not operation_failed:
        msg = 'Squid config is updated!'
        print msg
        # raven_client.captureMessage(msg)


if __name__ == '__main__':
    print
    try:
        main()
    except Exception as err:
        print err
        operation_failed = True
        # raven_client.captureException()
    finally:
        if operation_failed and backup_file_loc is not None:
            print 'Restoring backup file...'
            subprocess.call(['cp', '-fv', backup_file_loc, REGEX_LIST_LOC])
    print