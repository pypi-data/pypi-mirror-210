"""
created by：2018-2-23 14:15:57
modify by: 2023-05-13 15:05:05

功能：sqlite3的方法函数的封装。
"""

import sqlite3

import sqlite3

class SQLite3Util:
    """
    使用时可以像这样：
    with SQLite3Util('my.db') as db:
        result = db.query('SELECT * FROM users WHERE age > ?', (18,))
        for row in result:
            print(row['username'], row['age'])
    """

    def __init__(self, dbfile=None):
        """
        如果dbfile为None或空字符串，就使用内存数据库，
        否则就使用dbfile指定的数据库文件存
        """
        self.db = sqlite3.connect(dbfile or ':memory:')
        self.c = self.db.cursor()

    def query(self, sql, params=None):
        """
        执行查询操作，返回所有结果。
        """
        with self.db:
            self.c.execute(sql, params or ())
            return self.c.fetchall()

    def insert(self, table, data):
        """
        执行插入操作，返回自动生成的 ID 号。
        """
        fields = ','.join(data.keys())
        values = tuple(data.values())
        placeholders = ','.join(['?'] * len(data))
        sql = f'INSERT INTO {table} ({fields}) VALUES ({placeholders})'
        with self.db:
            self.c.execute(sql, values)
            return self.c.lastrowid

    def select(self, table, fields='*', condition='', params=None):
        """
        执行查询操作，并使用 Row 创建可迭代的行对象。
        """
        sql = f'SELECT {fields} FROM {table}'
        if condition:
            sql += f' WHERE {condition}'
        with self.db:
            self.db.row_factory = sqlite3.Row  # 设置 row_factory
            self.c.execute(sql, params or ())
            return self.c.fetchall()

    def execute(self, sql, params=None):
        """
        执行任意 SQL 语句，返回是否修改了数据。
        可以通过判断 total_changes 是否大于 0 来确定是否有更新。
        """
        with self.db:
            if isinstance(sql, list):
                self.c.executemany(sql, params or ())
            else:
                self.c.execute(sql, params or ())
            return True if self.db.total_changes > 0 else False

    def __enter__(self):
        """
        将 Row 作为默认的行处理函数。
        """
        self.db.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, tb):
        """
        关闭游标和数据库连接。
        """
        self.c.close()
        self.db.close()
