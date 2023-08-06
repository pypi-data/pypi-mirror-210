# -*- coding: utf-8 -*-
import importlib

from tornado.options import options

from lesscode.db.base_connection_pool import BaseConnectionPool

tornado_sqlalchemy = None
try:
    tornado_sqlalchemy = importlib.import_module("tornado_sqlalchemy")
except ImportError as e:
    raise Exception(f"tornado-sqlalchemy is not exist,run:pip install tornado-sqlalchemy==0.7.0")


class MysqlSqlAlchemyPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    def sync_create_pool(self):
        mysql_url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
            self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
            self.conn_info.db_name)
        db = tornado_sqlalchemy.SQLAlchemy(mysql_url, engine_options={"echo": True, "pool_recycle": 3600})
        options.db = db
        return db
