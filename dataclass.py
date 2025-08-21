# -*- coding: utf-8 -*-
import types
import inspect
import sys
from fields import Field, ValidationError

def validate(field_name):
    """
    装饰器：为指定字段添加自定义验证函数
    
    用法:
    @validate("name")
    def custom_name_validator(self, value):
        if not value.isalnum():
            raise ValidationError("Name must be alphanumeric")
    """
    def decorator(func):
        func._validate_field = field_name
        return func
    return decorator


def dataclass(cls=None, **kwargs):
    """
    装饰器版本的dataclass，支持更灵活的使用方式
    
    用法:
    @dataclass
    class MyClass:
        name = StringField()
        
    或者:
    @dataclass(repr=False)
    class MyClass:
        name = StringField()
    """
    def wrap(cls):
        # 收集字段
        fields = {}
        validators = {}
        
        # 收集所有get_xxx格式的getter方法
        potential_getters = {}
        for key, val in cls.__dict__.items():
            if (callable(val) and
                key.startswith('get_') and
                hasattr(val, '__call__')):
                # 检查方法签名，确保它只接受self参数
                import inspect
                try:
                    if sys.version_info[0] >= 3:
                        sig = inspect.signature(val)
                        params = list(sig.parameters.keys())
                    else:
                        argspec = inspect.getargspec(val)
                        params = argspec.args

                    # 只有接受self参数的方法才被认为是getter
                    if len(params) == 1 and params[0] == 'self':
                        field_name = key[4:]  # 去掉'get_'前缀
                        potential_getters[field_name] = val
                except (TypeError, ValueError):
                    # 如果无法检查签名，跳过
                    pass

        # 收集Field字段和dataclass字段
        # 使用一个更直接的方法：检查类的所有基类和自身
        all_attrs = {}

        # 收集所有可能的属性，包括被覆盖的
        for base in reversed(cls.__mro__):
            if base is object:
                continue
            for key, val in base.__dict__.items():
                if key not in all_attrs:  # 只保存第一次遇到的（最具体的）
                    all_attrs[key] = val

        # 现在从所有属性中收集字段
        for key, val in all_attrs.items():
            if isinstance(val, Field):
                fields[key] = val
                val.name = key  # 设置字段名称
            elif (isinstance(val, type) and
                  hasattr(val, '_dataclass_fields')):
                # 这是一个dataclass类型的字段
                fields[key] = val

        # 不需要特殊处理，因为我们只收集get_xxx格式的方法

        # 收集自定义验证函数
        for key, val in cls.__dict__.items():
            if hasattr(val, '_validate_field'):
                field_name = val._validate_field
                if field_name not in validators:
                    validators[field_name] = []
                validators[field_name].append(val)

        # 设置字段信息
        cls._dataclass_fields = fields
        cls._dataclass_validators = validators

        # 收集所有get_xxx方法，用于属性访问
        cls._dataclass_getters = {}
        for field_name, getter in potential_getters.items():
            if field_name in fields:  # 只有对应字段存在的getter才被收集
                cls._dataclass_getters[field_name] = getter

        # 生成 __init__ 方法
        original_init = getattr(cls, '__init__', None)
        
        def __init__(self, **init_kwargs):
            # 设置初始化标志，避免在初始化过程中触发__setattr__验证
            # 直接设置到__dict__避免Python 2的__setattr__问题
            self.__dict__['_initializing'] = True

            # 如果有原始的__init__，先调用它（但跳过object.__init__）
            if original_init and original_init != object.__init__:
                try:
                    original_init(self)
                except TypeError:
                    # 如果原始__init__不接受参数，忽略错误
                    pass

            # 验证和设置字段值
            for key, value in init_kwargs.items():
                if key not in fields:
                    # 无效字段直接设置到实例，不做校验
                    self.__dict__[key] = value
                    continue

                # 获取字段定义
                field = fields[key]

                # 检查是否是dataclass类型的字段
                if (isinstance(field, type) and
                    hasattr(field, '_dataclass_fields') and
                    isinstance(value, dict)):
                    # 如果字段是dataclass类型且值是dict，直接实例化
                    try:
                        validated_value = field(**value)
                    except ValidationError as e:
                        if key not in str(e):
                            e.path = [key] + getattr(e, 'path', [])
                        raise
                elif isinstance(field, Field):
                    # 执行Field基础验证
                    try:
                        validated_value = field.validate(value)
                    except ValidationError as e:
                        if key not in str(e):
                            e.path = [key] + getattr(e, 'path', [])
                        raise
                else:
                    # 其他情况直接赋值
                    validated_value = value

                # 执行自定义验证
                if key in validators:
                    for validator in validators[key]:
                        try:
                            validator(self, validated_value)
                        except ValidationError as e:
                            if key not in str(e):
                                e.path = [key] + getattr(e, 'path', [])
                            raise

                # 直接设置到__dict__，避免触发__setattr__
                self.__dict__[key] = validated_value

            # 设置未提供值的字段的默认值
            for key, field in fields.items():
                if key not in init_kwargs:
                    if isinstance(field, Field):
                        default_value = field.get_default()
                        if default_value is not None:
                            self.__dict__[key] = default_value
                    # dataclass字段不设置默认值

            # 初始化完成，移除标志
            self.__dict__['_initializing'] = False

        cls.__init__ = __init__

        # 添加字段访问方法
        def _get_field_value(self, key):
            """获取字段值：统一处理自定义方法和字段值"""
            # 使用__getattribute__来获取值，这样可以统一处理getter方法
            try:
                return self.__getattribute__(key)
            except AttributeError:
                # 如果属性不存在，检查是否是定义的字段
                if hasattr(self, '_dataclass_fields') and key in self._dataclass_fields:
                    field = self._dataclass_fields[key]
                    if isinstance(field, Field):
                        return field.get_default()
                    return None

                # 如果不是定义的字段，但实例中有这个属性，直接返回
                if hasattr(self, '__dict__') and key in self.__dict__:
                    return self.__dict__[key]

                raise KeyError("Field '{0}' not found".format(key))

        def __getitem__(self, key):
            """支持通过 [] 访问属性"""
            try:
                return self._get_field_value(key)
            except KeyError:
                raise KeyError(key)

        def __setitem__(self, key, value):
            """支持通过 [] 设置属性"""
            if key in self._dataclass_fields:
                setattr(self, key, value)
            else:
                raise KeyError(key)
                
        def __getattribute__(self, name):
            # 避免无限递归，先获取必要的属性
            try:
                dataclass_getters = object.__getattribute__(self, '_dataclass_getters')
                # 检查是否正在执行getter方法（避免递归）
                try:
                    in_getter = object.__getattribute__(self, '_in_getter_call')
                except AttributeError:
                    in_getter = False
            except AttributeError:
                # 如果还没有初始化完成，使用默认行为
                return object.__getattribute__(self, name)

            # 如果正在执行getter方法，直接返回原始值（避免递归）
            if in_getter:
                return object.__getattribute__(self, name)

            # 如果有自定义getter方法，使用getter
            if name in dataclass_getters:
                getter = dataclass_getters[name]
                # 设置标志，表示正在执行getter
                object.__setattr__(self, '_in_getter_call', True)
                try:
                    result = getter(self)
                finally:
                    # 清除标志
                    object.__setattr__(self, '_in_getter_call', False)
                return result

            # 否则使用默认行为
            return object.__getattribute__(self, name)

        def __setattr__(self, name, value):
            """设置属性时，如果是 Field 字段，应重新验证"""
            # 如果正在初始化，直接设置属性
            if getattr(self, '_initializing', False):
                self.__dict__[name] = value
                return

            if hasattr(self, '_dataclass_fields') and name in self._dataclass_fields:
                field = self._dataclass_fields[name]

                # 检查是否是dataclass类型的字段
                if (isinstance(field, type) and
                    hasattr(field, '_dataclass_fields') and
                    isinstance(value, dict)):
                    # 如果字段是dataclass类型且值是dict，重新实例化
                    try:
                        validated_value = field(**value)
                    except ValidationError as e:
                        if name not in str(e):
                            e.path = [name] + getattr(e, 'path', [])
                        raise
                elif isinstance(field, Field):
                    # 执行Field基础验证
                    try:
                        validated_value = field.validate(value)

                        # 执行自定义验证
                        if hasattr(self, '_dataclass_validators') and name in self._dataclass_validators:
                            for validator in self._dataclass_validators[name]:
                                validator(self, validated_value)

                    except ValidationError as e:
                        if name not in str(e):
                            e.path = [name] + getattr(e, 'path', [])
                        raise
                else:
                    # 其他情况直接赋值
                    validated_value = value

                value = validated_value
            self.__dict__[name] = value

        def __contains__(self, key):
            return hasattr(self, '_dataclass_fields') and key in self._dataclass_fields

        def to_dict(self):
            """转换为字典"""
            result = {}

            # 添加所有实例属性（包括无效字段）
            for k, v in self.__dict__.items():
                if k.startswith('_'):  # 跳过私有属性
                    continue

                # 如果值是dataclass实例，递归转换为字典
                if hasattr(v, 'to_dict') and callable(getattr(v, 'to_dict')):
                    result[k] = v.to_dict()
                elif isinstance(v, list):
                    # 处理列表中的dataclass实例
                    result[k] = []
                    for item in v:
                        if hasattr(item, 'to_dict') and callable(getattr(item, 'to_dict')):
                            result[k].append(item.to_dict())
                        else:
                            result[k].append(item)
                else:
                    result[k] = v

            # 对于定义的字段但没有值的，尝试获取默认值
            if hasattr(self, '_dataclass_fields'):
                for k, field in self._dataclass_fields.items():
                    if k not in result and isinstance(field, Field):
                        default_value = field.get_default()
                        if default_value is not None:
                            result[k] = default_value

            return result

        def keys(self):
            return self._dataclass_fields.keys() if hasattr(self, '_dataclass_fields') else []

        def values(self):
            return [getattr(self, k) for k in self._dataclass_fields] if hasattr(self, '_dataclass_fields') else []

        def items(self):
            return [(k, getattr(self, k)) for k in self._dataclass_fields] if hasattr(self, '_dataclass_fields') else []

        def get(self, key, default=None):
            try:
                return getattr(self, key)
            except (AttributeError, KeyError):
                return default

        # 添加方法到类
        cls._get_field_value = _get_field_value
        cls.__getitem__ = __getitem__
        cls.__setitem__ = __setitem__
        cls.__getattribute__ = __getattribute__
        cls.__setattr__ = __setattr__
        cls.__contains__ = __contains__
        cls.to_dict = to_dict
        cls.keys = keys
        cls.values = values
        cls.items = items
        cls.get = get

        # 可选：生成 __repr__
        if kwargs.get('repr', True):
            def __repr__(self):
                if hasattr(self, '_dataclass_fields'):
                    args = ', '.join('%s=%r' % (k, self.__dict__.get(k, None)) for k in self._dataclass_fields)
                    return '%s(%s)' % (cls.__name__, args)
                return object.__repr__(self)
            cls.__repr__ = __repr__

        # 可选：生成 __eq__
        if kwargs.get('eq', True):
            def __eq__(self, other):
                if not isinstance(other, self.__class__):
                    return False
                if hasattr(self, '_dataclass_fields'):
                    return all(getattr(self, k, None) == getattr(other, k, None) for k in self._dataclass_fields)
                return object.__eq__(self, other)
            cls.__eq__ = __eq__

            def __ne__(self, other):
                return not self.__eq__(other)
            cls.__ne__ = __ne__

        return cls

    # 支持 @dataclass 和 @dataclass() 两种用法
    if cls is None:
        return wrap
    else:
        return wrap(cls)
