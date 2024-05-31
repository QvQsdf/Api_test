"""
封装请求方法
"""
from base import BaseApi


class DOMEApi(BaseApi):  # 类方法，自动将类对象作为第一个参数传递，DOMApi为子类，自动继承父类BaseApi中的方法，可在子类中直接调用父类方法

    def __init__(self, env=None, host=None, token=None, version=None):
        super(DOMEApi, self).__init__()  # 子类B与父类A中都有_init__方法时，A类中的__init__会被B类的覆盖，所以使用super()调用
        self.env = env
        self.host = host
        self.token = token
        self.version = version

    def handle_token(self):
        """
        token前置处理
        :return:
        """


    def post_headers(self, req=None, **kwargs):
        """
        前置处理headers及**kwargs传入的参数
        :return:
        """
        if req and kwargs:
            for k, v in kwargs.items():  #请求参数从**kwargs传入，放入req内
                req[k] = v
        self.handle_token



    def Dome_get(self):

        #处理自定义传入的一些参数，比如token
        req, herders = self.post_headers(req, path, headers, **kwargs)
