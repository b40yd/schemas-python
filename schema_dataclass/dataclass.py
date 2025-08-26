# -*- coding: utf-8 -*-
import abc
from .fields import Field, ValidationError


class DataClassWrap(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def to_dict(self):
        """将对象转换为字典"""
        pass

def getter(field_name):
    def decorator(func):
        def attach(cls_dict):
            getters = cls_dict.setdefault('__getters__', {})
            getters[field_name] = func
        func._attach_getter = attach
        return func
    return decorator


def setter(field_name):
    def decorator(func):
        def attach(cls_dict):
            setters = cls_dict.setdefault('__setters__', {})
            setters[field_name] = func
        func._attach_setter = attach
        return func
    return decorator


def validate(field_name):
    def decorator(func):
        def attach(cls_dict):
            validators = cls_dict.setdefault('_dataclass_validators', {})
            validators.setdefault(field_name, []).append(func)
        func._attach_validator = attach
        return func
    return decorator


def dataclass(cls):
    fields = {}
    seen = set()
    class_attrs = {}
    
    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for k, v in base.__dict__.items():
            if k in seen:
                continue
            seen.add(k)
            class_attrs[k] = v
            
            if isinstance(v, Field):
                v.name = k
                fields[k] = v
            elif isinstance(v, type) and hasattr(v, '__dataclass_fields__'):
                fields[k] = v
            elif isinstance(v, DataClassWrap):
                fields[k] = v.__class__

    namespace = {
        '__dataclass_fields__': fields,
        '_dataclass_validators': {},
        '__dataclass_values__': None,
        '__getters__': {},
        '__setters__': {},
    }

    # 处理getter/setter/validator装饰器
    for attr in class_attrs.values():
        if hasattr(attr, '_attach_getter'):
            attr._attach_getter(namespace)
        if hasattr(attr, '_attach_setter'):
            attr._attach_setter(namespace)
        if hasattr(attr, '_attach_validator'):
            attr._attach_validator(namespace)

    # 复制普通属性和方法
    for k, v in class_attrs.items():
        if k in ['__module__', '__doc__', '__annotations__', '__dict__', '__weakref__']:
            continue
        if k in fields:
            continue
        if hasattr(v, '_attach_getter') or hasattr(v, '_attach_setter') or hasattr(v, '_attach_validator'):
            continue
        if k not in namespace:
            namespace[k] = v

    namespace.update({
        '__init__': _make_init(fields),
        'get': _make_get(),
        '__getattribute__': _make_getattribute(),
        '__setattr__': _make_setattr(fields),
        '__getitem__': lambda self, k: self.get(k),
        '__setitem__': lambda self, k, v: setattr(self, k, v),
        'to_dict': _make_to_dict(),
        '__repr__': _make_repr(),
        '__eq__': _make_eq(),
        '__ne__': lambda self, other: not self.__eq__(other) if hasattr(self, '__eq__') else NotImplemented,
    })

    new_cls = type(cls.__name__, (DataClassWrap,), namespace)
    new_cls.__module__ = cls.__module__
    new_cls.__doc__ = cls.__doc__
    return new_cls


def _make_init(fields):
    def __init__(self, **kwargs):
        object.__setattr__(self, '__dataclass_values__', {})
        for k, field in fields.items():
            if isinstance(field, Field) and field.required and k not in kwargs:
                raise ValidationError("Missing required field: '{}'".format(k))

        for k, v in kwargs.items():
            if k in fields:
                setattr(self, k, v)
            else:
                object.__setattr__(self, k, v)

        for k, field in fields.items():
            if k in getattr(self, '__dataclass_values__', {}):
                continue
            if k in self.__dict__:
                continue
            original_default = getattr(self.__class__, k, None)
            if isinstance(original_default, DataClassWrap):
                setattr(self, k, original_default)
            elif hasattr(field, '__dataclass_fields__'):
                setattr(self, k, field())
            elif isinstance(field, Field) and not field.required:
                default = field.get_default()
                if default is not None:
                    setattr(self, k, default)
    return __init__


def _make_get():
    def get(self, key, default=None):
        values = object.__getattribute__(self, '__dataclass_values__')
        if key in values:
            return values[key]
        fields = object.__getattribute__(self, '__dataclass_fields__')
        if key in fields:
            field = fields[key]
            original_default = getattr(self.__class__, key, None)
            if isinstance(original_default, DataClassWrap):
                return original_default
            if isinstance(field, Field):
                return field.get_default()
            if hasattr(field, '__dataclass_fields__'):
                return field()
        return default
    return get


def _make_getattribute():
    def __getattribute__(self, name):
        try:
            fields = object.__getattribute__(self, '__dataclass_fields__')
            getters = object.__getattribute__(self, '__getters__')
            values = object.__getattribute__(self, '__dataclass_values__')
        except AttributeError:
            return object.__getattribute__(self, name)

        if name in getters and callable(getters[name]):
            current_getter = getters.pop(name)
            try:
                return current_getter(self)
            finally:
                getters[name] = current_getter

        if name in fields:
            if name in values:
                return values[name]
            original_default = getattr(self.__class__, name, None)
            if isinstance(original_default, DataClassWrap):
                return original_default
            field = fields[name]
            if isinstance(field, Field):
                return field.get_default()
            elif hasattr(field, '__dataclass_fields__'):
                instance = field()
                values[name] = instance
                return instance
            return None

        return object.__getattribute__(self, name)
    return __getattribute__


def _make_setattr(fields):
    def __setattr__(self, name, value):
        try:
            setters = object.__getattribute__(self, '__setters__')
            values = object.__getattribute__(self, '__dataclass_values__')
            field = fields.get(name)
            validators = object.__getattribute__(self, '_dataclass_validators')
        except AttributeError:
            object.__setattr__(self, name, value)
            return

        if field is None:
            object.__setattr__(self, name, value)
            return

        validated_value = _validate_and_convert_value(self, field, name, value, validators)

        if name in setters:
            current_setter = setters.pop(name)
            try:
                result = current_setter(self, validated_value)
                if result is not None:
                    validated_value = result
            finally:
                setters[name] = current_setter

        values[name] = validated_value
    return __setattr__


def _serialize_value(value):
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return value.to_dict()
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, tuple):
        return tuple(_serialize_value(item) for item in value)
    else:
        return value


def _make_to_dict():
    def to_dict(self):
        result = {}
        fields = object.__getattribute__(self, '__dataclass_fields__')
        values = object.__getattribute__(self, '__dataclass_values__')

        for k in fields:
            if k in values:
                result[k] = _serialize_value(values[k])
            else:
                original_default = getattr(self.__class__, k, None)
                if isinstance(original_default, DataClassWrap):
                    result[k] = _serialize_value(original_default)
                else:
                    field = fields[k]
                    if isinstance(field, Field):
                        default = field.get_default()
                        if default is not None:
                            result[k] = _serialize_value(default)
                    elif hasattr(field, '__dataclass_fields__'):
                        result[k] = _serialize_value(field())

        for k, v in self.__dict__.items():
            if not k.startswith("_") and k not in fields:
                result[k] = _serialize_value(v)

        return result
    return to_dict


def _make_repr():
    def __repr__(self):
        fields = object.__getattribute__(self, '__dataclass_fields__')
        args = ", ".join("%s=%r" % (k, self.get(k)) for k in fields)
        return "%s(%s)" % (type(self).__name__, args)
    return __repr__


def _make_eq():
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        fields = object.__getattribute__(self, '__dataclass_fields__')
        return all(self.get(k) == other.get(k) for k in fields)
    return __eq__


def _validate_and_convert_value(instance, field, field_name, value, validators):
    try:
        validated_value = None

        if isinstance(field, type) and hasattr(field, '__dataclass_fields__'):
            if isinstance(value, dict):
                validated_value = field(**value)
            elif isinstance(value, DataClassWrap):
                validated_value = value
            else:
                raise ValidationError("Expected dict or {} instance for field '{}'".format(
                    field.__name__, field_name))
            if hasattr(validated_value, '__dataclass_fields__'):
                for k, f in validated_value.__dataclass_fields__.items():
                    if k in validated_value.__dataclass_values__:
                        v = validated_value.__dataclass_values__[k]
                    else:
                        original_default = getattr(validated_value.__class__, k, None)
                        if isinstance(original_default, DataClassWrap):
                            v = original_default
                        elif isinstance(f, Field):
                            v = f.get_default()
                        else:
                            continue
                    sub_validators = getattr(validated_value, '_dataclass_validators', {}).get(k, [])
                    _validate_and_convert_value(validated_value, f, k, v, sub_validators)

        elif isinstance(field, Field):
            validated_value = field.validate(value)

        else:
            validated_value = value

        if field_name in validators:
            for validator in validators[field_name]:
                validator(instance, validated_value)

        return validated_value

    except ValidationError as e:
        if field_name not in str(e):
            e.path = [field_name] + getattr(e, "path", [])
        raise
