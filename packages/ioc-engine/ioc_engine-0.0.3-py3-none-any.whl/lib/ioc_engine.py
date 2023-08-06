import functools
from typing import Type

from lib import function_util
from lib.application_context import ApplicationContext
from lib.exception import NoAutoScanException
from lib.function_util import FunctionParamsMeta


class AutoScan:
    """
    如果需要被自动扫描，需要继承这个类
    """


class ContextEngine:
    def __init__(self):
        self.application_context = ApplicationContext()

    def scan(self, clazz: Type):
        # 监测到还依赖于自动注入的类，递归加载依赖的类
        if not issubclass(clazz, AutoScan):
            raise NoAutoScanException(f"无法加载没有开启AutoScan的类, class:{clazz}")
        value = self.application_context.get_type_object_first(clazz)
        if value is not None:
            return value

        value = clazz.__new__(clazz)
        try:
            # 检测构造函数是否被重写
            getattr(clazz.__init__, "__annotations__")
        except:
            # condition: 无构造函数
            # 如果没有没有自定义__init__，直接初始化加返回
            clazz.__init__(value)
            self.application_context.set_object(value)
            return value

        # condition: 存在构造函数
        # 查找构造函数需要什么参数，将其构造成kwargs
        params = function_util.get_function_params_meta_list(clazz.__init__)
        kwargs = {}
        for param in params:
            if param.args_type == FunctionParamsMeta.ArgsTypeEnum.INSTANCE:
                kwargs["self"] = value
            else:
                # 监测到还依赖于自动注入的类，递归加载依赖的类
                if not issubclass(param.args_class, AutoScan):
                    raise NoAutoScanException(
                        f"class:{clazz} 无法加载没有开启AutoScan的类:{param.args_class}"
                    )
                kwargs[param.args_name] = self.scan(param.args_class)
        clazz.__init__(**kwargs)
        self.application_context.set_object(value)
        return value

    def autowire(self, func):
        """
        类似@Autowired
        :param func:
        :return:
        """

        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            application_context = self.application_context
            for meta in function_util.get_function_params_meta_list(func):
                if meta.args_type != FunctionParamsMeta.ArgsTypeEnum.NORMAL:
                    continue
                class_type = meta.args_class
                value = None
                if not self.application_context.contain_type(class_type):
                    value = self.scan(class_type)
                if value is None:
                    value = application_context.get_type_object_first(class_type)
                if meta.args_name not in kwargs:
                    kwargs[meta.args_name] = value
            result = func(*args, **kwargs)
            return result

        return inner_wrapper
