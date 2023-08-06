# -*- coding: utf-8 -*-
import importlib

from lesscode.db.base_connection_pool import BaseConnectionPool


class SqlAlchemyPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    def sync_create_pool(self):
        db_type = "mysql"
        if self.conn_info.params:
            if self.conn_info.params.get("db_type"):
                db_type = self.conn_info.params.pop("db_type")
        if db_type == "mysql":
            url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        elif db_type == "postgresql":
            url = 'postgresql+psycopg2://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        elif db_type == "tidb":
            url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        elif db_type == "ocean_base":
            url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
                self.conn_info.user, self.conn_info.password, self.conn_info.host, self.conn_info.port,
                self.conn_info.db_name)
        else:
            raise Exception("UNSUPPORTED DB TYPE")
        try:
            sqlalchemy = importlib.import_module("sqlalchemy")
        except ImportError:
            raise Exception(f"sqlalchemy is not exist,run:pip install sqlalchemy==1.4.36")
        engine = sqlalchemy.create_engine(url, echo=self.conn_info.params.get("echo",
                                                                              True) if self.conn_info.params else True,
                                          pool_size=self.conn_info.min_size,
                                          pool_recycle=self.conn_info.params.get("pool_recycle",
                                                                                 3600) if self.conn_info.params else 3600,
                                          max_overflow=self.conn_info.params.get("max_overflow",
                                                                                 0) if self.conn_info.params else 0,
                                          pool_timeout=self.conn_info.params.get("pool_timeout",
                                                                                 10) if self.conn_info.params else 10,
                                          pool_pre_ping=self.conn_info.params.get("pool_pre_ping",
                                                                                  True) if self.conn_info.params else True)
        return engine
