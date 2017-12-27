#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GLPI Command Line"""

import pymysql
import datetime
import getpass
import tabulate
import configparser
import help.logos as logos
import help.ldap_auth as ldap
import os
import random
import time
import argparse

USERNAME = None

parser = argparse.ArgumentParser(description='Aplicacao para abrir varios chamados no GLPI.')
parser.add_argument('-c', '--config', help='.env or config file', required=True)
args = parser.parse_args()
CONFIG_FILE = args.config


def config_parser(section):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if config.has_section(section):
        items_dict = dict(config.items(section))
        return items_dict


def get_connection():
    try:
        sql_config = config_parser('sql')
        connection = pymysql.connect(host=sql_config['mysql_server'], user=sql_config['mysql_user'], passwd=sql_config['mysql_pass'], db=sql_config['mysql_db'])
        return connection.cursor()
    except Exception as error:
        print('get_connection() error: {}'.format(error))
        exit(2)


def search_user(name):
    query = "SELECT id, name FROM glpi_users WHERE name LIKE '%{}%'".format(name)
    with get_connection() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def search_category(name):
    query = "SELECT id, name FROM glpi_itilcategories WHERE name LIKE '%{}%'".format(name)
    with get_connection() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def search_group(name):
    query = "SELECT id, name FROM glpi_groups WHERE name LIKE '%{}%'".format(name)
    with get_connection() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def send_ticket(title, description, category_id, time_spent, tecnico_id, group_id):
    date_now = datetime.datetime.now()
    date_open = date_now.strftime('%Y-%m-%d %H:%M:%S')
    date_closed = (date_now + datetime.timedelta(minutes=int(time_spent))).strftime('%Y-%m-%d %H:%M:%S')
    duration = int(time_spent) * 60

    query_insert_ticket = """
    INSERT INTO glpi_tickets (name, date, closedate, solvedate, date_mod, status, users_id_recipient, requesttypes_id, 
    content, urgency, impact, priority, itilcategories_id, type, global_validation, takeintoaccount_delay_stat, actiontime) 
    VALUES ('{0}', '{1}', '{2}', '{2}', '{2}', '6', '{3}', '1', "{4}", '3', '3', '3', '{5}', '1', '1', '27', '900')
    """.format(title, date_open, date_closed, tecnico_id, description, category_id)

    with get_connection() as cursor:
        cursor.execute(query_insert_ticket)
        last_id = cursor.lastrowid

        query_insert_worker = """
        INSERT INTO glpi_tickets_users (tickets_id, users_id, type, use_notification) 
        VALUES ({0}, {1}, '2', '1')
        """.format(last_id, tecnico_id)

        query_insert_group = """
        INSERT INTO glpi_groups_tickets (tickets_id, groups_id, type) 
        VALUES ({0}, {1}, '2')
        """.format(last_id, group_id)

        query_insert_duration = """
        INSERT INTO glpi_tickettasks (tickets_id, date, users_id, content, actiontime, state, users_id_tech) 
        VALUES ({0}, '{1}', {2}, "{3}", {4}, '2', '0')
        """.format(last_id, date_closed, tecnico_id, description, duration)

        cursor.execute(query_insert_worker)
        cursor.execute(query_insert_group)
        cursor.execute(query_insert_duration)

        return last_id


def main_menu():

    os.system('clear')
    menus = dict()
    menus[1] = 'Abrir chamados'
    menus[2] = 'Procurar usuarios'
    menus[3] = 'Procurar categorias'
    menus[4] = 'Procurar grupos'

    print('Escolha uma das opcoes:')
    for num, key in enumerate(menus.keys(), 1):
        print('{0}. {1}'.format(num, menus[key]))
    print('\n0. Sair')

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
            print('Opcao invalida. Tente novamente!\n')
            time.sleep(1)
            menu_actions['main_menu']()


def menu_open_ticket():
    try:
        glpi_config = config_parser('glpi')
        glpi_ticket_url = glpi_config['url']

        title = input('Titulo\n > ')
        print('Digite/Cole a descricao. Ctrl-D para salvar.')
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
                time_spent = int(input('Tempo gasto em cada chamado (minutos)\n > '))
            except ValueError:
                print('Tente digitar numeros!')
                time.sleep(1)
                pass
            else:
                break

        while True:
            category = input('Categoria\n > ')
            check_category = search_category(category)
            if len(check_category) == 0:
                print('Nao foi possivel achar uma categoria com esse nome. Digite outra!')
            if len(check_category) == 1:
                category = check_category[0]
                break
            if len(check_category) > 1:
                print('Foram encontradas mais de uma categoria. Especifique!')
                print(tabulate.tabulate(check_category))

        while True:
            group = input('Grupo\n > ')
            check_group = search_group(group)
            if len(check_group) == 0:
                print('Não foi possivel achar um grupo com esse nome. Digite outra!')
            if len(check_group) == 1:
                group = check_group[0]
                break
            if len(check_group) > 1:
                print('Foram encontradas mais de um grupo. Especifique!')
                print(tabulate.tabulate(check_group))

        while True:
            try:
                amount = int(input('Quantidade (100 max.)\n > '))
                if amount > 100:
                    print('Quantidade máxima excedida!')
                else:
                    break
            except ValueError:
                print('Tente digitar numeros!')
                time.sleep(1)
                pass

        while True:
            tecnico = input('Tecnico\n > ')
            check_user = search_user(tecnico)
            print(check_user)
            if len(check_user) == 0:
                print('Não foi possivel achar um tecnico com esse nome. Digite outro!')
            if len(check_user) == 1:
                username = check_user[0]
                break
            if len(check_user) > 1:
                print('Foram encontradas mais de um técnico com esse nome. Especifique!')
                print(tabulate.tabulate(check_user))

        os.system('clear')
        print(tabulate.tabulate([['Titulo', title], ['Descricao', description], ['Tempo gasto', str(time_spent) + ' minutos'],
                                 ['Categoria', category[1]], ['Grupo', group[1]], ['Quantidade', amount], ['Autor', username[1]]], tablefmt='grid'))

        confirm = input('\nAs informações estão corretas? ([S]/n)\n > ').lower()
        if confirm in ('s', 'sim', ''):

            print('Chamados sendo processados... ')
            time.sleep(1)
            for num in range(1, int(amount) + 1):
                last_id = send_ticket(title, description, category[0], time_spent, username[0], group[0])
                print('{}. {}{}'.format(num, glpi_ticket_url, last_id))

    except KeyboardInterrupt:
        print('\nTchau!')
        exit(0)


def menu_search_user():
    while True:
        try:
            user = input('Usuário > ')
            print(tabulate.tabulate(search_user(user), headers=['ID', 'Usuário']))
            other_user = input('Pesquisar outro usuário? ([S]/n) > ').lower()
            if other_user in ['s', 'sim', '']:
                os.system('clear')
                pass
            else:
                back()
        except EOFError:
            back()


def menu_search_category():
    while True:
        try:
            category = input('Categoria > ')
            print(tabulate.tabulate(search_category(category), headers=['ID', 'Categoria']))
            other_user = input('Pesquisar outra categoria? ([S]/n) > ').lower()
            if other_user in ['s', 'sim', '']:
                os.system('clear')
                pass
            else:
                back()
        except EOFError:
            back()


def menu_search_group():
    while True:
        try:
            group = input(' Grupo > ')
            print(tabulate.tabulate(search_user(group), headers=['ID', 'Grupo']))
            other_user = input('Pesquisar outro grupo? ([S]/n) > ').lower()
            if other_user in ['s', 'sim', '']:
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

    ad = config_parser('active_directory')
    os.system('clear')

    try:
        random_logo = logos.LOGOS[list(logos.LOGOS)[random.randrange(0, len(logos.LOGOS))]]
        print(random_logo)

        print('\n* Autenticacao AD')
        print('* Necessario estar no grupo Diretoria TI\n')

        global USERNAME
        USERNAME = input('Seu usuario: ')
        password = getpass.getpass('Sua senha: ')

        if ldap.auth_ad(USERNAME, password, ad['domain_servers'], ad['domain_name'], ad['base_dn']):
            main_menu()
        else:
            exit(1)

    except KeyboardInterrupt:
        print('\nBye...')
        exit(0)


if __name__ == '__main__':
    main()
