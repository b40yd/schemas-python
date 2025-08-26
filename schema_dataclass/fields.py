# -*- coding: utf-8 -*-
import abc
import re
import sys
import datetime
import os
import time
from schema_dataclass.exceptions import ValidationError

# Python 2/3 兼容性
if sys.version_info[0] >= 3:
    unicode = str
    string_types = (str,)
else:
    string_types = (str, unicode)

class ValidationStrategy(object):
    __metaclass__ = abc.ABCMeta
    """验证策略基类"""
    
    @abc.abstractmethod
    def validate(self, value, field):
        pass


class RequiredValidationStrategy(ValidationStrategy):
    """必填字段验证策略"""
    def validate(self, value, field):
        if value is None or (field.required and isinstance(value, string_types) and value == ""):
            if field.required:
                error_msg = field.get_error_message("required")
                raise ValidationError(error_msg)
            return field.get_default()
        return value


class LengthValidationStrategy(ValidationStrategy):
    """长度验证策略"""
    def validate(self, value, field):
        if isinstance(value, string_types + (list, tuple, set)):
            length = len(value)
            if field.min_length is not None and length < field.min_length:
                error_msg = field.get_error_message("min_length", min_length=field.min_length)
                raise ValidationError(error_msg)
            if field.max_length is not None and length > field.max_length:
                error_msg = field.get_error_message("max_length", max_length=field.max_length)
                raise ValidationError(error_msg)
        return value


class RangeValidationStrategy(ValidationStrategy):
    """范围验证策略"""
    def validate(self, value, field):
        if isinstance(value, (int, float)):
            if field.minvalue is not None and value < field.minvalue:
                error_msg = field.get_error_message("minvalue", minvalue=field.minvalue)
                raise ValidationError(error_msg)
            if field.maxvalue is not None and value > field.maxvalue:
                error_msg = field.get_error_message("maxvalue", maxvalue=field.maxvalue)
                raise ValidationError(error_msg)
        return value


class ChoicesValidationStrategy(ValidationStrategy):
    """选项验证策略"""
    def validate(self, value, field):
        if field.choices is not None and value not in field.choices:
            error_msg = field.get_error_message("choices", choices=field.choices)
            raise ValidationError(error_msg)
        return value


class RegexValidationStrategy(ValidationStrategy):
    """正则表达式验证策略"""
    def validate(self, value, field):
        if field.regex is not None and isinstance(value, string_types):
            if not re.match(field.regex, value):
                error_msg = field.get_error_message("regex", regex=field.regex)
                raise ValidationError(error_msg)
        return value


class ListItemsValidationStrategy(ValidationStrategy):
    """列表项验证策略"""
    def validate(self, value, field):
        if not isinstance(value, list) or not field.item_type:
            error_msg = field.get_error_message("invalid_type", expected_type="list")
            raise ValidationError(error_msg)

        results = []
        for i, item in enumerate(value):
            try:
                # 情况1: item_type 是 dataclass 类型
                if (
                    isinstance(field.item_type, type) and 
                    hasattr(field.item_type, '__dataclass_fields__') and
                    isinstance(item, dict)
                ):
                    results.append(field.item_type(**item))
                    continue

                # 情况2: item_type 是 Field 实例
                if isinstance(field.item_type, Field):
                    validated_item = field.item_type.validate(item)
                    results.append(validated_item)
                    continue

                # 情况3: item_type 是普通类型（如 int, str）
                if not isinstance(item, field.item_type):
                    expected = getattr(field.item_type, "__name__", str(field.item_type))
                    error_msg = field.get_error_message(
                        "invalid_list_item", index=i, expected_type=expected
                    )
                    raise ValidationError(error_msg, field_name=field.name)
                results.append(item)

            except ValidationError:
                raise
            except Exception:
                expected = getattr(field.item_type, "__name__", str(field.item_type))
                error_msg = field.get_error_message(
                    "invalid_list_item", index=i, expected_type=expected
                )
                raise ValidationError(error_msg, field_name=field.name)
        return results


class DateValidationStrategy(ValidationStrategy):
    """日期范围验证策略"""
    def validate(self, value, field):
        if value is None:
            return value
            
        # 检查最小日期
        if field.min_date is not None and value < field.min_date:
            error_msg = field.get_error_message(
                "min_date", 
                min_date=field.min_date.strftime(field.output_format or "%Y-%m-%d")
            )
            raise ValidationError(error_msg)
            
        # 检查最大日期
        if field.max_date is not None and value > field.max_date:
            error_msg = field.get_error_message(
                "max_date", 
                max_date=field.max_date.strftime(field.output_format or "%Y-%m-%d")
            )
            raise ValidationError(error_msg)
            
        return value


class DateTimeValidationStrategy(ValidationStrategy):
    """日期时间范围验证策略"""
    def validate(self, value, field):
        if value is None:
            return value
            
        # 检查最小日期时间
        if field.min_datetime is not None and value < field.min_datetime:
            error_msg = field.get_error_message(
                "min_datetime", 
                min_datetime=field.min_datetime.strftime(field.output_format or "%Y-%m-%d %H:%M:%S")
            )
            raise ValidationError(error_msg)
            
        # 检查最大日期时间
        if field.max_datetime is not None and value > field.max_datetime:
            error_msg = field.get_error_message(
                "max_datetime", 
                max_datetime=field.max_datetime.strftime(field.output_format or "%Y-%m-%d %H:%M:%S")
            )
            raise ValidationError(error_msg)
            
        return value


class Field(object):
    """字段基类，使用策略模式实现验证逻辑"""
    __metaclass__ = abc.ABCMeta
    
    # 默认验证策略
    DEFAULT_VALIDATION_STRATEGIES = [
        RequiredValidationStrategy(),
    ]

    def __init__(
        self,
        default=None,
        alias=None,
        required=False,
        min_length=None,
        max_length=None,
        minvalue=None,
        maxvalue=None,
        choices=None,
        item_type=None,
        regex=None,
        error_messages=None,
        validation_strategies=None,
        **kwargs
    ):
        """
        字段初始化

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
        :param error_messages: 自定义错误消息字典
        :param validation_strategies: 自定义验证策略
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

        # 默认错误消息
        self.default_error_messages = {
            "required": "This field is required",
            "min_length": "Length must be at least {min_length}",
            "max_length": "Length must be at most {max_length}",
            "minvalue": "Value must be at least {minvalue}",
            "maxvalue": "Value must be at most {maxvalue}",
            "choices": "Value must be one of: {choices}",
            "regex": "Value does not match pattern: {regex}",
            "invalid_type": "Value must be a {expected_type}",
            "invalid_list_item": "Item at index {index} has invalid type, expected {expected_type}",
            "min_date": "Date must be on or after {min_date}",
            "max_date": "Date must be on or before {max_date}",
            "min_datetime": "Datetime must be on or after {min_datetime}",
            "max_datetime": "Datetime must be on or before {max_datetime}",
            "file_not_exists": "File {path} does not exist",
            "not_a_file": "{path} is not a file",
            "not_a_directory": "{path} is not a directory",
        }

        # 合并用户自定义错误消息
        self.error_messages = self.default_error_messages.copy()
        if error_messages:
            self.error_messages.update(error_messages)
            
        # 验证策略
        self.validation_strategies = validation_strategies or list(self.DEFAULT_VALIDATION_STRATEGIES)

    def get_error_message(self, error_key, **format_kwargs):
        """
        获取格式化的错误消息

        :param error_key: 错误消息键
        :param format_kwargs: 格式化参数
        :return: 格式化后的错误消息
        """
        message_template = self.error_messages.get(error_key, "Validation error")
        try:
            return message_template.format(**format_kwargs)
        except (KeyError, ValueError):
            # 如果格式化失败，返回原始模板
            return message_template

    def get_default(self):
        """获取默认值，支持可调用对象"""
        if callable(self.default):
            return self.default()
        return self.default

    def validate(self, value):
        """执行所有验证策略"""
        for strategy in self.validation_strategies:
            try:
                value = strategy.validate(value, self)
            except ValidationError:
                raise
            except Exception as e:
                error_msg = self.get_error_message("invalid_type", expected_type=self.__class__.__name__)
                raise ValidationError("{0}: {1}".format(error_msg, str(e)))
        return value


class StringField(Field):
    """字符串字段"""
    DEFAULT_VALIDATION_STRATEGIES = Field.DEFAULT_VALIDATION_STRATEGIES + [
        LengthValidationStrategy(),
        RegexValidationStrategy(),
        ChoicesValidationStrategy()
    ]

    def validate(self, value):
        # 先执行自己的类型检查
        if value is not None and not isinstance(value, string_types):
            error_msg = self.get_error_message("invalid_type", expected_type="string")
            raise ValidationError(error_msg)
            
        # 再调用父类验证
        return Field.validate(self, value)


class ListField(Field):
    """列表字段"""
    DEFAULT_VALIDATION_STRATEGIES = Field.DEFAULT_VALIDATION_STRATEGIES + [
        LengthValidationStrategy(),
        ListItemsValidationStrategy()
    ]


class NumberField(Field):
    """数字字段"""
    DEFAULT_VALIDATION_STRATEGIES = Field.DEFAULT_VALIDATION_STRATEGIES + [
        RangeValidationStrategy(),
        ChoicesValidationStrategy()
    ]

    def validate(self, value):
        # 先执行自己的类型检查
        if value is not None and not isinstance(
            value, (int, float, long if sys.version_info[0] < 3 else int)
        ):
            error_msg = self.get_error_message("invalid_type", expected_type="number")
            raise ValidationError(error_msg)
            
        # 再调用父类验证
        return Field.validate(self, value)


class DateField(Field):
    """日期字段"""
    DEFAULT_VALIDATION_STRATEGIES = Field.DEFAULT_VALIDATION_STRATEGIES + [
        DateValidationStrategy()
    ]
    
    def __init__(self, output_format=None, return_timestamp=False, min_date=None, max_date=None, **kwargs):
        """
        :param output_format: 日期格式化字符串，如 "%Y-%m-%d"
        :param return_timestamp: 是否返回时间戳（整数）
        :param min_date: 最小允许日期
        :param max_date: 最大允许日期
        """
        super(DateField, self).__init__(**kwargs)
        self.output_format = output_format
        self.return_timestamp = return_timestamp
        self.min_date = min_date
        self.max_date = max_date

    def _parse_isoformat(self, value):
        """Python 2 版本的 isoformat 解析"""
        # 简单处理 ISO 格式，如 '2023-07-15'
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            pass
            
        # 处理带时间的 ISO 格式，如 '2023-07-15T10:30:00'
        if 'T' in value:
            date_str, time_str = value.split('T')
            try:
                return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
                
        return None

    def validate(self, value):
        # 处理整数时间戳
        if isinstance(value, (int, float)):
            try:
                dt = datetime.datetime.fromtimestamp(value)
                value = dt.date()
            except (ValueError, TypeError) as e:
                error_msg = self.get_error_message("invalid_type", expected_type="date")
                raise ValidationError("{0}: {1}".format(error_msg, str(e)))
        
        # 处理字符串输入
        if isinstance(value, string_types):
            try:
                # 尝试解析ISO格式
                if 'T' in value:
                    dt = self._parse_isoformat(value)
                    if dt is None:
                        # 尝试其他常见格式
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']:
                            try:
                                dt = datetime.datetime.strptime(value.split('T')[0], fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            raise ValueError("Invalid date format")
                    value = dt
                else:
                    # 尝试解析常见日期格式
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            value = datetime.datetime.strptime(value, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError("Invalid date format")
            except (ValueError, TypeError) as e:
                error_msg = self.get_error_message("invalid_type", expected_type="date")
                raise ValidationError("{0}: {1}".format(error_msg, str(e)))

        # 处理datetime对象
        elif isinstance(value, datetime.datetime):
            value = value.date()

        # 检查是否为date对象
        elif not isinstance(value, datetime.date) and value is not None:
            error_msg = self.get_error_message("invalid_type", expected_type="date")
            raise ValidationError(error_msg)

        # 根据参数决定返回格式
        if value is not None and self.return_timestamp:
            # 转换为时间戳（秒）
            dt = datetime.datetime.combine(value, datetime.time.min)
            return int(time.mktime(dt.timetuple()))
        elif value is not None and self.output_format:
            # 格式化为字符串
            return value.strftime(self.output_format)
        
        # 再调用父类验证
        return Field.validate(self, value)


class DateTimeField(Field):
    """日期时间字段"""
    DEFAULT_VALIDATION_STRATEGIES = Field.DEFAULT_VALIDATION_STRATEGIES + [
        DateTimeValidationStrategy(),
        ChoicesValidationStrategy()  # 确保添加Choices验证策略
    ]
    
    def __init__(self, output_format=None, return_timestamp=False, min_datetime=None, max_datetime=None, **kwargs):
        """
        :param output_format: 日期时间格式化字符串，如 "%Y-%m-%d %H:%M:%S"
        :param return_timestamp: 是否返回时间戳（整数）
        :param min_datetime: 最小允许日期时间
        :param max_datetime: 最大允许日期时间
        """
        super(DateTimeField, self).__init__(**kwargs)
        self.output_format = output_format
        self.return_timestamp = return_timestamp
        self.min_datetime = min_datetime
        self.max_datetime = max_datetime

    def _parse_isoformat(self, value):
        """Python 2 版本的 isoformat 解析"""
        try:
            # 处理标准 ISO 格式
            if 'T' in value:
                date_str, time_str = value.split('T')
                if '.' in time_str:
                    # 处理带毫秒的格式
                    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
                else:
                    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            else:
                # 尝试其他常见格式
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                    try:
                        return datetime.datetime.strptime(value, fmt)
                    except ValueError:
                        continue
        except ValueError:
            pass
        return None

    def validate(self, value):
        # 处理整数或浮点数时间戳
        if isinstance(value, (int, float)):
            try:
                return datetime.datetime.fromtimestamp(value)
            except (ValueError, TypeError) as e:
                error_msg = self.get_error_message("invalid_type", expected_type="datetime")
                raise ValidationError("{0}: {1}".format(error_msg, str(e)))
        
        # 处理字符串输入
        if isinstance(value, string_types):
            try:
                # 尝试解析ISO格式
                if 'T' in value:
                    dt = self._parse_isoformat(value)
                    if dt is not None:
                        value = dt
                    else:
                        raise ValueError("Invalid datetime format")
                else:
                    # 尝试解析常见日期时间格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S']:
                        try:
                            value = datetime.datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        raise ValueError("Invalid datetime format")
            except (ValueError, TypeError) as e:
                error_msg = self.get_error_message("invalid_type", expected_type="datetime")
                raise ValidationError("{0}: {1}".format(error_msg, str(e)))

        # 检查是否为datetime对象
        elif not isinstance(value, datetime.datetime) and value is not None:
            error_msg = self.get_error_message("invalid_type", expected_type="datetime")
            raise ValidationError(error_msg)

        # 再调用父类验证
        result = Field.validate(self, value)
        
        # 根据参数决定返回格式
        if result is not None and self.return_timestamp:
            # 转换为时间戳（秒）
            return int(time.mktime(result.timetuple()))
        elif result is not None and self.output_format:
            # 格式化为字符串
            return result.strftime(self.output_format)
        
        return result


class EmailField(StringField):
    """电子邮件字段"""
    EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    def __init__(self, **kwargs):
        # 确保使用电子邮件正则表达式
        kwargs.setdefault('regex', self.EMAIL_REGEX)
        super(EmailField, self).__init__(**kwargs)
        
        # 更新错误消息
        self.error_messages["regex"] = "Invalid email format"
        self.error_messages["invalid_type"] = "Value must be a valid email address"

        
