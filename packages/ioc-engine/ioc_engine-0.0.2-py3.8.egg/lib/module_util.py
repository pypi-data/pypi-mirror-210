import inspect
import logging
import pkgutil
from typing import Type, Set


def search_class(search_module: str, clazz_filter=None) -> Set[Type]:
    """
    search包下面的所以类文件
    :param search_module:   module类
    :param clazz_filter:    lambda clazz -> bool
    :return:
    """
    result_type_set = set()
    for finder, name, is_sub_pkg in pkgutil.walk_packages(
        path=search_module.__path__, prefix=search_module.__name__ + "."
    ):
        # 如果是父包名，跳过
        if is_sub_pkg:
            continue
        # 开始加载module
        logging.debug(f"{finder}, {name}, {is_sub_pkg}")
        module_loader = finder.find_module(name)
        try:
            module = module_loader.load_module(name)
        except Exception as e:
            logging.error(e)
            continue
        # search module下的所有类
        for clazz_name, clazz in inspect.getmembers(module, inspect.isclass):
            # 如果设置了filter，则过滤
            if clazz_filter is not None:
                if not clazz_filter(clazz):
                    continue
            result_type_set.add(clazz)
    return result_type_set


def search_sub_class(search_module: str, super_clazz: Type) -> Set[Type]:
    return search_class(
        search_module,
        lambda clazz: issubclass(clazz, super_clazz) and clazz != super_clazz,
    )
