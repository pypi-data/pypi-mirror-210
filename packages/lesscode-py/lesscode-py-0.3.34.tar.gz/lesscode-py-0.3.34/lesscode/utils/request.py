import importlib
import random

import tornado.options

from lesscode.web.business_exception import BusinessException
from lesscode.web.status_code import StatusCode


async def post(path, data=None,
               base_url=tornado.options.options.data_server,
               result_type="json", pack=False, **kwargs):
    try:
        aiohttp = importlib.import_module("aiohttp")
    except ImportError as e:
        raise Exception(f"aiohttp is not exist,run:pip install aiohttp==3.8.3")

    project_name = tornado.options.options.project_name.encode("utf-8")
    flag = kwargs.pop("flag", True)
    if flag:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Content-Type": "application/json",
                "Project-Name": project_name
            }})
        else:
            kwargs["headers"].update({"Project-Name": project_name})
    else:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Project-Name": project_name
            }})
        else:
            kwargs["headers"].update({"Project-Name": project_name})
    async with aiohttp.ClientSession() as session:
        flag = kwargs.pop("flag", True)
        if flag:
            async with session.post(base_url + path, json=data, **kwargs) as resp:
                if result_type == "json":
                    result = await resp.json()
                    if not pack:
                        if result.get("status") == "00000":
                            result = result.get("data")
                        else:
                            message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                            raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
                elif result_type == "text":
                    result = await resp.text()
                else:
                    result = await resp.content.read()
                return result
        else:
            async with session.post(base_url + path, data=data, **kwargs) as resp:
                if result_type == "json":
                    result = await resp.json()
                    if not pack:
                        if result.get("status") == "00000":
                            result = result.get("data")
                        else:
                            message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                            raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
                elif result_type == "text":
                    result = await resp.text()
                else:
                    result = await resp.content.read()
                return result


async def get(path, params=None, base_url=tornado.options.options.data_server, result_type="json", pack=False,
              **kwargs):
    try:
        aiohttp = importlib.import_module("aiohttp")
    except ImportError as e:
        raise Exception(f"aiohttp is not exist,run:pip install aiohttp==3.8.3")
    project_name = tornado.options.options.project_name.encode("utf-8")
    if not kwargs.get("headers"):
        kwargs.update({"headers": {
            "Project-Name": project_name
        }})
    else:
        kwargs["headers"].update({"Project-Name": project_name})

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url + path, params=params, **kwargs) as resp:
            if result_type == "json":
                result = await resp.json()
                if not pack:
                    if result.get("status") == "00000":
                        result = result.get("data")
                    else:
                        message = f'ori_message:{result.get("status", "")}, {result.get("message", "未知错误")}'
                        raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
            elif result_type == "text":
                result = await resp.text()
            else:
                result = await resp.content.read()
            return result


def sync_common_request(method, path, params=None, data=None, json=None, base_url=None, result_type="json",
                        pack=False, connect_config=None, **kwargs):
    try:
        requests = importlib.import_module("requests")
        requests_adapters = importlib.import_module("requests.adapters")
    except ImportError as e:
        raise Exception(f"requests is not exist,run:pip install requests==2.27.1")
    project_name = tornado.options.options.project_name.encode("utf-8")
    if not base_url:
        base_url = tornado.options.options.data_server
    if not kwargs.get("headers"):
        kwargs.update({"headers": {
            "Project-Name": project_name
        }})
    else:
        kwargs["headers"].update({"Project-Name": project_name})
    if not connect_config:
        connect_config = {
            "pool_connections": 10,
            "pool_maxsize": 10,
            "max_retries": 0,
            "pool_block": False
        }
    s = requests.session()
    if connect_config and isinstance(connect_config, dict):
        adapter = requests_adapters.HTTPAdapter(**connect_config)
        s.mount(prefix="http", adapter=adapter)
        s.mount(prefix="https", adapter=adapter)
    try:
        if method == "GET":
            res = s.get(base_url + path, params=params, data=data, json=json, **kwargs)
        elif method == "POST":
            res = s.post(base_url + path, params=params, data=data, json=json, **kwargs)
        elif method == "PUT":
            res = s.put(base_url + path, params=params, data=data, json=json, **kwargs)
        elif method == "PATCH":
            res = s.patch(base_url + path, params=params, data=data, json=json, **kwargs)
        elif method == "DELETE":
            res = s.delete(base_url + path, params=params, data=data, json=json, **kwargs)
        else:
            raise Exception(f"method={method} is not allowed")
    except Exception as e:
        raise e
    finally:
        s.close()
    if result_type == "json":
        res = res.json()
        if not pack:
            if res.get("status") == "00000":
                res = res.get("data")
            else:
                message = f'ori_message:{res.get("status", "")}, {res.get("message", "未知错误")}'
                raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
    elif result_type == "text":
        res = res.text
    else:
        res = res.content
    return res


def sync_get(path, params=None, base_url=None, result_type="json", pack=False, connect_config=None, **kwargs):
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    res = sync_common_request(method="GET", path=path, params=params, base_url=base_url,
                              result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
    return res


def sync_post(path, data=None,
              base_url=None,
              result_type="json", pack=False, connect_config=None, **kwargs):
    flag = kwargs.pop("flag", True)
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if flag:
        res = sync_common_request(method="POST", path=path, json=data, base_url=base_url,
                                  result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
        return res
    else:
        res = sync_common_request(method="POST", path=path, data=data, base_url=base_url,
                                  result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
        return res


def sync_patch(path, params=None, data=None, json=None, base_url=None,
               result_type="json", pack=False, connect_config=None, **kwargs):
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    res = sync_common_request(method="PATCH", path=path, params=params, data=data, json=json, base_url=base_url,
                              result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
    return res


def sync_put(path, params=None, data=None, json=None, base_url=None,
             result_type="json", pack=False, connect_config=None, **kwargs):
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    res = sync_common_request(method="PATCH", path=path, params=params, data=data, json=json, base_url=base_url,
                              result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
    return res


def sync_delete(path, params=None, data=None, json=None, base_url=None,
                result_type="json", pack=False, connect_config=None, **kwargs):
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    res = sync_common_request(method="DELETE", path=path, params=params, data=data, json=json, base_url=base_url,
                              result_type=result_type, pack=pack, connect_config=connect_config, **kwargs)
    return res


def eureka_request(path="", return_type="json", method="GET", data=None, app_name="DATA_SERVICE", pack=False, **kwargs):
    flag = kwargs.pop("flag", True)
    if flag:
        if not kwargs.get("headers"):
            kwargs.update({"headers": {
                "Content-Type": "application/json"
            }})
    try:
        eureka_client = importlib.import_module("py_eureka_client.eureka_client")
    except ImportError as e:
        raise Exception(f"py-eureka-client is not exist,run:pip install py-eureka-client==0.11.3")
    res = eureka_client.eureka_client.do_service(app_name=app_name, service=path, return_type=return_type,
                                                 method=method, data=data,
                                                 **kwargs)
    if return_type == "json" and not pack:
        if not pack:
            if res.get("status") == "00000":
                res = res.get("data")
            else:
                message = f'ori_message:{res.get("status", "")}, {res.get("message", "未知错误")}'
                raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))
    return res


def eureka_get(path="", data=None, return_type="json", app_name="DATA_SERVICE", pack=False, **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")

    if tornado.options.options.running_env != "local":

        res = eureka_request(path=path, return_type=return_type, method="GET", data=data, app_name=app_name, pack=pack,
                             **kwargs)
    else:
        res = sync_get(path=path, params=data, base_url=base_url,
                       result_type=return_type,
                       pack=pack, **kwargs)
    return res


def eureka_post(path="", data=None, return_type="json", app_name="DATA_SERVICE", pack=False, **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":
        import json
        res = eureka_request(path=path, return_type=return_type, method="POST", data=json.dumps(data),
                             app_name=app_name,
                             pack=pack, **kwargs)
    else:
        res = sync_post(path=path, data=data, base_url=base_url,
                        result_type=return_type,
                        pack=pack, **kwargs)
    return res


def nacos_service_instance(service_name, namespace, clusters=None, group_name=None):
    server_addresses = tornado.options.options.nacos_config.get("server_addresses")
    try:
        nacos = importlib.import_module("nacos")
    except ImportError as e:
        raise Exception(f"nacos-sdk-python is not exist,run:pip install nacos-sdk-python==0.1.8")
    client = nacos.NacosClient(server_addresses=server_addresses, namespace=namespace)
    service = client.list_naming_instance(service_name=service_name, clusters=clusters, group_name=group_name,
                                          healthy_only=True)
    service_hosts = service.get("hosts")
    if service_hosts:
        service_host = random.choice(service_hosts)
        return service_host
    else:
        message = f'ori_message:service_name={service_name} has no healthy instance'
        raise BusinessException(StatusCode.COMMON_CODE_MESSAGE("C0001", message))


def nacos_get(path, params=None, service_name=None, namespace="public", clusters=None, group_name=None,
              pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":
        service_instance = nacos_service_instance(service_name=service_name,
                                                  namespace=namespace, clusters=clusters, group_name=group_name)
        base_url = f'http://{service_instance.get("ip")}:{service_instance.get("port")}'

    res = sync_get(path=path, params=params, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
    return res


def nacos_post(path, data=None, service_name=None, namespace="public", clusters=None, group_name=None,
               pack=False, return_type="json", **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.running_env != "local":
        service_instance = nacos_service_instance(service_name=service_name,
                                                  namespace=namespace, clusters=clusters, group_name=group_name)
        base_url = f'http://{service_instance.get("ip")}:{service_instance.get("port")}'

    res = sync_post(path=path, data=data, base_url=base_url, result_type=return_type, pack=pack, **kwargs)
    return res


def common_get(path, params=None, service_name=None, namespace="public", clusters=None, group_name=None,
               pack=False, return_type="json", connect_config=None, **kwargs):
    base_url = tornado.options.options.data_server
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.request_type == "request":
        res = sync_get(path=path, params=params, base_url=base_url, result_type=return_type, pack=pack,
                       connect_config=connect_config, **kwargs)
        return res
    elif tornado.options.options.request_type == "eureka":
        res = eureka_get(path=path, data=params, return_type=return_type, app_name=service_name, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "nacos":
        res = nacos_get(path=path, params=params, service_name=service_name, namespace=namespace, clusters=clusters,
                        group_name=group_name, pack=pack, return_type=return_type, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)


def common_post(path, data=None, service_name=None, namespace="public", clusters=None, group_name=None,
                pack=False, return_type="json", connect_config=None, **kwargs):
    base_url = tornado.options.options.data_server
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.request_type == "request":
        res = sync_post(path=path, data=data, base_url=base_url, result_type=return_type, pack=pack,
                        connect_config=connect_config, **kwargs)
        return res
    elif tornado.options.options.request_type == "eureka":
        res = eureka_post(path=path, data=data, return_type=return_type, app_name=service_name, pack=pack, **kwargs)
        return res
    elif tornado.options.options.request_type == "nacos":
        res = nacos_post(path=path, data=data, service_name=service_name, namespace=namespace, clusters=clusters,
                         group_name=group_name,
                         pack=pack, return_type=return_type, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)


def common_put(path, params=None, data=None, json=None, pack=False, return_type="json", connect_config=None, **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if tornado.options.options.request_type == "request":
        res = sync_put(path=path, params=params, data=data, json=json,
                       base_url=base_url, result_type=return_type, pack=pack, connect_config=connect_config, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)


def common_patch(path, params=None, data=None, json=None, pack=False, return_type="json", connect_config=None,
                 **kwargs):
    base_url = tornado.options.options.data_server
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if tornado.options.options.request_type == "request":
        res = sync_patch(path=path, params=params, data=data, json=json,
                         base_url=base_url, result_type=return_type, pack=pack, connect_config=connect_config, **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)


def common_delete(path, params=None, data=None, json=None, pack=False, return_type="json", connect_config=None,
                  **kwargs):
    base_url = tornado.options.options.data_server
    if connect_config is None:
        connect_config = tornado.options.options.connect_config
    if kwargs.get("base_url") is not None:
        base_url = kwargs.pop("base_url")
    if tornado.options.options.request_type == "request":
        res = sync_delete(path=path, params=params, data=data, json=json,
                          base_url=base_url, result_type=return_type, pack=pack, connect_config=connect_config,
                          **kwargs)
        return res
    else:
        raise BusinessException(StatusCode.UNSUPPORTED_REQUEST_TYPE)
