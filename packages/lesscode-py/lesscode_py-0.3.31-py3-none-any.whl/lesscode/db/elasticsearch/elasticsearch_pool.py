# -*- coding: utf-8 -*-
import importlib

from lesscode.db.base_connection_pool import BaseConnectionPool

elasticsearch = None
try:
    elasticsearch = importlib.import_module("elasticsearch")
except ImportError as e:
    raise Exception(f"elasticsearch is not exist,run:pip install elasticsearch==7.15.2")


class ElasticsearchPool(BaseConnectionPool):
    """
    Elasticsearch 数据库链接创建类
    """

    async def create_pool(self):
        """
        创建elasticsearch 异步连接池
        :param conn_info: 连接信息
        :return:
        """
        info = self.conn_info
        if info.async_enable:
            host_str = info.host.split(",")
            hosts = [f"http://{info.user}:{info.password}@{host}:{info.port}" for host in host_str]
            pool = elasticsearch.AsyncElasticsearch(hosts=hosts)
            return pool
        else:
            raise NotImplementedError

    def sync_create_pool(self):
        info = self.conn_info
        host_str = info.host.split(",")
        hosts = [f"http://{info.user}:{info.password}@{host}:{info.port}" for host in host_str]
        pool = elasticsearch.Elasticsearch(hosts)
        return pool
