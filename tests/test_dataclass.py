# -*- coding: utf-8 -*-
"""
DataClass 功能测试
"""

import pytest
from schema_dataclass import (
    StringField,
    NumberField,
    ListField,
    ValidationError,
    dataclass,
    validate,
)


class TestDataClassBasic:
    """DataClass 基础功能测试"""

    @pytest.mark.dataclass
    def test_dataclass_creation(self, sample_dataclass):
        """测试 dataclass 创建"""
        User = sample_dataclass

        user = User(
            name="Alice",
            age=25,
            email="alice@example.com",
            tags=["developer", "python"],
        )

        assert user.name == "Alice"
        assert user.age == 25
        assert user.email == "alice@example.com"
        assert user.tags == ["developer", "python"]

    @pytest.mark.dataclass
    def test_dataclass_validation(self, sample_dataclass):
        """测试 dataclass 验证"""
        User = sample_dataclass

        # 测试无效姓名（太短）
        with pytest.raises(ValidationError):
            User(name="A", age=25, email="alice@example.com")

        # 测试无效年龄（超出范围）
        with pytest.raises(ValidationError):
            User(name="Alice", age=150, email="alice@example.com")

        # 测试无效邮箱格式
        with pytest.raises(ValidationError):
            User(name="Alice", age=25, email="invalid-email")

    @pytest.mark.dataclass
    def test_optional_fields(self, sample_dataclass):
        """测试可选字段"""
        User = sample_dataclass

        # age 和 tags 是可选的，只提供必填字段
        user = User(name="Bob", email="bob@example.com")
        assert user.age is None
        assert user.tags is None

        # 也可以提供可选字段
        user2 = User(name="Alice", email="alice@example.com", age=30, tags=["dev"])
        assert user2.age == 30
        assert user2.tags == ["dev"]

    @pytest.mark.dataclass
    def test_to_dict_method(self, sample_dataclass):
        """测试 to_dict 方法"""
        User = sample_dataclass

        user = User(
            name="Charlie", age=35, email="charlie@example.com", tags=["manager"]
        )

        user_dict = user.to_dict()
        expected = {
            "name": "Charlie",
            "age": 35,
            "email": "charlie@example.com",
            "tags": ["manager"],
        }

        assert user_dict == expected

    @pytest.mark.dataclass
    def test_field_access_methods(self, sample_dataclass):
        """测试字段访问方法"""
        User = sample_dataclass

        user = User(name="David", age=40, email="david@example.com")

        # 属性访问
        assert user.name == "David"

        # 索引访问
        assert user["name"] == "David"

        # get 方法访问
        assert user.get("name") == "David"
        assert user.get("nonexistent", "default") == "default"


class TestDataClassWithCustomErrors:
    """带自定义错误消息的 DataClass 测试"""

    @pytest.mark.dataclass
    @pytest.mark.error_messages
    def test_custom_error_in_dataclass(self, sample_dataclass_with_custom_errors):
        """测试 dataclass 中的自定义错误消息"""
        Product = sample_dataclass_with_custom_errors

        # 测试产品名称长度错误
        with pytest.raises(ValidationError) as exc_info:
            Product(name="", price=10.0, category="电子产品")
        assert exc_info.value.message == "产品名称至少需要 1 个字符"

        # 测试价格错误
        with pytest.raises(ValidationError) as exc_info:
            Product(name="测试产品", price=0, category="电子产品")
        assert exc_info.value.message == "价格必须大于 0.01 元"

        # 测试类别错误
        with pytest.raises(ValidationError) as exc_info:
            Product(name="测试产品", price=10.0, category="无效类别")
        # 检查错误消息开头，避免 Python 2/3 Unicode 表示差异
        error_message = exc_info.value.message
        assert error_message.startswith("产品类别必须是以下之一")

    @pytest.mark.dataclass
    @pytest.mark.error_messages
    def test_successful_creation_with_custom_errors(
        self, sample_dataclass_with_custom_errors
    ):
        """测试带自定义错误消息的成功创建"""
        Product = sample_dataclass_with_custom_errors

        product = Product(name="智能手机", price=2999.99, category="电子产品")

        assert product.name == "智能手机"
        assert product.price == 2999.99
        assert product.category == "电子产品"


class TestCustomValidation:
    """自定义验证测试"""

    @pytest.mark.dataclass
    @pytest.mark.validation
    def test_custom_validation_decorator(self):
        """测试自定义验证装饰器"""

        @dataclass
        class Product(object):
            name = StringField()
            price = NumberField(minvalue=0)

            @validate("name")
            def validate_name_no_special_chars(self, name):
                """产品名称不能包含特殊字符"""
                if not name.replace(" ", "").replace("-", "").isalnum():
                    raise ValidationError(
                        "Name can only contain letters, numbers, spaces, and hyphens"
                    )

            @validate("price")
            def validate_price_reasonable(self, price):
                """价格必须合理"""
                if price > 10000:
                    raise ValidationError("Price cannot exceed $10,000")

        # 测试有效产品
        product = Product(name="Test Product", price=99.99)
        assert product.name == "Test Product"
        assert product.price == 99.99

        # 测试无效名称
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Test@Product", price=99.99)
        assert "can only contain letters" in str(exc_info.value)

        # 测试无效价格
        with pytest.raises(ValidationError) as exc_info:
            Product(name="Test Product", price=15000)
        assert "cannot exceed $10,000" in str(exc_info.value)

    @pytest.mark.dataclass
    @pytest.mark.validation
    def test_multiple_custom_validations(self):
        """测试多个自定义验证"""

        @dataclass
        class User(object):
            username = StringField(min_length=3)
            password = StringField(min_length=8)

            @validate("username")
            def validate_username_format(self, username):
                if not username.isalnum():
                    raise ValidationError("Username must be alphanumeric")

            @validate("password")
            def validate_password_strength(self, password):
                if not any(c.isupper() for c in password):
                    raise ValidationError(
                        "Password must contain at least one uppercase letter"
                    )
                if not any(c.isdigit() for c in password):
                    raise ValidationError("Password must contain at least one digit")

        # 测试有效用户
        user = User(username="testuser", password="Password123")
        assert user.username == "testuser"
        assert user.password == "Password123"

        # 测试无效用户名
        with pytest.raises(ValidationError) as exc_info:
            User(username="test_user", password="Password123")
        assert "must be alphanumeric" in str(exc_info.value)

        # 测试无效密码（缺少大写字母）
        with pytest.raises(ValidationError) as exc_info:
            User(username="testuser", password="password123")
        assert "uppercase letter" in str(exc_info.value)

        # 测试无效密码（缺少数字）
        with pytest.raises(ValidationError) as exc_info:
            User(username="testuser", password="Password")
        assert "contain at least one digit" in str(exc_info.value)


class TestCustomGetters:
    """自定义 getter 方法测试"""

    @pytest.mark.dataclass
    def test_custom_getter_method(self):
        """测试自定义 getter 方法"""

        @dataclass
        class BlogPost(object):
            title = StringField()
            status = StringField(default="draft")

            def get_title(self):
                """自定义获取标题的方法"""
                title = self.__dict__.get("title", "")
                status = self.__dict__.get("status", "draft")
                return "[{0}] {1}".format(status.upper(), title)

        post = BlogPost(title="Hello World")

        # 应该调用自定义的 get_title 方法
        assert post.title == "[DRAFT] Hello World"

        # 修改状态
        post.status = "published"
        assert post.title == "[PUBLISHED] Hello World"

    @pytest.mark.dataclass
    def test_getter_priority(self):
        """测试 getter 方法优先级"""

        @dataclass
        class TestClass(object):
            value = StringField(default="default")
            description = StringField()

            def get_value(self):
                return "custom_getter_value"

        obj = TestClass()

        # get_value 方法应该优先于默认值
        assert obj.value == "custom_getter_value"

        # 但直接访问 __dict__ 应该显示实际存储的值
        assert obj.__dict__.get("value") is "default"
        assert obj.__dict__.get("description") is None  # 没有设置实际值

    @pytest.mark.dataclass
    def test_getter_self_reference(self):
        """测试 getter 方法优先级"""

        @dataclass
        class TestClass(object):
            value = StringField(default="default")
            description = StringField()

            def get_value(self):
                return "custom_getter_value"

            def get_description(self):
                if not self.description is None:
                    return self.description
                else:
                    return "No description"

        obj = TestClass()

        # get_value 方法应该优先于默认值
        assert obj.value == "custom_getter_value"
        assert (
            obj.description == "No description"
        )  # get_description 返回 No description

        # 但直接访问 __dict__ 应该显示实际存储的值
        assert obj.__dict__.get("value") is "default"
        assert obj.__dict__.get("description") is None  # 没有设置实际值
