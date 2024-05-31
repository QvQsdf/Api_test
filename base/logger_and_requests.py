import copy
import json
import sys
from datetime import datetime
from json import JSONDecodeError
from websocket import create_connection, WebSocketTimeoutException

import requests

from utils.log import Logger, log_api_cost

try:
    log_file_name = ".".join(sys.argv[1].replace(".py::", ".").replace("::", ".").split(".")[-2:])
    # 命令行执行时对日志命进行重命名 如：python my.py --version -y | sys.argv[1]指的是"--version"
except:
    log_file_name = "base_api.py兜底文件名"
    # 直接在文件夹下执行时，不加参数的pytest命令，期望是带文件夹的名字作为log_file_name

# 日志级别设置：BEBUG  INFO  WARN  ERROR  CRITICAL  如果不想输出INFO的日志，可以将日志级别设置为：WARN  ERROR CRITICAL
logger = Logger(log_file_name, level="INFO").logger  # 去掉INFO级别日志
logger.info("<== logger 初始化完成，开始收集日志 ==>")
logger.info(f"log主文件路径={log_file_name}")


def cast_param_to_req_bady_key(param: str):
    """
    装换接口业务层函数的传入参数，变为请求体的key
    需根据不同业务类型定义，仅供参考
    :param param:
    :return:
    """

    if "_" not in param:
        return param

    res = []

    for i in range(len(param)):
        if i == 0:  # 第一位一般为url，直接返回
            temp = param[i]
        elif param[i] == "_":  # 为“_”跳过
            continue
        elif param[i - 1] == "_" and i < len(param) and param[i].isalpha():  # isalpha()判断是否为英文字母
            temp = param[i].upper()  # upper()所有字符装换为大写，只能用于字符串
        else:
            temp = param[i]

        res.append(temp)

    return "".join(res)


def get_req_body(req: dict, is_tp_uid=False):
    """
    获取HTTP业务接口req参数
    :param req:
    :param is_tp_uid:
    :return:
    """
    req_data = {}
    body = {}

    for k, v in req.items():
        if k in ["self", "kwargs", "version"] or v is None or v == "":
            continue
        elif k in ["h", "header", "headers"]:
            req_data["headers"] = v
        elif k in ["path", "p"]:
            req_data["path"] = v
        elif k == "name":  # 传入参数内增加“name”标明接口名称
            req_data[k] = v
        elif not is_tp_uid and k == "uid":  # is_tp_uid传为true时，用默认数据层的uid，不使用传参内的uid
            continue
        else:
            req_key = cast_param_to_req_bady_key(k)
            body[req_key] = v

    if req_data.get("headers", None) is None:
        uid = req.get("uid", None)  # 兜底，若req内headers为空，取req内的uid
        if uid is None:
            pass
            # raise ValueError("传入handle_req_params的locals()中既未传入headers相关，也为传入uid参数！！！")
        else:
            req_data["headers"] = {"uid": uid}  # 兜底，header给的就是uid，则变更键值
    req_data['params'] = body
    return req_data


class BaseApi:

    def __init__(self):
        self.log = logger

    @log_api_cost
    def request(self, req: dict):

        if req.get("protocol", None) == "websocket":
            return self.websocket_request(req)

        return self.http_request(req)

    def websocket_request(self, req):
        pass

    def http_request(self, req: dict):

        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间，格式为str
        self.log.info(f"-------------------接口请求开始，开始时间【{t}】-------------------")
        self.log.info(f"接口名称：{req.get("name", "not setting api name")}")
        self.log.info(f"请求方式:{req.get("method")}")
        self.log.info(f"请求路径：{req.get("url")}")

        req.pop("name", None)
        tmp = []
        for k in req.keys():
            if k not in ["method", "json", "param", "url", "data", "headers", "cookies", "files", "auth",
                         "timeout", "allow_redirects", "proxies", "hooks", "stream", "verify",
                         "cert"]:  # 兜底，弹出req内非必要参数（根据公司业务而定）
                tmp.append(k)
        for k in tmp:
            req.pop(k, None)
        # 再次处理错误SSLError(MaxRetryError("HTTPSConnectionPool(host='api-test.joinbudapp.com', port=443)，如果出现再加上此兜底
        # 根据公司业务写死固定参数
        req["verify"] = False
        # 拷贝一份req在日志上输出，只需要输出关键信息
        data = copy.deepcopy(req)
        data.pop("method")
        data.pop("url")
        data.pop("header", None)
        data.pop("name", None)
        self.log.info(f"REQ ==> 请求参数：{json.dumps(data, indent=4, ensure_ascii=False)}")  # 将所需的请求体以json格式写入日志文件
        r = requests.request(**req)
        self.log.info(f"返回状态码：【{r.status_code}】")  # 根据业务修改
        if r.status_code in (500, 501, 502, 503):
            self.log.error(f"ServerRSPError: 服务器返回状态码={r.status_code}, 服务器出错")
            from base.exception_class import ServerRSPError
            raise ServerRSPError(f"ServerRSPError: 服务器返回状态码={r.status_code}, 服务器出错")
        try:
            rsp = r.json()
            r.encoding = "utd-8"
            self.log.info(f"RSR ==> 返回响应: {json.dumps(rsp, indent=4, ensure_ascii=False)}")  # 将响应以json格式写入日志文件
        except JSONDecodeError:
            self.log.error(f"捕获JSONDecodeError  ==>  返回体不能转换为json体 r.content = {r.content}")
            self.log.error(f"捕获JSONDecodeError  ==>  返回体不能转换为json体 r.text= {r.text}")
            raise JSONDecodeError(f"返回体捕获JSONDecodeError，r.text === {r.text}", f"r.content = {r.content}",
                                  "line 148")
        self.log.info("----------------------接口请求结束-----------------------")
        return r

    def get(self, req: dict):

        req['method'] = 'GET'
        return self.request(req)

    def post(self, req: dict):

        req['method'] = "POST"
        req['headers']["Content-Type"] = "application/json"
        return self.request(req)

    def head(self, req: dict):

        req['method'] = "HEAD"
        return self.request(req)

    def delete(self, req: dict):

        req["method"] = "DELETE"
        return self.request(req)

    def options(self, req: dict):

        req['method'] = "OPTIONS"
        return self.request(req)

    def handle_req_params(self, params: dict, is_tp_uid=False):
        """
        处理请求参数
        Todo 处理嵌套参数能力{“a":{'b':type_b}}
        :param params:
        :param is_tp_uid:
        :return:
        """
        args = params.get("args", None)
        if not args:
            if isinstance(params, dict):  # 传入的params是否字典格式
                return get_req_body(params, is_tp_uid=is_tp_uid)  # 字典用get_req_body方法处理
            else:
                raise ValueError(f"传入解析的参数不是字典！！！ params = {params}")  # 非字典报异常
        return get_req_body(args, is_tp_uid=is_tp_uid)

    # 以下为websocket + python的请求封装

    def conn(self, uri, timeout=3):
        """
        连接web服务器
        :param uri:
        :param timeout:
        :return:
        """
        self.wss = create_connection(uri, timeout=timeout)  # uri是一个在线回环websocket接口，必须以websocket的方式连接后访问，无法直接在网页端输入该地址访问

    def send(self, message):
        """
        发送websocket请求数据体
        :param message:
        :return:
        """
        if not isinstance(message, str):
            message = json.dumps(message)  # websocket不支持直接发送除字符串以为的其他数据类型，所以要转成json字符串
        self.log.info(f"发送的message={message}")
        return self.wss.send(message)  # 发送websocket消息

    def handle_json(self, base_req):
        """
        websocket返回的数据体信息处理，字符串转换为字典，列表内的值再进行handle_json处理加入列表内，字典处理后输出字典
        :param base_req:
        :return:
        """
        if isinstance(base_req, str):  # isinstance()判断一个对象是否是一个已知的类型，返回bool值
            try:
                res = json.loads(base_req)  # json.loads()把json字符串装换为python对象（一般为dict），功能与json.dumps()相反
                return self.handle_json(res)
            except JSONDecodeError:
                return base_req

        elif isinstance(base_req, list):
            res = []
            for i in base_req:
                res.append(self.handle_json(i))
            return res

        elif isinstance(base_req, dict):
            for k, v in base_req.items():
                base_req[k] = self.handle_json(v)
            return base_req

        return base_req

    def set_timeout(self, timeout):
        """
        websocket连接设置超时时间
        :param timeout:
        :return:
        """
        self.wss.settimeout(timeout)

    def recv(self, timeout=3):
        """
        接受websocket的数据体信息
        :param timeout:
        :return:
        """
        if isinstance(timeout, dict):
            timeout = timeout['timeout']
        try:
            self.set_timeout(timeout)
            recv_json = self.wss.recv()  # 接收websocket消息
            all_json_recv = self.handle_json(recv_json)  # 将返回数据体信息处理成python对象
            self._set_response(all_json_recv)
            return all_json_recv
        except WebSocketTimeoutException:
            self.log.error(f"超过{timeout}秒没有接收数据！！！")

    def recv_all(self, timeout=3):
        """
        接收多个数据体信息，并调用数据体处理方法handle_json处理响应体
        :param timeout:
        :return:
        """
        if isinstance(timeout, dict):
            timeout = timeout['timeout']
        recv_list = []
        while True:
            try:
                self.set_timeout(timeout)
                recv_json = self.wss.recv()  # 接收websocket消息
                all_recv_json = self.handle_json(recv_json)  # 将响应消息经过处理后放入列表
                recv_list.append(all_recv_json)
                self.log.info(f"收到的所有数据 ===> {all_recv_json}")
            except WebSocketTimeoutException:  # 超时异常
                self.log.error(f"超过{timeout}秒没有接收到数据！！！")
                break
        self._set_response(recv_list)
        return recv_list

    def _set_response(self, rsp):  # 响应集合
        self.response = rsp

    def _get_response(self, rsp):  # 获取响应并return
        return self.response

    def close(self):
        """
        关闭连接
        :return:
        """
        return self.wss.close()
