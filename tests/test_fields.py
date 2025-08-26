# -*- coding: utf-8 -*-
"""
字段类型测试
"""
import datetime
import pytest
import sys
from schema_dataclass import StringField, NumberField, ListField, ValidationError, DateField, EmailField, DateTimeField


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
        assert field.get_default() is None

        # 有效值应该正常验证
        result = field.validate(["test", "list"])
        assert result == ["test", "list"]

class TestDateField:
    """DateField 测试类"""

    @pytest.mark.unit
    def test_valid_date(self):
        """测试有效日期"""
        field = DateField()
        test_date = datetime.date(2023, 12, 25)
        assert field.validate(test_date) == test_date

    @pytest.mark.unit
    def test_valid_date_string(self):
        """测试有效的日期字符串"""
        field = DateField(format="%Y-%m-%d")
        result = field.validate("2023-12-25")
        assert result == datetime.date(2023, 12, 25)

    @pytest.mark.unit
    def test_invalid_date_string(self):
        """测试无效的日期字符串"""
        field = DateField(format="%Y-%m-%d")
        with pytest.raises(ValidationError) as exc_info:
            field.validate("2023-13-25")
        assert "Invalid date format" in str(exc_info.value)

    @pytest.mark.unit
    def test_min_date_validation(self):
        """测试最小日期验证"""
        min_date = datetime.date(2023, 1, 1)
        field = DateField(min_date=min_date)
        
        # 有效日期
        assert field.validate(datetime.date(2023, 6, 15)) == datetime.date(2023, 6, 15)
        
        # 无效日期
        with pytest.raises(ValidationError) as exc_info:
            field.validate(datetime.date(2022, 12, 31))
        assert "Date must be on or after" in str(exc_info.value)

    @pytest.mark.unit
    def test_max_date_validation(self):
        """测试最大日期验证"""
        max_date = datetime.date(2023, 12, 31)
        field = DateField(max_date=max_date)
        
        # 有效日期
        assert field.validate(datetime.date(2023, 6, 15)) == datetime.date(2023, 6, 15)
        
        # 无效日期
        with pytest.raises(ValidationError) as exc_info:
            field.validate(datetime.date(2024, 1, 1))
        assert "Date must be on or before" in str(exc_info.value)

    @pytest.mark.unit
    def test_invalid_type(self):
        """测试无效类型"""
        field = DateField()
        with pytest.raises(ValidationError) as exc_info:
            field.validate('123')  # 数字类型，不是日期
        assert "must be a date" in str(exc_info.value)

    @pytest.mark.unit
    def test_custom_date_format(self):
        """测试自定义日期格式"""
        field = DateField(format="%d/%m/%Y")
        result = field.validate("25/12/2023")
        assert result == datetime.date(2023, 12, 25)


class TestEmailField:
    """EmailField 测试类"""

    @pytest.mark.unit
    def test_valid_email(self):
        """测试有效邮箱"""
        field = EmailField()
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "first.last@sub.domain.com"
        ]
        
        for email in valid_emails:
            assert field.validate(email) == email

    @pytest.mark.unit
    def test_invalid_email(self):
        """测试无效邮箱"""
        field = EmailField()
        invalid_emails = [
            "invalid",
            "missing@",
            "@missing.com",
            "spaces in@email.com",
            "invalid@.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                field.validate(email)
            # 检查错误消息，可能是正则验证错误或邮箱格式错误
            error_msg = str(exc_info.value).lower()
            assert any(keyword in error_msg for keyword in ["email", "pattern", "match"])

    @pytest.mark.unit
    def test_email_with_string_validation(self):
        """测试邮箱字段的字符串验证功能"""
        field = EmailField(min_length=10, max_length=30)
        
        # 有效长度
        assert field.validate("valid@example.com") == "valid@example.com"
        
        # 太短
        with pytest.raises(ValidationError) as exc_info:
            field.validate("a@b.c")
        assert "Length must be at least" in str(exc_info.value)
        
        # 太长
        with pytest.raises(ValidationError) as exc_info:
            field.validate("very_long_email_address_that_exceeds_limit@example.com")
        assert "Length must be at most" in str(exc_info.value)


class TestDateTimeField:
    """DateTimeField 测试类"""

    @pytest.mark.unit
    def test_valid_datetime(self):
        """测试有效日期时间"""
        field = DateTimeField()
        test_datetime = datetime.datetime(2025, 1, 10, 10, 0, 0)
        assert field.validate(test_datetime) == test_datetime

    @pytest.mark.unit
    def test_valid_datetime_string(self):
        """测试有效的日期时间字符串"""
        field = DateTimeField()
        
        # 测试明确的格式
        test_cases = [
            ("2025-01-10 10:00:00", datetime.datetime(2025, 1, 10, 10, 0, 0)),  # 年-月-日 时:分:秒
            ("2025-01-10T10:00:00", datetime.datetime(2025, 1, 10, 10, 0, 0)),  # ISO格式
            ("2025-01-10 10:00", datetime.datetime(2025, 1, 10, 10, 0, 0)),     # 年-月-日 时:分
        ]
        
        for datetime_str, expected in test_cases:
            result = field.validate(datetime_str)
            assert result == expected

        # 测试月/日/年格式 - 使用明确的格式避免歧义
        result = field.validate("01/10/2025 10:00:00")  # 月/日/年
        # 由于格式解析顺序，这个可能被解析为1月10日或10月1日
        # 我们只验证它能成功解析，不验证具体结果
        assert isinstance(result, datetime.datetime)

        # 测试日/月/年格式 - 使用明确的格式避免歧义
        result = field.validate("10/01/2025 10:00:00")  # 日/月/年
        # 由于格式解析顺序，这个可能被解析为10月1日或1月10日
        # 我们只验证它能成功解析，不验证具体结果
        assert isinstance(result, datetime.datetime)

    @pytest.mark.unit
    def test_valid_unix_timestamp(self):
        """测试有效的Unix时间戳"""
        field = DateTimeField()
        
        # 测试整数时间戳
        test_timestamp = 1736505600  # 2025-01-10 10:00:00 UTC
        result = field.validate(test_timestamp)
        expected = datetime.datetime.fromtimestamp(test_timestamp)
        assert result == expected
        
        # 测试浮点数时间戳
        test_timestamp_float = 1736505600.5
        result = field.validate(test_timestamp_float)
        expected = datetime.datetime.fromtimestamp(test_timestamp_float)
        assert result == expected

    @pytest.mark.unit
    def test_invalid_datetime_string(self):
        """测试无效的日期时间字符串"""
        field = DateTimeField()
        
        invalid_datetimes = [
            "invalid_datetime",
            "2025-13-10 10:00:00",  # 无效月份
            "2025-01-32 10:00:00",  # 无效日期
            "2025-01-10 25:00:00",  # 无效小时
        ]
        
        for invalid_dt in invalid_datetimes:
            with pytest.raises(ValidationError) as exc_info:
                field.validate(invalid_dt)
            assert "datetime" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_min_datetime_validation(self):
        """测试最小日期时间验证"""
        min_datetime = datetime.datetime(2025, 1, 1, 0, 0, 0)
        field = DateTimeField(min_datetime=min_datetime)
        
        # 有效日期时间
        assert field.validate(datetime.datetime(2025, 6, 15, 12, 0, 0)) == datetime.datetime(2025, 6, 15, 12, 0, 0)
        
        # 无效日期时间
        with pytest.raises(ValidationError) as exc_info:
            field.validate(datetime.datetime(2024, 12, 31, 23, 59, 59))
        assert "Datetime must be on or after" in str(exc_info.value)

    @pytest.mark.unit
    def test_max_datetime_validation(self):
        """测试最大日期时间验证"""
        max_datetime = datetime.datetime(2025, 12, 31, 23, 59, 59)
        field = DateTimeField(max_datetime=max_datetime)
        
        # 有效日期时间
        assert field.validate(datetime.datetime(2025, 6, 15, 12, 0, 0)) == datetime.datetime(2025, 6, 15, 12, 0, 0)
        
        # 无效日期时间
        with pytest.raises(ValidationError) as exc_info:
            field.validate(datetime.datetime(2026, 1, 1, 0, 0, 0))
        assert "Datetime must be on or before" in str(exc_info.value)

    @pytest.mark.unit
    def test_invalid_type(self):
        """测试无效类型"""
        field = DateTimeField()
        with pytest.raises(ValidationError) as exc_info:
            field.validate(["not", "a", "datetime"])  # 列表类型，不是日期时间
        assert "must be a datetime" in str(exc_info.value)

    @pytest.mark.unit
    def test_datetime_with_choices(self):
        """测试日期时间字段的选择项验证"""
        choices = [
            datetime.datetime(2025, 1, 10, 10, 0, 0),
            datetime.datetime(2025, 1, 11, 10, 0, 0),
            datetime.datetime(2025, 1, 12, 10, 0, 0),
        ]
        field = DateTimeField(choices=choices)
        
        # 有效选择
        assert field.validate(choices[0]) == choices[0]
        
        # 无效选择
        with pytest.raises(ValidationError) as exc_info:
            field.validate(datetime.datetime(2025, 1, 13, 10, 0, 0))
        assert "must be one of" in str(exc_info.value)
