# -*- coding: utf-8 -*-
import sys
import inspect
from .fields import Field, ValidationError

DATACLASS_FIELDS = "_dataclass_fields"
DATACLASS_GETTERS = "_dataclass_getters"

INIT_FLAG = "_initializing"
IN_GETTER = "_in_getter"
CUSTOM_GET_VALUE_FUNCTION_NAME_PREFIX = "get_"

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
            fields[key] = val  # 嵌套 dataclass
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


# ================== 工厂函数 ==================

def _make_get_field_value():
    def _get_field_value(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            fields = getattr(self, DATACLASS_FIELDS, {})
            if key in fields:
                field = fields[key]
                if isinstance(field, Field):
                    return field.get_default()
                return None
            if key in self.__dict__:
                return self.__dict__[key]
            raise KeyError("Field '%s' not found" % key)
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
                return fields[name].get_default() if isinstance(fields[name], Field) else None

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
                if isinstance(value, Field):
                    return fields[name].get_default()
                return value
            except AttributeError:
                field = fields[name]
                return field.get_default() if isinstance(field, Field) else None

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
        validated_value = _validate_and_convert_value(self, field, name, value, validators)
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

        # === 新增：检查 required 字段是否传值 ===
        for key, field in fields.items():
            if isinstance(field, Field) and field.required:
                if key not in kwargs:
                    raise ValidationError("Missing required field: '{}'".format(key))

        # === 初始化传入字段 ===
        for key, value in kwargs.items():
            if key not in fields:
                self.__dict__[key] = value
                continue
            field = fields[key]
            validated_value = _validate_and_convert_value(self, field, key, value, validators)
            self.__dict__[key] = validated_value

        # === 设置非 required 字段的默认值 ===
        for key, field in fields.items():
            if (
                key not in kwargs and
                isinstance(field, Field) and
                not field.required and
                key not in self.__dict__
            ):
                self.__dict__[key] = field.get_default()

        self.__dict__[INIT_FLAG] = False
    return __init__


def _validate_and_convert_value(instance, field, field_name, value, validators):
    """
    统一校验入口：基础验证 -> 自定义验证
    """
    # 1. 基础验证：Field 或嵌套 dataclass
    if isinstance(field, type) and hasattr(field, DATACLASS_FIELDS) and isinstance(value, dict):
        try:
            validated_value = field(**value)
        except ValidationError as e:
            if field_name not in str(e):
                e.path = [field_name] + getattr(e, "path", [])
            raise
    elif isinstance(field, Field):
        try:
            validated_value = field.validate(value)
        except ValidationError as e:
            if field_name not in str(e):
                e.path = [field_name] + getattr(e, "path", [])
            raise
    else:
        validated_value = value

    # 2. 自定义验证（在基础验证之后）
    if field_name in validators:
        for validator in validators[field_name]:
            try:
                validator(instance, validated_value)
            except ValidationError as e:
                if field_name not in str(e):
                    e.path = [field_name] + getattr(e, "path", [])
                raise

    return validated_value


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
            if k not in result and isinstance(field, Field):
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
