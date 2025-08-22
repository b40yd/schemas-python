# -*- coding: utf-8 -*-
"""
自定义错误消息功能演示
展示如何在 Python2 兼容的 Field 类型中使用自定义错误消息
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass

def demo_basic_usage():
    """基础用法演示"""
    print("=== 基础用法演示 ===\n")
    
    # 创建带有自定义错误消息的字段
    username_field = StringField(
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
        error_messages={
            'required': '用户名是必填项',
            'min_length': '用户名至少需要 {min_length} 个字符',
            'max_length': '用户名不能超过 {max_length} 个字符',
            'regex': '用户名必须以字母开头，只能包含字母、数字和下划线',
            'invalid_type': '用户名必须是字符串类型'
        }
    )
    
    age_field = NumberField(
        minvalue=0,
        maxvalue=150,
        error_messages={
            'required': '年龄是必填项',
            'minvalue': '年龄不能小于 {minvalue} 岁',
            'maxvalue': '年龄不能大于 {maxvalue} 岁',
            'invalid_type': '年龄必须是数字类型'
        }
    )
    
    # 测试各种错误情况
    test_cases = [
        ("用户名长度测试", username_field, "ab"),
        ("用户名格式测试", username_field, "123invalid"),
        ("年龄范围测试", age_field, -5),
        ("年龄类型测试", age_field, "not_a_number"),
    ]
    
    for test_name, field, test_value in test_cases:
        print("{}:".format(test_name))
        try:
            result = field.validate(test_value)
            print("  ✓ 验证通过: {}".format(result))
        except ValidationError as e:
            print("  ✗ 验证失败: {}".format(e.message))
        print()

def demo_dataclass_integration():
    """与 dataclass 集成演示"""
    print("=== 与 dataclass 集成演示 ===\n")
    
    @dataclass
    class Product(object):
        name = StringField(
            min_length=1,
            max_length=100,
            error_messages={
                'required': '产品名称不能为空',
                'min_length': '产品名称至少需要 {min_length} 个字符',
                'max_length': '产品名称不能超过 {max_length} 个字符'
            }
        )
        
        price = NumberField(
            minvalue=0.01,
            error_messages={
                'required': '价格是必填项',
                'minvalue': '价格必须大于 {minvalue} 元',
                'invalid_type': '价格必须是数字'
            }
        )
        
        category = StringField(
            choices=['电子产品', '服装', '食品', '图书'],
            error_messages={
                'required': '请选择产品类别',
                'choices': '产品类别必须是以下之一: {choices}'
            }
        )
        
        tags = ListField(
            item_type=str,
            required=False,
            error_messages={
                'invalid_list_item': '标签列表中第 {index} 项必须是字符串类型'
            }
        )
    
    # 测试成功创建
    print("1. 成功创建产品:")
    try:
        product = Product(
            name="智能手机",
            price=2999.99,
            category="电子产品",
            tags=["智能", "通讯", "便携"]
        )
        print("  ✓ 产品创建成功!")
        print("    名称: {}".format(product.name))
        print("    价格: {} 元".format(product.price))
        print("    类别: {}".format(product.category))
        print("    标签: {}".format(product.tags))
    except ValidationError as e:
        print("  ✗ 创建失败: {}".format(e.message))
    
    print("\n2. 测试各种错误情况:")
    
    # 测试价格错误
    print("  价格错误测试:")
    try:
        Product(name="测试产品", price=-10, category="电子产品")
        print("    ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("    ✓ 价格错误: {}".format(e.message))
    
    # 测试类别错误
    print("  类别错误测试:")
    try:
        Product(name="测试产品", price=100, category="无效类别")
        print("    ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("    ✓ 类别错误: {}".format(e.message))
    
    # 测试标签类型错误
    print("  标签类型错误测试:")
    try:
        Product(name="测试产品", price=100, category="电子产品", tags=["标签1", 123, "标签3"])
        print("    ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("    ✓ 标签错误: {}".format(e.message))

def demo_multilingual_support():
    """多语言支持演示"""
    print("\n=== 多语言支持演示 ===\n")
    
    # 中文错误消息
    chinese_field = StringField(
        min_length=2,
        max_length=50,
        regex=r'^[\u4e00-\u9fa5a-zA-Z\s]+$',
        error_messages={
            'required': '此字段为必填项',
            'min_length': '长度不能少于{min_length}个字符',
            'max_length': '长度不能超过{max_length}个字符',
            'regex': '只能包含中文、英文字母和空格',
            'invalid_type': '必须是字符串类型'
        }
    )
    
    # 英文错误消息
    english_field = StringField(
        min_length=2,
        max_length=50,
        regex=r'^[\u4e00-\u9fa5a-zA-Z\s]+$',
        error_messages={
            'required': 'This field is required',
            'min_length': 'Must be at least {min_length} characters long',
            'max_length': 'Must be at most {max_length} characters long',
            'regex': 'Only Chinese characters, English letters and spaces are allowed',
            'invalid_type': 'Must be a string'
        }
    )
    
    test_values = ["a", "Hello World 你好", "invalid123"]
    
    print("中文错误消息:")
    for value in test_values:
        try:
            result = chinese_field.validate(value)
            print("  ✓ '{}' 验证通过".format(value))
        except ValidationError as e:
            print("  ✗ '{}' 验证失败: {}".format(value, e.message))
    
    print("\n英文错误消息:")
    for value in test_values:
        try:
            result = english_field.validate(value)
            print("  ✓ '{}' validation passed".format(value))
        except ValidationError as e:
            print("  ✗ '{}' validation failed: {}".format(value, e.message))

def demo_advanced_features():
    """高级功能演示"""
    print("\n=== 高级功能演示 ===\n")
    
    # 演示错误消息格式化的灵活性
    print("1. 错误消息格式化演示:")
    
    field = NumberField(
        minvalue=18,
        maxvalue=65,
        error_messages={
            'minvalue': '年龄必须满 {minvalue} 周岁才能注册',
            'maxvalue': '年龄不能超过 {maxvalue} 周岁',
            'invalid_type': '请输入有效的年龄数字'
        }
    )
    
    test_ages = [16, 70, "abc"]
    for age in test_ages:
        try:
            field.validate(age)
            print("  ✓ 年龄 {} 验证通过".format(age))
        except ValidationError as e:
            print("  ✗ 年龄 {} 验证失败: {}".format(age, e.message))
    
    # 演示复杂的正则表达式错误消息
    print("\n2. 复杂正则表达式错误消息:")
    
    email_field = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        error_messages={
            'regex': '请输入有效的邮箱地址格式 (例: user@example.com)'
        }
    )
    
    test_emails = ["valid@example.com", "invalid-email", "@invalid.com", "user@"]
    for email in test_emails:
        try:
            email_field.validate(email)
            print("  ✓ 邮箱 '{}' 验证通过".format(email))
        except ValidationError as e:
            print("  ✗ 邮箱 '{}' 验证失败: {}".format(email, e.message))

if __name__ == "__main__":
    demo_basic_usage()
    demo_dataclass_integration()
    demo_multilingual_support()
    demo_advanced_features()
    
    print("\n=== 演示完成 ===")
    print("自定义错误消息功能已成功集成到 Field 类型系统中！")
    print("支持的功能:")
    print("- 所有验证类型的自定义错误消息")
    print("- 错误消息模板格式化")
    print("- 多语言支持")
    print("- 与 dataclass 完美集成")
    print("- Python 2/3 兼容性")
