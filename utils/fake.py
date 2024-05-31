"""
Todo: 假数据生成，由faker包封装
暂时不需要用到
"""
from faker import Faker


class Fake:

    __faker_1 = Faker()   #多套环境可以创建多个Faker()
    # __faker_2 = Faker('zh_CN')
    # __faker_3 = Faker('en_US')
    print(__faker_1.name()[:12])

    # @property   #通过 @property 装饰器，可以直接通过方法名来访问方法，不需要在方法名后添加一对“（）”小括号
    # def