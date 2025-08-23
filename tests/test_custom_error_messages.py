# -*- coding: utf-8 -*-
"""
自定义错误消息测试
"""

import pytest
import sys
from schema_dataclass import StringField, NumberField, ListField, ValidationError


class TestDefaultErrorMessages:
    """默认错误消息测试"""

    @pytest.mark.error_messages
    def test_required_error(self):
        """测试必填字段默认错误"""
        field = StringField(required=True)
        with pytest.raises(ValidationError) as exc_info:
            field.validate(None)
        assert exc_info.value.message == "This field is required"

    @pytest.mark.error_messages
    def test_min_length_error(self):
        """测试最小长度默认错误"""
        field = StringField(min_length=5)
        with pytest.raises(ValidationError) as exc_info:
            field.validate("abc")
        assert exc_info.value.message == "Length must be at least 5"

    @pytest.mark.error_messages
    def test_max_length_error(self):
        """测试最大长度默认错误"""
        field = StringField(max_length=3)
        with pytest.raises(ValidationError) as exc_info:
            field.validate("toolong")
        assert exc_info.value.message == "Length must be at most 3"

    @pytest.mark.error_messages
    def test_minvalue_error(self):
        """测试最小值默认错误"""
        field = NumberField(minvalue=10)
        with pytest.raises(ValidationError) as exc_info:
            field.validate(5)
        assert exc_info.value.message == "Value must be at least 10"

    @pytest.mark.error_messages
    def test_maxvalue_error(self):
        """测试最大值默认错误"""
        field = NumberField(maxvalue=100)
        with pytest.raises(ValidationError) as exc_info:
            field.validate(150)
        assert exc_info.value.message == "Value must be at most 100"

    @pytest.mark.error_messages
    def test_choices_error(self):
        """测试选择项默认错误"""
        field = StringField(choices=["red", "green", "blue"])
        with pytest.raises(ValidationError) as exc_info:
            field.validate("yellow")
        expected = "Value must be one of: ['red', 'green', 'blue']"
        assert exc_info.value.message == expected

    @pytest.mark.error_messages
    def test_regex_error(self):
        """测试正则表达式默认错误"""
        field = StringField(regex=r"^\d{3}-\d{4}$")
        with pytest.raises(ValidationError) as exc_info:
            field.validate("abc-defg")
        expected = "Value does not match pattern: ^\d{3}-\d{4}$"
        assert exc_info.value.message == expected

    @pytest.mark.error_messages
    def test_invalid_type_error(self):
        """测试类型错误默认消息"""
        field = StringField()
        with pytest.raises(ValidationError) as exc_info:
            field.validate(123)
        assert exc_info.value.message == "Value must be a string"


class TestCustomErrorMessages:
    """自定义错误消息测试"""

    @pytest.mark.error_messages
    def test_custom_required_error(self, custom_error_messages):
        """测试自定义必填错误"""
        field = StringField(
            required=True,
            error_messages={"required": custom_error_messages["required"]},
        )
        with pytest.raises(ValidationError) as exc_info:
            field.validate(None)
        assert exc_info.value.message == "这个字段是必填的"

    @pytest.mark.error_messages
    def test_custom_length_errors(self, custom_error_messages):
        """测试自定义长度错误"""
        field = StringField(
            min_length=5,
            max_length=10,
            error_messages={
                "min_length": custom_error_messages["min_length"],
                "max_length": custom_error_messages["max_length"],
            },
        )

        # 测试最小长度
        with pytest.raises(ValidationError) as exc_info:
            field.validate("abc")
        assert exc_info.value.message == "长度至少需要 5 个字符"

        # 测试最大长度
        with pytest.raises(ValidationError) as exc_info:
            field.validate("verylongstring")
        assert exc_info.value.message == "长度不能超过 10 个字符"

    @pytest.mark.error_messages
    def test_custom_value_range_errors(self, custom_error_messages):
        """测试自定义数值范围错误"""
        field = NumberField(
            minvalue=10,
            maxvalue=100,
            error_messages={
                "minvalue": custom_error_messages["minvalue"],
                "maxvalue": custom_error_messages["maxvalue"],
            },
        )

        # 测试最小值
        with pytest.raises(ValidationError) as exc_info:
            field.validate(5)
        assert exc_info.value.message == "数值不能小于 10"

        # 测试最大值
        with pytest.raises(ValidationError) as exc_info:
            field.validate(150)
        assert exc_info.value.message == "数值不能大于 100"

    @pytest.mark.error_messages
    def test_custom_choices_error(self, custom_error_messages):
        """测试自定义选择项错误"""
        field = StringField(
            choices=["红色", "绿色", "蓝色"],
            error_messages={"choices": custom_error_messages["choices"]},
        )
        with pytest.raises(ValidationError) as exc_info:
            field.validate("黄色")
        # 检查错误消息开头，避免 Python 2/3 Unicode 表示差异
        error_message = exc_info.value.message
        assert error_message.startswith("请选择有效的选项")

    @pytest.mark.error_messages
    def test_custom_regex_error(self, custom_error_messages):
        """测试自定义正则表达式错误"""
        field = StringField(
            regex=r"^\d{3}-\d{4}$",
            error_messages={"regex": custom_error_messages["regex"]},
        )
        with pytest.raises(ValidationError) as exc_info:
            field.validate("abc-defg")
        assert exc_info.value.message == "格式不正确"

    @pytest.mark.error_messages
    def test_custom_type_error(self, custom_error_messages):
        """测试自定义类型错误"""
        field = StringField(
            error_messages={"invalid_type": custom_error_messages["invalid_type"]}
        )
        with pytest.raises(ValidationError) as exc_info:
            field.validate(123)
        assert exc_info.value.message == "类型必须是 string"

    @pytest.mark.error_messages
    def test_custom_list_item_error(self, custom_error_messages):
        """测试自定义列表项错误"""
        field = ListField(
            item_type=int,
            error_messages={
                "invalid_list_item": custom_error_messages["invalid_list_item"]
            },
        )
        with pytest.raises(ValidationError) as exc_info:
            field.validate([1, 2, "three", 4])
        assert exc_info.value.message == "列表第 2 项类型错误，期望 int"


class TestErrorMessageFormatting:
    """错误消息格式化测试"""

    @pytest.mark.error_messages
    def test_parameter_formatting(self):
        """测试参数格式化"""
        field = StringField(
            min_length=3,
            max_length=10,
            error_messages={
                "min_length": "至少需要 {min_length} 个字符",
                "max_length": "最多允许 {max_length} 个字符",
            },
        )

        # 测试参数替换
        with pytest.raises(ValidationError) as exc_info:
            field.validate("ab")
        assert exc_info.value.message == "至少需要 3 个字符"

    @pytest.mark.error_messages
    def test_missing_parameter_handling(self):
        """测试缺失参数处理"""
        field = StringField(
            min_length=5,
            error_messages={"min_length": "长度至少 {missing_param} 个字符"},
        )

        # 格式化失败时应返回原始模板
        with pytest.raises(ValidationError) as exc_info:
            field.validate("abc")
        assert exc_info.value.message == "长度至少 {missing_param} 个字符"

    @pytest.mark.error_messages
    def test_empty_error_messages(self):
        """测试空错误消息字典"""
        field = StringField(required=True, error_messages={})
        with pytest.raises(ValidationError) as exc_info:
            field.validate(None)
        # 应该使用默认消息
        assert exc_info.value.message == "This field is required"

    @pytest.mark.error_messages
    def test_none_error_messages(self):
        """测试 None 错误消息"""
        field = StringField(required=True, error_messages=None)
        with pytest.raises(ValidationError) as exc_info:
            field.validate(None)
        # 应该使用默认消息
        assert exc_info.value.message == "This field is required"


class TestMultilingualSupport:
    """多语言支持测试"""

    @pytest.mark.error_messages
    @pytest.mark.skipif(
        sys.version_info[0] < 3, reason="Unicode regex issues in Python 2"
    )
    def test_chinese_error_messages(self):
        """测试中文错误消息"""
        field = StringField(
            min_length=2,
            regex=r"^[a-zA-Z\u4e00-\u9fa5]+$",
            error_messages={
                "min_length": "长度不能少于{min_length}个字符",
                "regex": "只能包含字母和中文字符",
            },
        )

        # 测试最小长度错误
        with pytest.raises(ValidationError) as exc_info:
            field.validate("a")
        assert exc_info.value.message == "长度不能少于2个字符"

        # 测试正则错误
        with pytest.raises(ValidationError) as exc_info:
            field.validate("hello123")
        assert exc_info.value.message == "只能包含字母和中文字符"

    @pytest.mark.error_messages
    @pytest.mark.skipif(
        sys.version_info[0] < 3, reason="Unicode regex issues in Python 2"
    )
    def test_english_error_messages(self):
        """测试英文错误消息"""
        field = StringField(
            min_length=2,
            regex=r"^[a-zA-Z\u4e00-\u9fa5]+$",
            error_messages={
                "min_length": "Must be at least {min_length} characters long",
                "regex": "Only letters and Chinese characters are allowed",
            },
        )

        # 测试最小长度错误
        with pytest.raises(ValidationError) as exc_info:
            field.validate("a")
        assert exc_info.value.message == "Must be at least 2 characters long"

        # 测试正则错误
        with pytest.raises(ValidationError) as exc_info:
            field.validate("hello123")
        assert (
            exc_info.value.message == "Only letters and Chinese characters are allowed"
        )

    @pytest.mark.error_messages
    @pytest.mark.skipif(
        sys.version_info[0] < 3, reason="Unicode regex issues in Python 2"
    )
    def test_successful_validation(self):
        """测试成功验证"""
        chinese_field = StringField(
            min_length=2,
            regex=r"^[a-zA-Z\u4e00-\u9fa5]+$",
            error_messages={"min_length": "长度不能少于{min_length}个字符"},
        )

        english_field = StringField(
            min_length=2,
            regex=r"^[a-zA-Z\u4e00-\u9fa5]+$",
            error_messages={
                "min_length": "Must be at least {min_length} characters long"
            },
        )

        # 测试成功验证
        result1 = chinese_field.validate("你好")
        result2 = english_field.validate("Hello")

        assert result1 == "你好"
        assert result2 == "Hello"
