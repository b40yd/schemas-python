#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义错误消息示例

演示如何使用自定义错误消息功能：
- 基础自定义错误消息
- 多语言支持
- 错误消息模板格式化
- 在 dataclass 中使用自定义错误消息
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from schema_dataclass import (
    StringField,
    NumberField,
    ListField,
    ValidationError,
    dataclass,
)


def example_basic_custom_messages():
    """基础自定义错误消息示例"""
    print("=== 基础自定义错误消息示例 ===\n")

    # 1. 自定义字符串字段错误消息
    print("1. 自定义字符串字段错误消息:")
    username_field = StringField(
        min_length=3,
        max_length=20,
        regex=r"^[a-zA-Z][a-zA-Z0-9_]*$",
        error_messages={
            "required": "用户名是必填项",
            "min_length": "用户名至少需要 {min_length} 个字符",
            "max_length": "用户名不能超过 {max_length} 个字符",
            "regex": "用户名必须以字母开头，只能包含字母、数字和下划线",
            "invalid_type": "用户名必须是字符串类型",
        },
    )

    # 测试各种错误情况
    test_cases = [
        ("ab", "用户名太短"),
        ("verylongusernamethatexceedslimit", "用户名太长"),
        ("123invalid", "用户名格式错误"),
        (123, "用户名类型错误"),
    ]

    for test_value, description in test_cases:
        try:
            username_field.validate(test_value)
            print("  ✓ {}: 验证通过".format(description))
        except ValidationError as e:
            print("  ✗ {}: {}".format(description, e.message))

    # 2. 自定义数字字段错误消息
    print("\n2. 自定义数字字段错误消息:")
    age_field = NumberField(
        minvalue=0,
        maxvalue=120,
        error_messages={
            "required": "年龄是必填项",
            "minvalue": "年龄不能小于 {minvalue} 岁",
            "maxvalue": "年龄不能大于 {maxvalue} 岁",
            "invalid_type": "年龄必须是数字类型",
        },
    )

    test_cases = [
        (-5, "年龄为负数"),
        (150, "年龄超出范围"),
        ("not_a_number", "年龄类型错误"),
    ]

    for test_value, description in test_cases:
        try:
            age_field.validate(test_value)
            print("  ✓ {}: 验证通过".format(description))
        except ValidationError as e:
            print("  ✗ {}: {}".format(description, e.message))

    # 3. 自定义列表字段错误消息
    print("\n3. 自定义列表字段错误消息:")
    tags_field = ListField(
        item_type=str,
        min_length=1,
        max_length=5,
        error_messages={
            "min_length": "至少需要 {min_length} 个标签",
            "max_length": "最多只能有 {max_length} 个标签",
            "invalid_list_item": "第 {index} 个标签必须是字符串类型",
        },
    )

    test_cases = [
        ([], "标签列表为空"),
        (["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"], "标签过多"),
        (["tag1", 123, "tag3"], "标签类型错误"),
    ]

    for test_value, description in test_cases:
        try:
            tags_field.validate(test_value)
            print("  ✓ {}: 验证通过".format(description))
        except ValidationError as e:
            print("  ✗ {}: {}".format(description, e.message))


def example_multilingual_messages():
    """多语言错误消息示例"""
    print("\n=== 多语言错误消息示例 ===\n")

    # 中文错误消息
    print("1. 中文错误消息:")
    chinese_field = StringField(
        min_length=2,
        max_length=10,
        regex=r"^[\u4e00-\u9fa5a-zA-Z\s]+$",
        error_messages={
            "required": "此字段为必填项",
            "min_length": "长度不能少于{min_length}个字符",
            "max_length": "长度不能超过{max_length}个字符",
            "regex": "只能包含中文、英文字母和空格",
            "invalid_type": "必须是字符串类型",
        },
    )

    test_values = ["a", "Hello World 你好", "invalid123"]
    for value in test_values:
        try:
            result = chinese_field.validate(value)
            print("  ✓ '{}' 验证通过".format(value))
        except ValidationError as e:
            print("  ✗ '{}' 验证失败: {}".format(value, e.message))

    # 英文错误消息
    print("\n2. 英文错误消息:")
    english_field = StringField(
        min_length=2,
        max_length=10,
        regex=r"^[\u4e00-\u9fa5a-zA-Z\s]+$",
        error_messages={
            "required": "This field is required",
            "min_length": "Must be at least {min_length} characters long",
            "max_length": "Must be at most {max_length} characters long",
            "regex": "Only Chinese characters, English letters and spaces are allowed",
            "invalid_type": "Must be a string",
        },
    )

    for value in test_values:
        try:
            result = english_field.validate(value)
            print("  ✓ '{}' validation passed".format(value))
        except ValidationError as e:
            print("  ✗ '{}' validation failed: {}".format(value, e.message))


def example_dataclass_custom_messages():
    """DataClass 中的自定义错误消息示例"""
    print("\n=== DataClass 中的自定义错误消息示例 ===\n")

    @dataclass
    class User(object):
        # 用户名字段 - 中文错误消息
        username = StringField(
            min_length=3,
            max_length=20,
            regex=r"^[a-zA-Z][a-zA-Z0-9_]*$",
            error_messages={
                "required": "用户名是必填项",
                "min_length": "用户名至少需要 {min_length} 个字符",
                "max_length": "用户名不能超过 {max_length} 个字符",
                "regex": "用户名必须以字母开头，只能包含字母、数字和下划线",
            },
        )

        # 年龄字段 - 中文错误消息
        age = NumberField(
            minvalue=0,
            maxvalue=120,
            error_messages={
                "required": "年龄是必填项",
                "minvalue": "年龄不能小于 {minvalue} 岁",
                "maxvalue": "年龄不能大于 {maxvalue} 岁",
                "invalid_type": "年龄必须是数字",
            },
        )

        # 邮箱字段 - 中文错误消息
        email = StringField(
            regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            error_messages={
                "required": "邮箱地址是必填项",
                "regex": "请输入有效的邮箱地址格式",
                "invalid_type": "邮箱地址必须是字符串",
            },
        )

        # 标签字段 - 中文错误消息
        tags = ListField(
            item_type=str,
            required=False,
            min_length=1,
            max_length=5,
            error_messages={
                "min_length": "至少需要 {min_length} 个标签",
                "max_length": "最多只能有 {max_length} 个标签",
                "invalid_list_item": "第 {index} 个标签必须是字符串",
            },
        )

    print("1. 测试各种验证错误:")

    # 用户名错误
    try:
        User(username="ab", age=25, email="test@example.com")
    except ValidationError as e:
        print("  ✗ 用户名长度错误: {}".format(e.message))

    # 年龄错误
    try:
        User(username="testuser", age=150, email="test@example.com")
    except ValidationError as e:
        print("  ✗ 年龄范围错误: {}".format(e.message))

    # 邮箱错误
    try:
        User(username="testuser", age=25, email="invalid-email")
    except ValidationError as e:
        print("  ✗ 邮箱格式错误: {}".format(e.message))

    # 标签错误
    try:
        User(username="testuser", age=25, email="test@example.com", tags=[])
    except ValidationError as e:
        print("  ✗ 标签数量错误: {}".format(e.message))

    print("\n2. 成功创建用户:")
    try:
        user = User(
            username="alice123",
            age=28,
            email="alice@example.com",
            tags=["developer", "python"],
        )
        print("  ✓ 用户创建成功!")
        print("    用户名: {}".format(user.username))
        print("    年龄: {}".format(user.age))
        print("    邮箱: {}".format(user.email))
        print("    标签: {}".format(user.tags))
    except ValidationError as e:
        print("  ✗ 用户创建失败: {}".format(e.message))


def example_advanced_formatting():
    """高级格式化示例"""
    print("\n=== 高级格式化示例 ===\n")

    # 1. 复杂的错误消息模板
    print("1. 复杂的错误消息模板:")
    password_field = StringField(
        min_length=8,
        max_length=32,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
        error_messages={
            "required": "密码是必填项",
            "min_length": "密码长度至少需要 {min_length} 个字符",
            "max_length": "密码长度不能超过 {max_length} 个字符",
            "regex": "密码必须包含至少一个小写字母、一个大写字母、一个数字和一个特殊字符(@$!%*?&)",
        },
    )

    test_passwords = [
        ("weak", "弱密码"),
        ("WeakPassword", "缺少数字和特殊字符"),
        ("WeakPassword123", "缺少特殊字符"),
        ("WeakPassword123!", "强密码"),
    ]

    for password, description in test_passwords:
        try:
            result = password_field.validate(password)
            print("  ✓ {}: 验证通过".format(description))
        except ValidationError as e:
            print("  ✗ {}: {}".format(description, e.message))

    # 2. 格式化参数缺失处理
    print("\n2. 格式化参数缺失处理:")
    field_with_missing_param = StringField(
        min_length=5,
        error_messages={
            "min_length": "长度至少 {missing_param} 个字符"
        },  # 故意使用错误的参数名
    )

    try:
        field_with_missing_param.validate("abc")
    except ValidationError as e:
        print("  ✗ 格式化失败时返回原始模板: {}".format(e.message))


def example_business_scenarios():
    """业务场景示例"""
    print("\n=== 业务场景示例 ===\n")

    @dataclass
    class Product(object):
        name = StringField(
            min_length=1,
            max_length=100,
            error_messages={
                "required": "产品名称不能为空",
                "min_length": "产品名称至少需要 {min_length} 个字符",
                "max_length": "产品名称不能超过 {max_length} 个字符",
            },
        )

        price = NumberField(
            minvalue=0.01,
            error_messages={
                "required": "价格是必填项",
                "minvalue": "价格必须大于 {minvalue} 元",
                "invalid_type": "价格必须是数字",
            },
        )

        category = StringField(
            choices=["电子产品", "服装", "食品", "图书", "家居"],
            error_messages={
                "required": "请选择产品类别",
                "choices": "产品类别必须是以下之一: {choices}",
            },
        )

        sku = StringField(
            regex=r"^[A-Z]{2}\d{6}$",
            error_messages={
                "required": "SKU编码是必填项",
                "regex": "SKU编码格式错误，应为两个大写字母加六位数字 (如: AB123456)",
            },
        )

    print("1. 测试产品创建:")

    # 成功创建
    try:
        product = Product(
            name="智能手机", price=2999.99, category="电子产品", sku="EL123456"
        )
        print("  ✓ 产品创建成功: {}".format(product.name))
    except ValidationError as e:
        print("  ✗ 产品创建失败: {}".format(e.message))

    # 各种错误情况
    error_cases = [
        (
            {"name": "", "price": 100, "category": "电子产品", "sku": "EL123456"},
            "产品名称为空",
        ),
        (
            {"name": "测试产品", "price": 0, "category": "电子产品", "sku": "EL123456"},
            "价格为0",
        ),
        (
            {
                "name": "测试产品",
                "price": 100,
                "category": "无效类别",
                "sku": "EL123456",
            },
            "无效类别",
        ),
        (
            {
                "name": "测试产品",
                "price": 100,
                "category": "电子产品",
                "sku": "invalid",
            },
            "无效SKU",
        ),
    ]

    for product_data, description in error_cases:
        try:
            Product(**product_data)
            print("  ✓ {}: 验证通过".format(description))
        except ValidationError as e:
            print("  ✗ {}: {}".format(description, e.message))


if __name__ == "__main__":
    print("Schemas DataClass - 自定义错误消息示例")
    print("=" * 60)

    example_basic_custom_messages()
    example_multilingual_messages()
    example_dataclass_custom_messages()
    example_advanced_formatting()
    example_business_scenarios()

    print("\n" + "=" * 60)
    print("自定义错误消息示例运行完成！")
    print("\n这个示例展示了如何使用自定义错误消息功能来提供更友好的用户体验。")
    print("您可以根据自己的业务需求定制错误消息，支持多语言和复杂的格式化。")
