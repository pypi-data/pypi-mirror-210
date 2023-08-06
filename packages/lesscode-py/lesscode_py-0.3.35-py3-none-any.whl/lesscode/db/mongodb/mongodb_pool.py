# -*- coding: utf-8 -*-
import importlib

from lesscode.db.base_connection_pool import BaseConnectionPool


class MongodbPool(BaseConnectionPool):
    """
    mongodb 数据库链接创建类
    """

    def create_pool(self):
        print("mongodb create_pool")
        """
        创建mongodb 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        try:
            motor = importlib.import_module("motor")
        except ImportError:
            raise Exception(f"motor is not exist,run:pip install motor==2.5.1")
        info = self.conn_info
        if info.async_enable:
            host_str = info.host.split(",")
            hosts = ",".join([f"{host}:{info.port}" for host in host_str])
            conn_info_string = f"mongodb://{info.user}:{info.password}@{hosts}"
            if info.params:
                if info.params == "LDAP":
                    conn_info_string += "/?authMechanism=PLAIN"
                elif info.params == "Password":
                    conn_info_string += "/?authSource=admin"
                elif info.params == "X509":
                    conn_info_string += "/?authMechanism=MONGODB-X509"
            pool = motor.motor_tornado.MotorClient(conn_info_string)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        try:
            pymongo = importlib.import_module("pymongo")
        except ImportError:
            raise Exception(f"pymongo is not exist,run:pip install pymongo==3.13.0")
        info = self.conn_info
        host_str = info.host.split(",")
        hosts = ",".join([f"{host}:{info.port}" for host in host_str])
        conn_info_string = f"mongodb://{info.user}:{info.password}@{hosts}"
        if info.params:
            if info.params == "LDAP":
                conn_info_string += "/?authMechanism=PLAIN"
            elif info.params == "Password":
                conn_info_string += "/?authSource=admin"
            elif info.params == "X509":
                conn_info_string += "/?authMechanism=MONGODB-X509"
        pool = pymongo.MongoClient(conn_info_string)
        return pool
