# -*- coding: utf-8 -*-
import sys
import inspect
from .fields import Field, ValidationError

DATACLASS_FIELDS = "_dataclass_fields"
DATACLASS_GETTERS = "_dataclass_getters"

INIT_FLAG = "_initializing"
IN_GETTER = "_in_getter"
CUSTOM_GET_VALUE_FUNCTION_NAME_PREFIX = "get_"

FIELD_OBJECT = '_object'
FIELD_INSTANCE = '_instance'

def validate(field_name):
    """
    装饰器：为指定字段添加自定义验证函数
    """
    def decorator(func):
        func._validate_field = field_name
        return func
    return decorator


def dataclass(cls=None, **kwargs):
    """
    装饰器版本的 dataclass，支持更灵活的使用方式
    """

    def wrap(cls):
        # 收集字段、getter、验证器
        fields = _collect_fields(cls)
        getters = _collect_getters(cls, fields)
        validators = _collect_validators(cls)

        # 注入元数据
        cls._dataclass_fields = fields
        cls._dataclass_getters = getters
        cls._dataclass_validators = validators

        # 生成 __init__
        original_init = getattr(cls, "__init__", None)
        cls.__init__ = _make_init(cls, fields, validators, original_init)

        # 添加属性访问支持
        cls.__getitem__ = lambda self, key: self._get_field_value(key)
        cls.__setitem__ = lambda self, key, value: setattr(self, key, value)
        cls.__contains__ = lambda self, key: key in getattr(self, DATACLASS_FIELDS, {})

        # 重写 __getattribute__ 以支持 get_xxx 方法
        cls.__getattribute__ = _make_getattribute(getters)
        cls.__setattr__ = _make_setattr(fields, validators)

        # 实用方法
        cls._get_field_value = _make_get_field_value()
        cls.to_dict = _make_to_dict()
        cls.keys = lambda self: iter(getattr(self, DATACLASS_FIELDS, {}).keys())
        cls.values = lambda self: [getattr(self, k) for k in self.keys()]
        cls.items = lambda self: [(k, getattr(self, k)) for k in self.keys()]
        cls.get = lambda self, key, default=None: getattr(self, key, default)

        # 可选方法
        if kwargs.get("repr", True):
            cls.__repr__ = lambda self: "%s(%s)" % (
                type(self).__name__,
                ", ".join("%s=%r" % (k, self.__dict__.get(k)) for k in self._dataclass_fields)
            )

        if kwargs.get("eq", True):
            cls.__eq__ = lambda self, other: (
                isinstance(other, type(self)) and
                all(getattr(self, k, None) == getattr(other, k, None) for k in self._dataclass_fields)
            )
            cls.__ne__ = lambda self, other: not self.__eq__(other)

        return cls

    return wrap if cls is None else wrap(cls)


# ================== 收集逻辑 ==================
def _collect_fields(cls):
    """收集所有 Field 字段"""
    fields = {}
    all_attrs = {}

    # 从 MRO 中收集所有属性（保留最具体的）
    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for k, v in base.__dict__.items():
            if k not in all_attrs:
                all_attrs[k] = v

    for key, val in all_attrs.items():
        if isinstance(val, Field):
            val.name = key
            fields[key] = val
        elif isinstance(val, type) and hasattr(val, DATACLASS_FIELDS):
            fields[key] = (FIELD_OBJECT, val)
        elif hasattr(val, DATACLASS_FIELDS):
            fields[key] = (FIELD_INSTANCE, val.__class__, val)
    return fields


def _collect_getters(cls, fields):
    """收集 get_xxx 格式的 getter 方法"""
    getters = {}
    for key, val in cls.__dict__.items():
        if not (callable(val) and key.startswith(CUSTOM_GET_VALUE_FUNCTION_NAME_PREFIX)):
            continue
        field_name = key[4:]
        if field_name not in fields:
            continue
        try:
            args = inspect.getargspec(val).args if sys.version_info[0] < 3 \
                else list(inspect.signature(val).parameters.keys())
            if len(args) == 1 and args[0] == "self":
                getters[field_name] = val
        except (TypeError, ValueError):
            pass  # 无法分析签名，跳过
    return getters


def _collect_validators(cls):
    """收集自定义验证函数"""
    validators = {}
    for key, val in cls.__dict__.items():
        if hasattr(val, "_validate_field"):
            field = val._validate_field
            validators.setdefault(field, []).append(val)
    return validators


def _make_get_field_value():
    def _get_field_value(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            fields = getattr(self, DATACLASS_FIELDS, {})
            if key in fields:
                field = fields[key]
                if isinstance(field, tuple) and field[0] == FIELD_INSTANCE:
                    return field[2]  # 返回默认实例
                elif isinstance(field, Field):
                    return field.get_default()
                return None
            if key in self.__dict__:
                return self.__dict__[key]
            raise KeyError("Field '{}' not found".format(key))
    return _get_field_value

def _make_getattribute(getters):
    def __getattribute__(self, name):
        # 安全获取元数据
        try:
            fields = object.__getattribute__(self, DATACLASS_FIELDS)
            getters_map = object.__getattribute__(self, DATACLASS_GETTERS)
        except AttributeError:
            return object.__getattribute__(self, name)

        # 检查是否在 getter 调用中（防止递归）
        try:
            in_getter = object.__getattribute__(self, IN_GETTER)
        except AttributeError:
            in_getter = False

        # 如果正在执行 getter，跳过 getter 逻辑，直接取值
        if in_getter and name in getters_map:
            try:
                value = object.__getattribute__(self, name)
                if isinstance(value, Field) and name in fields:
                    return fields[name].get_default()
                return value
            except AttributeError:
                field = fields.get(name)
                if field and isinstance(field, tuple) and field[0] == FIELD_INSTANCE:
                    return field[2]  # 返回默认实例
                elif field and isinstance(field, Field):
                    return field.get_default()
                return None

        # 正常调用 getter
        if name in getters_map:
            getter = getters_map[name]
            object.__setattr__(self, IN_GETTER, True)
            try:
                return getter(self)
            finally:
                object.__setattr__(self, IN_GETTER, False)

        # 处理字段（未设置时返回默认值）
        if name in fields:
            try:
                value = object.__getattribute__(self, name)
                # 修复：如果值是Field对象，说明未设置，返回默认值
                if isinstance(value, Field):
                    return fields[name].get_default()
                return value
            except AttributeError:
                field = fields[name]
                if isinstance(field, tuple):
                    field_type, field_class = field[0], field[1]
                    if field_type == FIELD_OBJECT:
                        # 类引用字段，自动实例化
                        instance = field_class()
                        # 将实例存储到对象字典中，避免下次访问时重新创建
                        self.__dict__[name] = instance
                        return instance
                    elif field_type == FIELD_INSTANCE:
                        return field[2]  # 返回默认实例
                elif isinstance(field, Field):
                    return field.get_default()
                return None

        return object.__getattribute__(self, name)
    return __getattribute__

def _make_setattr(fields, validators):
    def __setattr__(self, name, value):
        if getattr(self, INIT_FLAG, False):
            self.__dict__[name] = value
            return

        if name not in fields:
            self.__dict__[name] = value
            return

        field = fields[name]
        # 为每次属性设置创建新的 visited 集合，防止递归验证
        validated_value = _validate_and_convert_value(self, field, name, value, validators, visited=set())
        self.__dict__[name] = validated_value
    return __setattr__


def _make_init(cls, fields, validators, original_init):
    def __init__(self, **kwargs):
        self.__dict__[INIT_FLAG] = True

        if original_init and original_init not in (object.__init__, cls.__init__):
            try:
                original_init(self)
            except TypeError:
                pass

        # === 检查 required 字段是否传值 ===
        for key, field in fields.items():
            if isinstance(field, tuple):
                continue  # dataclass 字段不强制 required
            if isinstance(field, Field) and field.required:
                if key not in kwargs:
                    raise ValidationError("Missing required field: '{}'".format(key))

        # === 初始化传入字段 ===
        # 为整个初始化过程创建共享的 visited 集合
        visited = set()
        for key, value in kwargs.items():
            if key not in fields:
                self.__dict__[key] = value
                continue
            field = fields[key]
            validated_value = _validate_and_convert_value(self, field, key, value, validators, visited)
            self.__dict__[key] = validated_value

        # === 设置非 required 字段的默认值 ===
        for key, field in fields.items():
            if key in kwargs or key in self.__dict__:
                continue
                
            if isinstance(field, tuple):
                field_type = field[0]
                if field_type == FIELD_OBJECT:
                    # 字段定义为：demo = Test2Class，自动创建实例
                    self.__dict__[key] = field[1]()  # 创建新实例
                elif field_type == FIELD_INSTANCE:
                    # 字段定义为：demo1 = Test2Class()
                    self.__dict__[key] = field[2]  # 默认实例
                    
            elif isinstance(field, Field) and not field.required:
                self.__dict__[key] = field.get_default()

        self.__dict__[INIT_FLAG] = False
    return __init__


def _validate_and_convert_value(instance, field, field_name, value, validators, visited):
    """
    统一校验入口：基础验证 -> 自定义验证，添加递归防护
    """
    # 递归防护：检查是否已处理过此对象
    obj_id = id(value)
    if obj_id in visited:
        return value  # 已访问过，跳过进一步验证
    visited.add(obj_id)
    
    try:
        validated_value = None
        
        # 处理嵌套 dataclass 字段（类引用或实例）
        if isinstance(field, tuple):
            field_type = field[0]
            field_class = field[1]
            
            if field_type == FIELD_OBJECT:
                # 字段定义为：类属性
                if isinstance(value, dict):
                    # 创建实例并确保正确初始化所有字段
                    validated_value = field_class(**value)
                elif hasattr(value, DATACLASS_FIELDS):
                    validated_value = value
                else:
                    raise ValidationError("Expected dict or {} instance for field '{}'".format(field_class.__name__, field_name))
                
            elif field_type == FIELD_INSTANCE:
                # 字段定义为：实例类属性
                if isinstance(value, dict):
                    validated_value = field_class(**value)
                elif hasattr(value, DATACLASS_FIELDS):
                    validated_value = value
                else:
                    raise ValidationError("Expected dict or {} instance for field '{}'".format(field_class.__name__, field_name))
                    
            # 递归验证嵌套 dataclass 实例的字段
            if hasattr(validated_value, DATACLASS_FIELDS):
                for sub_field_name, sub_field_def in validated_value._dataclass_fields.items():
                    # 检查 sub_field_def 是否是 tuple (嵌套 dataclass) 或 Field
                    if isinstance(sub_field_def, tuple):
                        sub_field_class = sub_field_def[1]
                        sub_value = getattr(validated_value, sub_field_name, None)
                        if sub_value is None and sub_field_def[0] == FIELD_INSTANCE:
                            sub_value = sub_field_def[2]  # 使用默认实例
                    elif isinstance(sub_field_def, Field):
                        try:
                            sub_value = getattr(validated_value, sub_field_name)
                            # 修复：如果sub_value是Field对象，说明未设置，返回默认值
                            if isinstance(sub_value, Field):
                                sub_value = sub_field_def.get_default()
                        except AttributeError:
                            sub_value = sub_field_def.get_default()
                    else:
                        continue
                        
                    # 递归验证
                    sub_validators = getattr(validated_value, '_dataclass_validators', {}).get(sub_field_name, [])
                    _validate_and_convert_value(
                        validated_value, 
                        sub_field_def, 
                        sub_field_name, 
                        sub_value, 
                        sub_validators, 
                        visited
                    )
        
        # 处理普通 Field
        elif isinstance(field, Field):
            try:
                validated_value = field.validate(value)
            except ValidationError as e:
                if field_name not in str(e):
                    e.path = [field_name] + getattr(e, "path", [])
                raise
                
        else:
            validated_value = value

        # 自定义验证
        if field_name in validators:
            for validator in validators[field_name]:
                try:
                    validator(instance, validated_value)
                except ValidationError as e:
                    if field_name not in str(e):
                        e.path = [field_name] + getattr(e, "path", [])
                    raise

        return validated_value
    
    finally:
        # 确保从 visited 集合中移除当前对象
        visited.discard(obj_id)


def _make_to_dict():
    def to_dict(self):
        result = {}
        fields = getattr(self, DATACLASS_FIELDS, {})

        # 序列化实例属性（非私有）
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            result[k] = _serialize_value(v)

        # 补全字段默认值（如果未设置）
        for k, field in fields.items():
            if k not in result:
                if isinstance(field, tuple) and field[0] == FIELD_INSTANCE:
                    result[k] = _serialize_value(field[2])  # 默认实例
                elif isinstance(field, Field):
                    default = field.get_default()
                    if default is not None:
                        result[k] = default

        return result
    return to_dict


def _serialize_value(value):
    """递归序列化值"""
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        return value.to_dict()
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(_serialize_value(item) for item in value)
    else:
        return value
