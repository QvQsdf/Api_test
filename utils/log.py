# 日志模块封装
import logging
import time
import os
from functools import wraps


class Logger:

    def __init__(self, logger_name=__name__, level="INFO"):
        # 使用logging模块产生logger对象 通用写法输出日志中显示年月日时分秒 AM、PM
        logging.basicConfig(datefmt="%Y-%m-%d%I:%M:%S %P")
        # 创建一个日志对象，这个参数可以随便填写，作用是唯一标识了这个日志对象(固定写法)
        self.logger = logging.getLogger(logger_name)
        # 设置日志级别(固定写法)
        self.logger.setLevel(getattr(logging, level))
        # 设置日志路径

        # 绝对路径--不推荐
        # log_abs_path = "C:\Users\armstrong\PycharmProjects\Test_Api_Dome\log"

        at = time.strftime("%Y_%m_%d_%H_%M", time.localtime(time.time()))  # 获取系统当前时间

        # 存放在相对执行位置下文件夹
        # current_path = os.path.dirname(os.path.realpath(__file__))  #去掉脚本的文件名，返回目录(固定写法)

        # 获取项目的根路径
        root_dir = os.path.abspath(os.path.dirname(__file__)).split('Test_Api_Dome')[0] + 'Test_Api_Dome/'
        # 返回上一层路径的绝对路径，将后面层具体路径替换成工程路径
        print(f"root_dir ={root_dir}")

        log_real_path = os.path.join(root_dir, 'log/')  # 定义日志存放地址为工程目录下log文件夹PycharmProjects\Test_Api_Dome/log/

        # 日志文件名
        log_file_name = log_real_path + str(logger_name) + '_' + 'dome_api_auto_test' + '.log'

        # todo 支持分布式运行. 1 随机字符  2 线程ID
        # 创建Handler，用于写入日志文件，a表示追加，encoding默认为ASCII，中文会显示乱码
        file_handler = logging.FileHandler(log_file_name, 'w', encoding='utf-8')  # 将日志文件写入log目录
        # 为logger添加日志处理器
        self.logger.addHandler(file_handler)
        # 设置日志输出格式  Formatter的默认格式包括时间戳、日志级别、日志名称和消息内容等信息。可以根据需求自定义格式
        # 固定写法：创建一个格式化器，并将其绑定到处理器
        formatter = logging.Formatter('%(asctime)s => %(filename)s[line:%(lineno)d] * %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)

    def fun(self):
        self.logger.error("this is err log.")
        self.logger.info("this is info log.")
        self.logger.debug("this is debug log.")
        self.logger.warning("this is waring log.")


def log_api_cost(func):
    """
    except Exception as e:：捕获所有异常，并将异常实例赋值给变量e,
    logger.error(repr(e))：使用日志模块（logger）记录异常的详细信息，repr(e)将异常e以字符串形式输出，通常会包含异常的类型和详细信息,
    raise e：重新抛出捕获的异常e，使得异常可以被上层代码捕获处理或者终止程序.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):  # wrapper包装器 用于将一个类或函数包装成另一个类或函数；主要目的是添加新的功能或修改现有功能，而不需修改原始类或函数的代码
        from base import logger
        start = 1000 * time.time()
        logger.info(f"===============  Begin func.__name__:{func.__name__}  ===============")

        try:
            rsp = func(*args, **kwargs)
            end = 1000 * time.time()
            logger.info(f"Api Time Cost: {end - start}ms")  # 日志输出接口请求耗时
            return rsp
        except Exception as e:
            logger.error(repr(e))
            raise e

    return wrapper
