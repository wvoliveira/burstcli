#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GLPI Command Line"""

from .help import *
from . import __git__
import getpass
import tabulate
import os
import random
import time
import argparse
import sys

USERNAME = None
GLPI = None


class Example(argparse.Action):
    def __init__(self, option_strings, dest='==SUPPRESS==', default='==SUPPRESS==', help='show example config file and exit'):
        super(Example, self).__init__( option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        package_dir = sys.modules['burst'].__path__[0]
        example_file = os.path.join(package_dir, 'conf/example.ini')

        with open(example_file) as file:
            print(file.read())
            exit(0)


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='GLPI - Open some tickets in one time.\n{0}'.format(__git__), prog='burst')
parser.add_argument('--conf', metavar='file', help='config file', required=True)
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('--example', action=Example)
args = parser.parse_args()


def example_conf():
    package_dir = sys.modules['burst'].__path__[0]
    example_file = os.path.join(package_dir, 'conf/example.ini')

    with open(example_file) as file:
        print(file.read())
        exit(0)


def main_menu():

    os.system('clear')
    menus = dict()
    menus[1] = 'Open tickets'
    menus[2] = 'Search users'
    menus[3] = 'Search categories'
    menus[4] = 'Search groups'

    print('Pick of one option:')
    for num, key in enumerate(menus.keys(), 1):
        print('{0}. {1}'.format(num, menus[key]))
    print('\n0. Exit')

    choice = input(" >  ")
    exec_menu(choice)


def exec_menu(choice):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print('Invalid option. Try again!\n')
            time.sleep(1)
            menu_actions['main_menu']()


def menu_open_ticket():
    try:
        glpi_ticket_url = GLPI.url()

        title = input('Title\n > ')
        print('Digit/paste description. Ctrl-D to save.')
        description = []
        while True:
            try:
                line = input(' > ')
            except EOFError:
                print('')
                break
            if line != '':
                description.append(line)
        description = '\n'.join(description)

        while True:
            try:
                time_spent = int(input('Time expend in ticket (minutes)\n > '))
            except ValueError:
                print('Just numbers, please!')
                time.sleep(1)
                pass
            else:
                break

        while True:
            category = input('Category\n > ')
            check_category = GLPI.search_category(category)
            if len(check_category) == 0:
                print("I didn't find categories with this name. Try again!")
            if len(check_category) == 1:
                category = check_category[0]
                break
            if len(check_category) > 1:
                print('I found some categories with this name. Specify!')
                print(tabulate.tabulate(check_category))

        while True:
            group = input('Group\n > ')
            check_group = GLPI.search_group(group)
            if len(check_group) == 0:
                print("I didn't find groups with this name. Try again!")
            if len(check_group) == 1:
                group = check_group[0]
                break
            if len(check_group) > 1:
                print('I found some groups with this name. Specify!')
                print(tabulate.tabulate(check_group))

        while True:
            try:
                amount = int(input('Number (100 max.)\n > '))
                if amount > 100:
                    print('Maximum quantity exceeded!')
                else:
                    break
            except ValueError:
                print('Just numbers!')
                time.sleep(1)
                pass

        while True:
            tecnico = input('Analyst (or ID)\n > ')
            check_user = GLPI.search_user(tecnico)
            print(check_user)

            if len(check_user) == 0:
                print("I didn't find analysts with this name. Try again!")

            if type(tecnico) == int:
                if len(check_user) == 1:
                    username = check_user[0]
                    break

            if len(check_user) == 1:
                username = check_user[0]
                break

            if len(check_user) > 1:
                print('I found some users with this name. Specify!')
                print(tabulate.tabulate(check_user))

        os.system('clear')
        print(tabulate.tabulate([['Title', title],
                                 ['Description', description],
                                 ['Expend time', str(time_spent) + ' minutes'],
                                 ['Category', category[1]],
                                 ['Group', group[1]],
                                 ['Number', amount],
                                 ['Author', username[1]]], tablefmt='grid'))

        confirm = input('\nIs the information correct? ([Y]/n)\n > ').lower()
        if confirm in ['y', 'yes', 's', 'sim', '']:
            print('Sending information.. ')
            time.sleep(1)

            for num in range(1, int(amount) + 1):
                last_id = GLPI.send_ticket(title, description, category[0], time_spent, username[0], group[0])
                print('{0}. {1}{2}'.format(num, glpi_ticket_url, last_id))

    except KeyboardInterrupt:
        print('\nBye!')
        exit(0)


def menu_search_user():
    while True:
        try:
            user = input('User > ')
            print(tabulate.tabulate(GLPI.search_user(user), headers=['ID', 'User']))
            other_user = input('Search for another user? ([Y]/n) > ').lower()
            if other_user in ['y', 'yes', 's', 'sim', '']:
                os.system('clear')
                pass
            else:
                back()
        except EOFError:
            back()


def menu_search_category():
    while True:
        try:
            category = input('Category > ')
            print(tabulate.tabulate(GLPI.search_category(category), headers=['ID', 'Category']))
            other_user = input('Search for another category? ([Y]/n) > ').lower()
            if other_user in ['y', 'yes', 's', 'sim', '']:
                os.system('clear')
                pass
            else:
                back()
        except EOFError:
            back()


def menu_search_group():
    while True:
        try:
            group = input('Group > ')
            print(tabulate.tabulate(GLPI.search_user(group), headers=['ID', 'Group']))
            other_user = input('Search for another group? ([Y]/n) > ').lower()
            if other_user in ['y', 'yes', 's', 'sim', '']:
                os.system('clear')
                pass
            else:
                back()
        except EOFError:
            back()


def back():
    menu_actions['main_menu']()


menu_actions = {
    'main_menu': main_menu,
    '1': menu_open_ticket,
    '2': menu_search_user,
    '3': menu_search_category,
    '4': menu_search_group,
    '9': back,
    '0': exit,
}


def main():
    os.system('clear')

    global GLPI
    GLPI = glpi.Glpi(args.conf)

    ad_server, ad_prefix, ad_base = GLPI.ad()

    try:
        random_logo = logos.LOGOS[list(logos.LOGOS)[random.randrange(0, len(logos.LOGOS))]]
        print(random_logo)

        print('\n* AD Authentication')
        print('* Need to be in the IT Management group\n')

        global USERNAME
        USERNAME = input('User: ')
        password = getpass.getpass('Pass: ')

        if ldap_auth.auth_ad(USERNAME, password, ad_server, ad_prefix, ad_base):
            main_menu()
        else:
            print('Error to authenticate!')
            exit(1)

    except KeyboardInterrupt:
        print('\nBye...')
        exit(0)


if __name__ == '__main__':
    main()
