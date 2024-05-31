"""
封装一层Exception, 重新定义AssertError
目的是能在日志中输出断言失败的原因

"""
from hamcrest import assert_that, equal_to  # hamcrest断言库

from base.logger_and_requests import logger
from base.exception_class import *


class BaseTest:
    log = logger

    def assert_equal(self, actual, expect):
        """
        断言实际值等于期望值
        :param actual:
        :param expect:
        :return:
        """
        self.log.info(f"实际值={actual}， 期望值={expect}")
        try:
            assert_that(actual, equal_to(expect))  # equal_to匹配相等对象
        except AssertionError as e:
            self.log.error(e)
            self.log.eroor(f"捕获异常ActualNEExpectedError: 实际值={actual} !===! 期望值={expect}")
            raise ActualNEExpectedError(f"实际值={actual} !===! 期望值={expect}")
        else:
            self.log.info(f"{actual} == {expect}")

    def assert_not_equal(self, actual, expected):
        """
        断言实际值不等于期望值
        :param actual:
        :param expected:
        :return:
        """
        try:
            assert actual != expected
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f" ActualEQExpectedError: actual={actual} 预期不应该等于expected={expected}")
            raise ActualEQExpectedError(f" ActualEQExpectedError: actual={actual}预期不应该等于expected={expected}")

    def assert_any_not_equal(self, seq):
        """
        校验seq中的二维数组任意一组不相等
        :param seq:
        :return:
        """
        flag = False
        for item in seq:
            actual, expected = item
            if actual != expected:  # 如果actual与expected相等则flag值不变，assert时弹出错误提示
                flag = True
                break
        try:
            assert flag
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f"ActualEQExpectedError: seq={seq}中的每一组数据都相等, 不符合预期！！！")
            raise ActualEQExpectedError(f"ActualEQExpectedError: seq={seq}中的每一组数据都相等, 不符合预期！！！")

    def assert_api_code_success(self, r):
        """
        接口返回成功码断言,根据业务返回数据修改
        :param r:
        :return:
        """
        self.assert_equal(r["err_code"], 0)
        self.assert_equal(r["err_msg"], "ok")

    def assert_response_json(self):
        """
        todo 通过json schema 进行校验接口反回
        :return:
        """

    def assert_data_not_empty(self, r):

        data = r["data"]
        try:
            assert data
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f" ValueEmptyError: api返回体data字段为空, r['data'] = {data}")
            raise ValueEmptyError()

    def assert_not_empty(self, r: object, **kwargs) -> object:  # object定义r为对象
        """
        断言某一对象不为空
        :param r:
        :param kwargs:
        :return:
        """
        msg = kwargs.get('msg', None)
        try:
            assert r
        except AssertionError as e:
            err_info = f" ValueEmptyError: 字段实际返回值为空, value={r}"
            if msg:
                err_info = f" ValueEmptyError: 字段【{mag}】实际返回值为空, value=【{msg}】"
            self.log.error(e)
            self.log.error(err_info)
            raise ValueEmptyError(err_info)

    def assert_not_none(self, r):
        """
        断言当前对象的值不为None
        :return:
        """
        try:
            assert r is not None
        except AssertionError as e:
            self.log.error(f"ValueIsNoneError: 字段实际返回值为None(Null), value={r}")
            raise ValueIsNoneError(f"ValueIsNoneError: 字段实际返回值为None(Null), value={r}")

    def assert_value_in(self, value, seq):
        """
        断言某值在序列内
        :param value:
        :param seq:
        :return:
        """
        try:
            assert value in seq
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f" NotContainValueError: {value}不包含在序列{seq}！！！")
            raise NotContainValueError(f" NotContainValueError: {value}不包含在序列{seq}！！！")

    def assert_value_not_in_seq(self, value, seq):
        """
        断言某值不应在序列内
        :param value:
        :param seq:
        :return:
        """
        try:
            assert value not in seq
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f" ContainInvalidValueError: {value}不应该包含在序列{seq}！！！")
            raise ContainInvalidValueError(f" ContainInvalidValueError: {value}不应该包含在序列{seq}！！！")

    def assert_not_value(self, r, seq):
        """
        断言响应无值情况
        :param r:
        :param seq:
        :return:
        """
        self.assert_value_not_in_seq(r, seq)

    def assert_any_not_empty(self, seq: list):
        """
        断言seq列表不为空值
        :param seq:
        :return:
        """
        flag = True
        for s in seq:
            if s:
                assert flag
            return
        flag = False
        try:
            assert flag
        except AssertionError as e:
            self.log.error(e)
            self.log.error(f" ValuesEmptyError: seq中所有的值都为空, seq={seq}")
            raise ValuesEmptyError(f" ValuesEmptyError: seq中所有的值都为空, seq={seq}")

    def assert_rsp_json(self, map_info: dict):
        """
        校验Test发布后应该返回的对应json (map_json, props_json, clothea_json, space_json)
        按业务区分是否需要此断言，或需更改校验json
        :param map_info:
        :return:
        """
        map_json = map_info.get("mapJson", None)
        props_json = map_info.get("propsJson", None)
        clothes_json = map_info.get("clothesJson", None)
        clothes_url = map_info.get("clothesUrl", None)
        self.assert_any_not_empty([map_json, props_json, clothes_json, clothes_url])
