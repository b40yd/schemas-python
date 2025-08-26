# -*- coding: utf-8 -*-
import sys
import inspect
from .fields import Field, ValidationError

# 元数据字段名
DATACLASS_FIELDS = "_dataclass_fields"
DATACLASS_ACCESSORS = "_dataclass_accessors"

# 内部状态标志
INIT_FLAG = "_initializing"       # 用于控制 __init__ 递归（保留）
IN_GETTER = "_in_getter"
IN_SETTER = "_in_setter"          # 防止 setter 递归

# 字段类型标识
FIELD_OBJECT = '_object'
FIELD_INSTANCE = '_instance'


def getter(field_name):
    """
    装饰器：为字段注册自定义 getter 方法
    """
    def decorator(func):
        func._is_dataclass_getter = True
        func._dataclass_field_name = field_name
        return func
    return decorator


def setter(field_name):
    """
    装饰器：为字段注册自定义 setter 方法
    """
    def decorator(func):
        func._is_dataclass_setter = True
        func._dataclass_field_name = field_name
        return func
    return decorator


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
        fields = _collect_fields(cls)
        accessors = _collect_accessors(cls)
        validators = _collect_validators(cls)

        cls._dataclass_fields = fields
        cls._dataclass_accessors = accessors
        cls._dataclass_validators = validators

        original_init = getattr(cls, "__init__", None)
        cls.__init__ = _make_init(cls, fields, validators, original_init)

        cls.__getitem__ = lambda self, key: self._get_field_value(key)
        cls.__setitem__ = lambda self, key, value: setattr(self, key, value)
        cls.__contains__ = lambda self, key: key in getattr(self, DATACLASS_FIELDS, {})

        cls.__getattribute__ = _make_getattribute(accessors)
        cls.__setattr__ = _make_setattr(fields, validators, accessors)

        cls._get_field_value = _make_get_field_value()
        cls.to_dict = _make_to_dict()
        cls.keys = lambda self: iter(getattr(self, DATACLASS_FIELDS, {}).keys())
        cls.values = lambda self: [getattr(self, k) for k in self.keys()]
        cls.items = lambda self: [(k, getattr(self, k)) for k in self.keys()]
        cls.get = lambda self, key, default=None: getattr(self, key, default)

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


def _collect_fields(cls):
    """收集所有 Field 字段"""
    fields = {}
    all_attrs = {}
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


def _collect_accessors(cls):
    """收集被 @getter 和 @setter 装饰的方法"""
    accessors = {}
    for key, val in cls.__dict__.items():
        if not callable(val):
            continue
        if hasattr(val, '_is_dataclass_getter'):
            field_name = val._dataclass_field_name
            if field_name not in accessors:
                accessors[field_name] = {}
            accessors[field_name]['getter'] = val
        if hasattr(val, '_is_dataclass_setter'):
            field_name = val._dataclass_field_name
            if field_name not in accessors:
                accessors[field_name] = {}
            accessors[field_name]['setter'] = val
    return accessors


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
                    return field[2]
                elif isinstance(field, Field):
                    return field.get_default()
                return None
            if key in self.__dict__:
                return self.__dict__[key]
            raise KeyError("Field '{}' not found".format(key))
    return _get_field_value


def _make_getattribute(accessors):
    def __getattribute__(self, name):
        try:
            fields = object.__getattribute__(self, DATACLASS_FIELDS)
            accessors_map = object.__getattribute__(self, DATACLASS_ACCESSORS)
        except AttributeError:
            return object.__getattribute__(self, name)

        try:
            in_getter = object.__getattribute__(self, IN_GETTER)
        except AttributeError:
            in_getter = False

        if in_getter and name in accessors_map and 'getter' in accessors_map[name]:
            try:
                value = object.__getattribute__(self, name)
                if isinstance(value, Field) and name in fields:
                    return fields[name].get_default()
                return value
            except AttributeError:
                field = fields.get(name)
                if field and isinstance(field, tuple) and field[0] == FIELD_INSTANCE:
                    return field[2]
                elif field and isinstance(field, Field):
                    return field.get_default()
                return None

        if name in accessors_map and 'getter' in accessors_map[name]:
            getter_func = accessors_map[name]['getter']
            object.__setattr__(self, IN_GETTER, True)
            try:
                return getter_func(self)
            finally:
                object.__setattr__(self, IN_GETTER, False)

        if name in fields:
            try:
                value = object.__getattribute__(self, name)
                if isinstance(value, Field):
                    return fields[name].get_default()
                return value
            except AttributeError:
                field = fields[name]
                if isinstance(field, tuple):
                    field_type, field_class = field[0], field[1]
                    if field_type == FIELD_OBJECT:
                        instance = field_class()
                        self.__dict__[name] = instance
                        return instance
                    elif field_type == FIELD_INSTANCE:
                        return field[2]
                elif isinstance(field, Field):
                    return field.get_default()
                return None

        return object.__getattribute__(self, name)
    return __getattribute__


def _make_setattr(fields, validators, accessors):
    """
    修改：移除 INIT_FLAG 短路逻辑，确保初始化时也走 setter
    """
    def __setattr__(self, name, value):
        # 移除：if getattr(self, INIT_FLAG, False): ... 的短路
        # 初始化时也要完整处理

        try:
            in_setter = object.__getattribute__(self, IN_SETTER)
        except AttributeError:
            in_setter = False

        if name in accessors and 'setter' in accessors[name] and not in_setter:
            setter_func = accessors[name]['setter']
            object.__setattr__(self, IN_SETTER, True)
            try:
                # 先验证和转换值，然后传递给 setter
                field = fields.get(name)
                if field and isinstance(field, Field):
                    validated_value = _validate_and_convert_value(self, field, name, value, validators, visited=set())
                    # 在调用 setter 之前，先设置值到 __dict__ 中，这样 setter 可以访问当前值
                    current_value = self.__dict__.get(name)
                    self.__dict__[name] = validated_value
                    setter_func(self, validated_value)
                else:
                    current_value = self.__dict__.get(name)
                    self.__dict__[name] = value
                    setter_func(self, value)
                return
            finally:
                object.__setattr__(self, IN_SETTER, False)

        if name not in fields:
            self.__dict__[name] = value
            return

        field = fields[name]
        validated_value = _validate_and_convert_value(self, field, name, value, validators, visited=set())
        self.__dict__[name] = validated_value
    return __setattr__


def _make_init(cls, fields, validators, original_init):
    def __init__(self, **kwargs):
        # 保留 INIT_FLAG 用于控制原始 __init__ 递归调用
        self.__dict__[INIT_FLAG] = True

        if original_init and original_init not in (object.__init__, cls.__init__):
            try:
                argspec = inspect.getargspec(original_init)
                init_params = argspec.args[1:]
                init_kwargs = {}
                for param in init_params:
                    if param in kwargs:
                        init_kwargs[param] = kwargs.pop(param)
                original_init(self, **init_kwargs)
            except Exception as e:
                raise TypeError("Error calling original __init__: {}".format(str(e)))

        # 检查 required 字段
        for key, field in fields.items():
            if isinstance(field, Field) and field.required:
                if key not in kwargs:
                    raise ValidationError("Missing required field: '{}'".format(key))

        visited = set()
        # 使用 setattr 触发 __setattr__ → 走 setter
        for key, value in kwargs.items():
            if key not in fields:
                self.__dict__[key] = value
                continue
            field = fields[key]
            validated_value = _validate_and_convert_value(self, field, key, value, validators, visited)
            setattr(self, key, validated_value)  # ← 触发 __setattr__，走 setter

        # 设置非 required 字段的默认值（也走 setter）
        for key, field in fields.items():
            if key in kwargs or key in self.__dict__:
                continue
            if isinstance(field, tuple):
                field_type = field[0]
                if field_type == FIELD_OBJECT:
                    setattr(self, key, field[1]())
                elif field_type == FIELD_INSTANCE:
                    setattr(self, key, field[2])
            elif isinstance(field, Field) and not field.required:
                default = field.get_default()
                if default is not None:
                    setattr(self, key, default)

        # 最后才清除 INIT_FLAG
        self.__dict__[INIT_FLAG] = False

    return __init__


def _validate_and_convert_value(instance, field, field_name, value, validators, visited):
    obj_id = id(value)
    if obj_id in visited:
        return value
    visited.add(obj_id)

    try:
        validated_value = None

        if isinstance(field, tuple):
            field_type = field[0]
            field_class = field[1]

            if field_type == FIELD_OBJECT:
                if isinstance(value, dict):
                    validated_value = field_class(**value)
                elif hasattr(value, DATACLASS_FIELDS):
                    validated_value = value
                else:
                    raise ValidationError("Expected dict or {} instance for field '{}'".format(
                        field_class.__name__, field_name))
            elif field_type == FIELD_INSTANCE:
                if isinstance(value, dict):
                    validated_value = field_class(**value)
                elif hasattr(value, DATACLASS_FIELDS):
                    validated_value = value
                else:
                    raise ValidationError("Expected dict or {} instance for field '{}'".format(
                        field_class.__name__, field_name))

            if hasattr(validated_value, DATACLASS_FIELDS):
                for sub_name, sub_field in validated_value._dataclass_fields.items():
                    try:
                        sub_value = getattr(validated_value, sub_name)
                        if isinstance(sub_value, Field):
                            sub_value = sub_field.get_default()
                    except AttributeError:
                        sub_value = sub_field.get_default() if isinstance(sub_field, Field) else None

                    sub_validators = getattr(validated_value, '_dataclass_validators', {}).get(sub_name, [])
                    _validate_and_convert_value(
                        validated_value, sub_field, sub_name, sub_value, sub_validators, visited
                    )
        elif isinstance(field, Field):
            try:
                validated_value = field.validate(value)
            except ValidationError as e:
                if field_name not in str(e):
                    e.path = [field_name] + getattr(e, "path", [])
                raise
        else:
            validated_value = value

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
        visited.discard(obj_id)


def _make_to_dict():
    def to_dict(self):
        result = {}
        fields = getattr(self, DATACLASS_FIELDS, {})

        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            result[k] = _serialize_value(v)

        for k, field in fields.items():
            if k not in result:
                if isinstance(field, tuple) and field[0] == FIELD_INSTANCE:
                    result[k] = _serialize_value(field[2])
                elif isinstance(field, Field):
                    default = field.get_default()
                    if default is not None:
                        result[k] = default

        return result
    return to_dict


def _serialize_value(value):
    if hasattr(value, "to_dict") and callable(getattr(value, "to_dict")):
        return value.to_dict()
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(_serialize_value(item) for item in value)
    else:
        return value
