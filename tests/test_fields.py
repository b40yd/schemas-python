# -*- coding: utf-8 -*-
"""
字段类型测试
"""

import pytest
import sys
from schema_dataclass import StringField, NumberField, ListField, ValidationError


class TestStringField:
    """StringField 测试类"""

    @pytest.mark.unit
    def test_valid_string(self, sample_string_field):
        """测试有效字符串"""
        result = sample_string_field.validate("hello")
        assert result == "hello"

    @pytest.mark.unit
    def test_min_length_validation(self, sample_string_field):
        """测试最小长度验证"""
        with pytest.raises(ValidationError) as exc_info:
            sample_string_field.validate("a")
        assert "Length must be at least 2" in str(exc_info.value)

    @pytest.mark.unit
    def test_max_length_validation(self):
        """测试最大长度验证"""
        field = StringField(max_length=5)
        with pytest.raises(ValidationError) as exc_info:
            field.validate("toolong")
        assert "Length must be at most 5" in str(exc_info.value)

    @pytest.mark.unit
    def test_regex_validation(self, sample_string_field):
        """测试正则表达式验证"""
        # 有效格式
        assert sample_string_field.validate("hello123") == "hello123"

        # 无效格式（以数字开头）
        with pytest.raises(ValidationError) as exc_info:
            sample_string_field.validate("123hello")
        assert "does not match pattern" in str(exc_info.value)

    @pytest.mark.unit
    def test_choices_validation(self):
        """测试选择项验证"""
        field = StringField(choices=["red", "green", "blue"])

        # 有效选择
        assert field.validate("red") == "red"

        # 无效选择
        with pytest.raises(ValidationError) as exc_info:
            field.validate("yellow")
        assert "must be one o" in str(exc_info.value)

    @pytest.mark.unit
    def test_required_validation(self):
        """测试必填验证"""
        field = StringField(required=True)

        with pytest.raises(ValidationError) as exc_info:
            field.validate(None)
        assert "required" in str(exc_info.value)

    @pytest.mark.unit
    def test_optional_field_explicit(self):
        """测试显式设置的可选字段"""
        field = StringField(required=False, default="default_value")

        result = field.validate(None)
        assert result == "default_value"

    @pytest.mark.unit
    def test_optional_field_default(self):
        """测试默认的可选字段行为 (required=False)"""
        field = StringField()  # 默认 required=False

        # None 应该返回 None (没有默认值)
        result = field.validate(None)
        assert result is None

        # 有效值应该正常验证
        result = field.validate("test")
        assert result == "test"

    @pytest.mark.unit
    def test_required_field_behavior(self):
        """测试必填字段的完整行为"""
        # 必填字段
        required_field = StringField(required=True)

        # 测试 None 值应该失败
        with pytest.raises(ValidationError) as exc_info:
            required_field.validate(None)
        assert "required" in str(exc_info.value)

        # 测试空字符串应该失败
        with pytest.raises(ValidationError) as exc_info:
            required_field.validate("")
        assert "required" in str(exc_info.value)

        # 测试有效值应该成功
        result = required_field.validate("valid")
        assert result == "valid"

    @pytest.mark.unit
    def test_invalid_type(self):
        """测试无效类型"""
        field = StringField()

        with pytest.raises(ValidationError) as exc_info:
            field.validate(123)
        assert "must be a string" in str(exc_info.value)


class TestNumberField:
    """NumberField 测试类"""

    @pytest.mark.unit
    def test_valid_number(self, sample_number_field):
        """测试有效数字"""
        assert sample_number_field.validate(25) == 25
        assert sample_number_field.validate(25.5) == 25.5

    @pytest.mark.unit
    def test_minvalue_validation(self, sample_number_field):
        """测试最小值验证"""
        with pytest.raises(ValidationError) as exc_info:
            sample_number_field.validate(-1)
        assert "must be at least 0" in str(exc_info.value)

    @pytest.mark.unit
    def test_maxvalue_validation(self, sample_number_field):
        """测试最大值验证"""
        with pytest.raises(ValidationError) as exc_info:
            sample_number_field.validate(150)
        assert "must be at most 120" in str(exc_info.value)

    @pytest.mark.unit
    def test_choices_validation(self):
        """测试数字选择项验证"""
        field = NumberField(choices=[1, 2, 3, 5, 8])

        # 有效选择
        assert field.validate(3) == 3

        # 无效选择
        with pytest.raises(ValidationError) as exc_info:
            field.validate(4)
        assert "must be one o" in str(exc_info.value)

    @pytest.mark.unit
    def test_invalid_type(self):
        """测试无效类型"""
        field = NumberField()

        with pytest.raises(ValidationError) as exc_info:
            field.validate("not_a_number")
        assert "must be a number" in str(exc_info.value)

    @pytest.mark.unit
    def test_optional_field_default(self):
        """测试默认的可选字段行为 (required=False)"""
        field = NumberField()  # 默认 required=False

        # None 应该返回 None (没有默认值)
        result = field.validate(None)
        assert result is None

        # 有效值应该正常验证
        result = field.validate(42)
        assert result == 42

    @pytest.mark.unit
    @pytest.mark.skipif(sys.version_info[0] >= 3, reason="Python 2 specific test")
    def test_python2_long_type(self):
        """测试 Python 2 的 long 类型"""
        field = NumberField()
        # 在 Python 2 中创建 long 类型
        import sys

        if sys.version_info[0] < 3:
            long_value = long(123)  # noqa: F821
            assert field.validate(long_value) == long_value


class TestListField:
    """ListField 测试类"""

    @pytest.mark.unit
    def test_valid_list(self, sample_list_field):
        """测试有效列表"""
        result = sample_list_field.validate(["item1", "item2"])
        assert result == ["item1", "item2"]

    @pytest.mark.unit
    def test_min_length_validation(self, sample_list_field):
        """测试列表最小长度验证"""
        with pytest.raises(ValidationError) as exc_info:
            sample_list_field.validate([])
        assert "Length must be at least 1" in str(exc_info.value)

    @pytest.mark.unit
    def test_max_length_validation(self, sample_list_field):
        """测试列表最大长度验证"""
        long_list = ["item{}".format(i) for i in range(10)]
        with pytest.raises(ValidationError) as exc_info:
            sample_list_field.validate(long_list)
        assert "Length must be at most 5" in str(exc_info.value)

    @pytest.mark.unit
    def test_item_type_validation(self):
        """测试列表项类型验证"""
        field = ListField(item_type=int)

        # 有效类型
        assert field.validate([1, 2, 3]) == [1, 2, 3]

        # 无效类型
        with pytest.raises(ValidationError) as exc_info:
            field.validate([1, "invalid", 3])
        assert "invalid type" in str(exc_info.value)
        assert "index 1" in str(exc_info.value)

    @pytest.mark.unit
    def test_nested_field_validation(self):
        """测试嵌套字段验证"""
        nested_field = StringField(min_length=2)
        field = ListField(item_type=nested_field)

        # 有效嵌套
        assert field.validate(["hello", "world"]) == ["hello", "world"]

        # 无效嵌套
        with pytest.raises(ValidationError):
            field.validate(["hello", "a"])  # "a" 太短

    @pytest.mark.unit
    def test_invalid_list_type(self):
        """测试无效的列表类型"""
        field = ListField(item_type=str)

        with pytest.raises(ValidationError) as exc_info:
            field.validate("not_a_list")
        assert "must be a list" in str(exc_info.value)

    @pytest.mark.unit
    def test_optional_field_default(self):
        """测试默认的可选字段行为 (required=False)"""
        field = ListField(item_type=str)  # 默认 required=False

        # None 应该返回 None (没有默认值)
        result = field.validate(None)
        assert result is None

        # 有效值应该正常验证
        result = field.validate(["test", "list"])
        assert result == ["test", "list"]
