# encoding:  utf-8

import sqlite3
import pymysql
from clickhouse_driver import Client as Clickhouse
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class SQLiteTool:
    #  sqlite 操作tools
    # db = SQLiteTool('../../db/db.sqlite3')
    # # result = db.execute_sql('SELECT * FROM cndba')
    # result = db.select('kg_user_all')
    # print(result)
    #
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def dict_factory(self, cursor, row):
        """格式化结果由set转为dict"""
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]
        return d

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def execute(self, sql, params=None):
        logging.debug("execute sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("params = {}".format(params))
        if not self.conn:
            self.connect()
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchall()

    def execute_many(self, sql, params_list):
        logging.debug("execute_many sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("params_list = {}".format(params_list))
        if not self.conn:
            self.connect()
        self.cursor.executemany(sql, params_list)

    def commit(self):
        if self.conn:
            self.conn.commit()

    def insert(self, table, data):
        placeholders = ', '.join(['?'] * len(data))
        columns = ', '.join(data.keys())
        values = tuple(data.values())
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        self.execute(sql, values)
        self.commit()

    def insert_many(self, table, data_list):
        for data in data_list:
            placeholders = ', '.join(['?'] * len(data))
            columns = ', '.join(data.keys())
            values = tuple(data.values())
            sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
            self.execute(sql, values)
        self.commit()

    def update(self, table, data, condition=None, params=None):
        set_clause = ', '.join([f'{col} = ?' for col in data.keys()])
        values = tuple(data.values())
        where_clause = f'WHERE {condition}' if condition else ''
        params = params or ()
        sql = f'UPDATE {table} SET {set_clause} {where_clause}'
        self.execute(sql, values + params)
        self.commit()

    def delete(self, table, condition=None, params=None):
        where_clause = f'WHERE {condition}' if condition else ''
        params = params or ()
        sql = f'DELETE FROM {table} {where_clause}'
        self.execute(sql, params)
        self.commit()

    def select(self, table, columns='*', condition=None, params=None):
        where_clause = f'WHERE {condition}' if condition else ''
        params = params or ()
        sql = f'SELECT {columns} FROM {table} {where_clause}'
        return self.execute(sql, params)

    def execute_sql(self, sql, params=None):
        return self.execute(sql, params)


class MySQLTool:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database,
                                    cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()

    def execute(self, sql, params=None):
        logging.debug("params sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("params = {}".format(params))
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return self.cursor.fetchall()
        except Exception as e:
            self.conn.rollback()
            print('Error:', e)

    def insert(self, table, data):
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        params = list(data.values())
        self.execute(sql, params)

    def update(self, table, data, condition):
        set_clause = ','.join([f"{k}=%s" for k in data])
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = list(data.values())
        self.execute(sql, params)

    def delete(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        self.execute(sql)

    def select(self, table, columns=None, condition=None):
        if not columns:
            columns = '*'
        if not condition:
            condition = '1'
        sql = f"SELECT {columns} FROM {table} WHERE {condition}"
        return self.execute(sql)

    def execute_many(self, sql, params_list):
        logging.debug("execute_many sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("execute_many = ".format(params_list))
        try:
            self.cursor.executemany(sql, params_list)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print('Error:', e)

    def insert_many(self, table, data_list):
        keys = ','.join(data_list[0].keys())
        values = ','.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        params_list = [list(data.values()) for data in data_list]
        self.execute_many(sql, params_list)


class ClickHouseTool:
    def __init__(self, host, port, user, password, database):
        self.client = Clickhouse(host=host, port=port, user=user, password=password, database=database)

    def execute(self, sql, params=None):
        logging.debug("execute sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("params = {}".format(params))
        try:
            result = self.client.execute(sql, params)
            return result
        except Exception as e:
            print('Error:', e)

    def insert(self, table, data):
        keys = ','.join(data.keys())
        values = ','.join(['%({})s'.format(key) for key in data.keys()])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.execute(sql, data)

    def update(self, table, data, condition):
        set_clause = ','.join([f"{k}=%({k})s" for k in data])
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        self.execute(sql, data)

    def delete(self, table, condition):
        sql = f"DELETE FROM {table} WHERE {condition}"
        self.execute(sql)

    def select(self, table, columns=None, condition=None):
        if not columns:
            columns = '*'
        if not condition:
            condition = '1'
        sql = f"SELECT {columns} FROM {table} WHERE {condition}"
        return self.execute(sql)

    def execute_many(self, sql, params_list):
        logging.debug("execute_many sql")
        logging.debug("sql = {}".format(sql))
        logging.debug("execute_many = ".format(params_list))
        try:
            self.client.execute(sql, params_list)
        except Exception as e:
            print('Error:', e)

    def insert_many(self, table, data_list):
        keys = ','.join(data_list[0].keys())
        values = [list(data.values()) for data in data_list]
        placeholders = ','.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        self.execute_many(sql, values)

#  sqlite 操作tools
# db = SQLiteTool('../../db/db.sqlite3')
# # result = db.execute_sql('SELECT * FROM cndba')
# result = db.execute_sql('SELECT * FROM kg_user_all limit 1')
# print(result)
