import dataclasses
from typing import Any, TypeVar, Type, Optional


T = TypeVar("T")


@dataclasses.dataclass
class BeanDefinition:
    # bean 的自定义名称
    name: str
    # bean 的包名称
    common_name: str
    # bean 的对象值
    value: Any
    # bean 的类
    class_type: Type

    @classmethod
    def build(cls, value: Any, name: str = None):
        class_type = value.__class__
        common_name = cls.build_common_name(class_type)
        name = name or common_name
        return cls(
            name=name, common_name=common_name, value=value, class_type=class_type
        )

    @classmethod
    def build_common_name(cls, class_type: Type):
        return f"{class_type.__module__}.{class_type.__name__}"


class ApplicationContext:
    """
    模拟Spring容器
    """

    def __init__(self):
        self.__context_name_map = {}

    def set_object(self, value: Any):
        bean_define = BeanDefinition.build(value)
        if bean_define.name in self.__context_name_map:
            raise Exception("容器内注入的对象发生冲突")
        self.__context_name_map[bean_define.name] = bean_define

    def get_type_object_first(self, clazz: Type[T]) -> Optional[T]:
        name = BeanDefinition.build_common_name(clazz)
        element = self.get_name_object(name)
        if element is not None:
            return element
        return None

    def get_name_object(self, name: str) -> Optional[T]:
        value: BeanDefinition = self.__context_name_map.get(name)
        if value is None:
            return None
        return value.value

    def contain_type(self, clazz: Type[T]):
        return clazz in self.__context_name_map
