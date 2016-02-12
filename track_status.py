# Copyright 2015 Egor Tensin <Egor.Tensin@gmail.com>
# This file is licensed under the terms of the MIT License.
# See LICENSE.txt for details.

import argparse
import logging
import time
import sys

from api import *

def format_user(user):
    if user.has_last_name():
        return '{} {}'.format(user.get_last_name(), user.get_first_name())
    else:
        return '{}'.format(user.get_first_name())

def format_user_is_online(user):
    return '{} is ONLINE'.format(format_user(user))

def format_user_is_offline(user):
    return '{} is OFFLINE'.format(format_user(user))

def format_user_last_seen(user):
    return '{} was last seen at {}'.format(format_user(user), user.get_last_seen())

def format_user_went_online(user):
    return '{} went ONLINE'.format(format_user(user))

def format_user_went_offline(user):
    return '{} went OFFLINE'.format(format_user(user))

def user_is_online(user):
    logging.info(format_user_is_online(user))

def user_is_offline(user):
    logging.info(format_user_is_offline(user))
    logging.info(format_user_last_seen(user))

def user_went_online(user):
    logging.info(format_user_went_online(user))

def user_went_offline(user):
    logging.info(format_usre_went_offline(user))

def print_status(user):
    if user.is_online():
        user_is_online(user)
    else:
        user_is_offline(user)

def print_status_update(user):
    if user.is_online():
        user_went_online(user)
    else:
        user_went_offline(user)

def parse_timeout(source):
    timeout = int(source)
    if timeout < 1:
        raise argparse.ArgumentTypeError(
            'please specify a positive number of seconds as refresh timeout')
    return timeout

DEFAULT_TIMEOUT=5

def loop_update_status(api, user_ids, timeout=DEFAULT_TIMEOUT):
    fields = User.Field.ONLINE, User.Field.LAST_SEEN
    users = list(api.users_get(user_ids, fields))
    for user in users:
        print_status(user)
    while True:
        time.sleep(timeout)
        updated_users = list(api.users_get(user_ids, fields))
        for i in range(len(updated_users)):
            if users[i].is_online() != updated_users[i].is_online():
                users[i] = updated_users[i]
                print_status_update(updated_users[i])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Track when people go online/offline.')

    parser.add_argument(metavar='UID', dest='user_ids', nargs='+',
                        help='user IDs or "screen names"')
    parser.add_argument('-t', '--timeout', default=DEFAULT_TIMEOUT,
                        type=parse_timeout,
                        help='set refresh interval (seconds)')
    parser.add_argument('-l', '--log', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='set log file path (stdout by default)')
    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s] %(message)s',
                        stream=args.log,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    api = API(Language.EN)

    try:
        loop_update_status(api, args.user_ids, timeout=args.timeout)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
