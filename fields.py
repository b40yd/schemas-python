# -*- coding: utf-8 -*-
import abc
import re
import sys

# Python 2/3 兼容性
if sys.version_info[0] >= 3:
    unicode = str
    string_types = (str,)
else:
    string_types = (str, unicode)

class ValidationError(Exception):
    """Validation error exception"""
    def __init__(self, message, field_name=None, path=None):
        self.message = message
        self.field_name = field_name
        self.path = path or []
        super(ValidationError, self).__init__(': '.join(self.path + [message]) if self.path else message)


class Field(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, default=None, alias=None, required=True,
                 min_length=None, max_length=None,
                 minvalue=None, maxvalue=None,
                 choices=None, item_type=None, regex=None,
                 **kwargs):
        """
        增强型字段验证基类
        
        :param default: 默认值（可为可调用对象）
        :param alias: 字段别名（用于序列化/反序列化）
        :param required: 是否必填
        :param min_length: 最小长度（字符串/列表）
        :param max_length: 最大长度（字符串/列表）
        :param minvalue: 最小值（数字）
        :param maxvalue: 最大值（数字）
        :param choices: 枚举选项（列表/元组）
        :param item_type: 列表项类型（ListField专用）
        :param regex: 正则表达式模式（字符串字段专用）
        """
        self.default = default
        self.alias = alias
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.choices = choices
        self.item_type = item_type
        self.regex = regex
        self.name = None  # 由元类设置
        self.params = kwargs

    def get_default(self):
        """获取默认值，支持可调用对象"""
        if callable(self.default):
            return self.default()
        return self.default

    def get_value(self, instance, name):
        """
        获取字段值的统一接口
        优先级：get_xxx() 方法 > 实例属性 > 默认值

        :param instance: 数据类实例
        :param name: 字段名称
        :return: 字段值
        """
        # 1. 优先：是否存在 get_xxx() 方法
        getter_name = 'get_{0}'.format(name)
        if hasattr(instance.__class__, getter_name):
            getter = getattr(instance.__class__, getter_name)
            if callable(getter):
                return getter(instance)

        # 2. 实例属性是否存在
        if hasattr(instance, '__dict__') and name in instance.__dict__:
            return instance.__dict__[name]

        # 3. 返回默认值
        return self.get_default()

    def validate_required(self, value):
        """Check required and return default if not required"""
        if value is None:
            if self.required:
                raise ValidationError("This field is required")
            return self.get_default()
        return value

    def validate_length(self, value):
        """Validate length for strings and lists"""
        if isinstance(value, string_types + (list, tuple, set)):
            length = len(value)
            if self.min_length is not None and length < self.min_length:
                raise ValidationError("Length must be at least %d" % self.min_length)
            if self.max_length is not None and length > self.max_length:
                raise ValidationError("Length must be at most %d" % self.max_length)
        return value

    def validatevalue_range(self, value):
        """Validate value range for numbers"""
        if isinstance(value, (int, float)):
            if self.minvalue is not None and value < self.minvalue:
                raise ValidationError("Value must be at least %d" % self.minvalue)
            if self.maxvalue is not None and value > self.maxvalue:
                raise ValidationError("Value must be at most %d" % self.maxvalue)
            
        return value

    def validate_choices(self, value):
        """Validate value is in allowed choices"""
        if self.choices is not None:
            if value not in self.choices:
                raise ValidationError("Value must be one of: %s" % str(self.choices))

        return value

    def validate_regex(self, value):
        """Validate value matches regex pattern"""
        if self.regex is not None and isinstance(value, string_types):
            if not re.match(self.regex, value):
                raise ValidationError("Value does not match pattern: %s" % self.regex)

        return value

    def validate_nested_model(self, value):
        """
        如果 item_type 是 DataClass 子类，且 value 是 dict，则实例化并校验
        """
        if (isinstance(self.item_type, type) and
            hasattr(self.item_type, '_dataclass_fields') and
            isinstance(value, dict)):
            # 实例化嵌套模型并校验
            return self.item_type(**value)

        return value
    
    def validate_list_items(self, value):
        if not isinstance(value, list) or not self.item_type:
            raise ValidationError("Value must be a list and item_type must be specified")

        results = []
        for i, item in enumerate(value):
            try:
                # 情况1: item_type 是 Model 子类，item 是 dict
                data = self.validate_nested_model(item)
                if data:
                    results.append(data)

                # 情况2: item_type 是 Field 实例
                elif hasattr(self.item_type, 'validate'):
                    validated_item = self.item_type.validate(item)
                    results.append(validated_item)

                # 情况3: item_type 是普通类型（如 int, str）
                else:
                    if not isinstance(item, self.item_type):
                        expected = getattr(self.item_type, '__name__', str(self.item_type))
                        raise ValidationError(
                            "Item at index %d has invalid type, expected %s" % (i, expected),
                            field_name=self.name
                        )
                    results.append(item)

            except ValidationError:
                raise
            except Exception:
                expected = getattr(self.item_type, '__name__', str(self.item_type))
                raise ValidationError(
                    "Item at index %d has invalid type, expected %s" % (i, expected),
                    field_name=self.name
                )
        return results if results else value  # 可选：替换原 value
    @abc.abstractmethod
    def validate(self, value):
        pass


class StringField(Field):
    def validate(self, value):
        """验证字段值，无效时抛出ValueError"""
        value = self.validate_required(value)
        if value is None:  # 已返回默认值且非必填
            return value

        # 确保是字符串类型
        if not isinstance(value, string_types):
            raise ValidationError("Value must be a string")

        # 长度校验
        value = self.validate_length(value)

        # 正则表达式校验
        value = self.validate_regex(value)

        # 枚举选项校验
        value = self.validate_choices(value)

        return value

class ListField(Field):
    def validate(self, value):
        value = self.validate_required(value)
        if value is None:  # 已返回默认值且非必填
            return value

        # 长度校验（字符串、列表）
        value = self.validate_length(value)
        # 列表项类型校验
        value = self.validate_list_items(value)
        return value
    
class NumberField(Field):
    def validate(self, value):
        value = self.validate_required(value)
        if value is None:  # 已返回默认值且非必填
            return value

        # 确保是数字类型
        if not isinstance(value, (int, float, long if sys.version_info[0] < 3 else int)):
            raise ValidationError("Value must be a number")

        # 数值范围校验
        value = self.validatevalue_range(value)

        # 枚举选项校验
        value = self.validate_choices(value)
        return value