import pymysql
import datetime
import configparser


class Glpi(object):
    def __init__(self, conf):
        self.conf = conf

    def __config_parser(self, section):
        config = configparser.ConfigParser()
        config.read(self.conf)
        if config.has_section(section):
            items_dict = dict(config.items(section))
            return items_dict

    def __sql(self):
        sql = self.__config_parser('sql')
        return sql['server'], sql['name'], sql['user'], sql['pass']

    def url(self):
        return self.__config_parser('glpi')['url']

    def ad(self):
        ad = self.__config_parser('ad')
        return ad['server'], ad['prefix'], ad['base']

    def connection(self):
        sql_server, sql_name, sql_user, sql_pass = self.__sql()
        connection = pymysql.connect(host=sql_server, user=sql_name, passwd=sql_user, db=sql_pass)
        return connection.cursor()

    def search_user(self, id_name):
        query = "SELECT id, name FROM glpi_users WHERE name LIKE '%{0}%' OR id == '%{0}%'".format(id_name)
        with self.connection() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def search_category(self, name):
        query = "SELECT id, name FROM glpi_itilcategories WHERE name LIKE '%{}%'".format(name)
        with self.connection() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def search_group(self, name):
        query = "SELECT id, name FROM glpi_groups WHERE name LIKE '%{}%'".format(name)
        with self.connection() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def send_ticket(self, title, description, category_id, time_spent, tecnico_id, group_id):
        date_now = datetime.datetime.now()
        date_open = date_now.strftime('%Y-%m-%d %H:%M:%S')
        date_closed = (date_now + datetime.timedelta(minutes=int(time_spent))).strftime('%Y-%m-%d %H:%M:%S')
        duration = int(time_spent) * 60

        query_insert_ticket = """
        INSERT INTO glpi_tickets (name, date, closedate, solvedate, date_mod, status, users_id_recipient, requesttypes_id, 
        content, urgency, impact, priority, itilcategories_id, type, global_validation, takeintoaccount_delay_stat, actiontime) 
        VALUES ('{0}', '{1}', '{2}', '{2}', '{2}', '6', '{3}', '1', "{4}", '3', '3', '3', '{5}', '1', '1', '27', '900')
        """.format(title, date_open, date_closed, tecnico_id, description, category_id)

        with self.connection() as cursor:
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
