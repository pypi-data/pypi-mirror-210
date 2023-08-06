# -*- coding: utf-8 -*-
import importlib

from lesscode.db.base_connection_pool import BaseConnectionPool


class MysqlPool(BaseConnectionPool):
    """
    mysql 数据库链接创建类
    """

    async def create_pool(self):
        """
        创建mysql 异步连接池
        :return:
        """
        try:
            aiomysql = importlib.import_module("aiomysql")
        except ImportError:
            raise Exception(f"pymysql is not exist,run:pip install aiomysql==0.0.22")
        if self.conn_info.async_enable:
            pool = await aiomysql.create_pool(host=self.conn_info.host, port=self.conn_info.port,
                                              user=self.conn_info.user,
                                              password=self.conn_info.password,
                                              pool_recycle=self.conn_info.params.get("pool_recycle", 3600)
                                              if self.conn_info.params else 3600,
                                              db=self.conn_info.db_name, autocommit=True,
                                              minsize=self.conn_info.min_size,
                                              maxsize=self.conn_info.max_size)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        try:
            pymysql = importlib.import_module("pymysql")
        except ImportError:
            raise Exception(f"pymysql is not exist,run:pip install pymysql==0.9.3")
        try:
            pooled_db = importlib.import_module("dbutils.pooled_db")
        except ImportError:
            raise Exception(f"DBUtils is not exist,run:pip install DBUtils==3.0.2")
        pool = pooled_db.PooledDB(creator=pymysql, host=self.conn_info.host, port=self.conn_info.port,
                                  user=self.conn_info.user,
                                  passwd=self.conn_info.password, db=self.conn_info.db_name,
                                  mincached=self.conn_info.min_size, blocking=True, maxusage=self.conn_info.min_size,
                                  maxshared=self.conn_info.max_size, maxcached=self.conn_info.max_size,
                                  ping=1, maxconnections=self.conn_info.max_size, charset="utf8mb4", autocommit=True,
                                  read_timeout=30)
        return pool
