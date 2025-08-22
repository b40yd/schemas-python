# -*- coding: utf-8 -*-
"""
测试自定义错误消息功能 - 使用断言方式
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass

def test_default_error_messages():
    """测试默认错误消息"""
    print("=== 测试默认错误消息 ===")

    # 测试必填字段错误
    field = StringField(required=True)
    try:
        field.validate(None)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "This field is required", f"期望: 'This field is required', 实际: '{e.message}'"
        print("✓ 默认必填错误消息正确")

    # 测试长度错误
    field = StringField(min_length=5, max_length=10)
    try:
        field.validate("abc")  # 太短
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "Length must be at least 5", f"期望: 'Length must be at least 5', 实际: '{e.message}'"
        print("✓ 默认最小长度错误消息正确")

    try:
        field.validate("abcdefghijk")  # 太长
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "Length must be at most 10", f"期望: 'Length must be at most 10', 实际: '{e.message}'"
        print("✓ 默认最大长度错误消息正确")

    # 测试数值范围错误
    field = NumberField(minvalue=10, maxvalue=100)
    try:
        field.validate(5)  # 太小
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "Value must be at least 10", f"期望: 'Value must be at least 10', 实际: '{e.message}'"
        print("✓ 默认最小值错误消息正确")

    try:
        field.validate(150)  # 太大
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "Value must be at most 100", f"期望: 'Value must be at most 100', 实际: '{e.message}'"
        print("✓ 默认最大值错误消息正确")

    # 测试选择项错误
    field = StringField(choices=['red', 'green', 'blue'])
    try:
        field.validate('yellow')
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = "Value must be one of: ['red', 'green', 'blue']"
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 默认选择项错误消息正确")

    # 测试正则表达式错误
    field = StringField(regex=r'^\d{3}-\d{4}$')  # 格式: 123-4567
    try:
        field.validate('abc-defg')
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = "Value does not match pattern: ^\d{3}-\d{4}$"
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 默认正则错误消息正确")

    # 测试类型错误
    field = StringField()
    try:
        field.validate(123)  # 数字而不是字符串
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        assert e.message == "Value must be a string", f"期望: 'Value must be a string', 实际: '{e.message}'"
        print("✓ 默认类型错误消息正确")

def test_custom_error_messages():
    """测试自定义错误消息"""
    print("\n=== 测试自定义错误消息 ===")

    # 测试自定义必填字段错误
    custom_messages = {
        'required': '这个字段是必填的，请提供一个值'
    }
    field = StringField(required=True, error_messages=custom_messages)
    try:
        field.validate(None)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '这个字段是必填的，请提供一个值'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义必填错误消息正确")

    # 测试自定义长度错误
    custom_messages = {
        'min_length': '字符串长度不能少于 {min_length} 个字符',
        'max_length': '字符串长度不能超过 {max_length} 个字符'
    }
    field = StringField(min_length=5, max_length=10, error_messages=custom_messages)
    try:
        field.validate("abc")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '字符串长度不能少于 5 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义最小长度错误消息正确")

    try:
        field.validate("abcdefghijk")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '字符串长度不能超过 10 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义最大长度错误消息正确")

    # 测试自定义数值范围错误
    custom_messages = {
        'minvalue': '数值必须大于等于 {minvalue}',
        'maxvalue': '数值必须小于等于 {maxvalue}'
    }
    field = NumberField(minvalue=10, maxvalue=100, error_messages=custom_messages)
    try:
        field.validate(5)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '数值必须大于等于 10'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义最小值错误消息正确")

    try:
        field.validate(150)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '数值必须小于等于 100'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义最大值错误消息正确")

    # 测试自定义选择项错误
    custom_messages = {
        'choices': '请选择以下选项之一: {choices}'
    }
    field = StringField(choices=['红色', '绿色', '蓝色'], error_messages=custom_messages)
    try:
        field.validate('黄色')
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = "请选择以下选项之一: ['红色', '绿色', '蓝色']"
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义选择项错误消息正确")

    # 测试自定义正则表达式错误
    custom_messages = {
        'regex': '请输入正确的电话号码格式 (例: 123-4567)'
    }
    field = StringField(regex=r'^\d{3}-\d{4}$', error_messages=custom_messages)
    try:
        field.validate('abc-defg')
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '请输入正确的电话号码格式 (例: 123-4567)'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义正则错误消息正确")

    # 测试自定义类型错误
    custom_messages = {
        'invalid_type': '输入值必须是 {expected_type} 类型'
    }
    field = StringField(error_messages=custom_messages)
    try:
        field.validate(123)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '输入值必须是 string 类型'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义类型错误消息正确")

def test_list_field_custom_errors():
    """测试列表字段的自定义错误消息"""
    print("\n=== 测试列表字段自定义错误消息 ===")

    # 测试列表项类型错误
    custom_messages = {
        'invalid_list_item': '列表中第 {index} 项的类型错误，期望类型: {expected_type}'
    }
    field = ListField(item_type=int, error_messages=custom_messages)
    try:
        field.validate([1, 2, "three", 4])
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '列表中第 2 项的类型错误，期望类型: int'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 自定义列表项错误消息正确")

def test_dataclass_with_custom_errors():
    """测试在dataclass中使用自定义错误消息"""
    print("\n=== 测试dataclass中的自定义错误消息 ===")

    @dataclass
    class User(object):
        name = StringField(
            min_length=2,
            max_length=20,
            error_messages={
                'required': '用户名是必填项',
                'min_length': '用户名至少需要 {min_length} 个字符',
                'max_length': '用户名不能超过 {max_length} 个字符'
            }
        )
        age = NumberField(
            minvalue=0,
            maxvalue=120,
            error_messages={
                'minvalue': '年龄不能小于 {minvalue} 岁',
                'maxvalue': '年龄不能大于 {maxvalue} 岁',
                'invalid_type': '年龄必须是数字'
            }
        )
        email = StringField(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            error_messages={
                'required': '邮箱地址是必填项',
                'regex': '请输入有效的邮箱地址格式'
            }
        )

    # 测试用户名长度错误
    try:
        user = User(name="A", age=25, email="test@example.com")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '用户名至少需要 2 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 用户名长度错误消息正确")

    # 测试年龄范围错误
    try:
        user = User(name="Alice", age=150, email="alice@example.com")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '年龄不能大于 120 岁'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 年龄范围错误消息正确")

    # 测试邮箱格式错误
    try:
        user = User(name="Bob", age=30, email="invalid-email")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '请输入有效的邮箱地址格式'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 邮箱格式错误消息正确")

    # 测试成功创建
    try:
        user = User(name="Charlie", age=28, email="charlie@example.com")
        assert user.name == "Charlie", f"期望姓名: 'Charlie', 实际: '{user.name}'"
        assert user.age == 28, f"期望年龄: 28, 实际: {user.age}"
        assert user.email == "charlie@example.com", f"期望邮箱: 'charlie@example.com', 实际: '{user.email}'"
        print("✓ 用户创建成功，所有字段值正确")
    except ValidationError as e:
        assert False, f"用户创建不应该失败: {e.message}"

def test_error_message_inheritance():
    """测试错误消息的继承和覆盖"""
    print("\n=== 测试错误消息继承和覆盖 ===")

    # 基础字段
    base_field = StringField(
        min_length=3,
        error_messages={
            'min_length': '基础字段: 长度至少 {min_length} 个字符'
        }
    )

    # 继承字段（部分覆盖）
    derived_field = StringField(
        min_length=5,
        max_length=10,
        error_messages={
            'min_length': '派生字段: 长度至少 {min_length} 个字符',
            'max_length': '派生字段: 长度最多 {max_length} 个字符'
        }
    )

    # 测试基础字段错误
    try:
        base_field.validate("ab")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '基础字段: 长度至少 3 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 基础字段错误消息正确")

    # 测试派生字段最小长度错误
    try:
        derived_field.validate("abcd")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '派生字段: 长度至少 5 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 派生字段最小长度错误消息正确")

    # 测试派生字段最大长度错误
    try:
        derived_field.validate("abcdefghijk")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '派生字段: 长度最多 10 个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 派生字段最大长度错误消息正确")

def test_complex_error_scenarios():
    """测试复杂的错误场景"""
    print("\n=== 测试复杂错误场景 ===")

    # 测试格式化参数缺失的情况
    field = StringField(
        min_length=5,
        error_messages={
            'min_length': '长度至少 {missing_param} 个字符'  # 故意使用错误的参数名
        }
    )
    try:
        field.validate("abc")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '长度至少 {missing_param} 个字符'  # 格式化失败时返回原始模板
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 格式化参数缺失时返回原始模板")

    # 测试空的自定义错误消息
    field = StringField(
        required=True,
        error_messages={}  # 空字典
    )
    try:
        field.validate(None)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = 'This field is required'  # 应该使用默认消息
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 空错误消息字典时使用默认消息")

    # 测试None作为自定义错误消息
    field = StringField(
        required=True,
        error_messages=None
    )
    try:
        field.validate(None)
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = 'This field is required'  # 应该使用默认消息
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ None错误消息时使用默认消息")

def test_multilingual_error_messages():
    """测试多语言错误消息"""
    print("\n=== 测试多语言错误消息 ===")

    # 中文错误消息
    chinese_field = StringField(
        min_length=2,
        max_length=10,
        regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
        error_messages={
            'required': '此字段为必填项',
            'min_length': '长度不能少于{min_length}个字符',
            'max_length': '长度不能超过{max_length}个字符',
            'regex': '只能包含字母和中文字符',
            'invalid_type': '必须是字符串类型'
        }
    )

    # 英文错误消息
    english_field = StringField(
        min_length=2,
        max_length=10,
        regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
        error_messages={
            'required': 'This field is required',
            'min_length': 'Must be at least {min_length} characters long',
            'max_length': 'Must be at most {max_length} characters long',
            'regex': 'Only letters and Chinese characters are allowed',
            'invalid_type': 'Must be a string'
        }
    )

    # 测试中文最小长度错误
    try:
        chinese_field.validate("a")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '长度不能少于2个字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 中文最小长度错误消息正确")

    # 测试中文正则错误
    try:
        chinese_field.validate("hello123")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = '只能包含字母和中文字符'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 中文正则错误消息正确")

    # 测试英文最小长度错误
    try:
        english_field.validate("a")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = 'Must be at least 2 characters long'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 英文最小长度错误消息正确")

    # 测试英文正则错误
    try:
        english_field.validate("hello123")
        assert False, "应该抛出 ValidationError"
    except ValidationError as e:
        expected = 'Only letters and Chinese characters are allowed'
        assert e.message == expected, f"期望: '{expected}', 实际: '{e.message}'"
        print("✓ 英文正则错误消息正确")

    # 测试成功验证
    try:
        result1 = chinese_field.validate("你好")
        result2 = english_field.validate("Hello")
        assert result1 == "你好", f"期望: '你好', 实际: '{result1}'"
        assert result2 == "Hello", f"期望: 'Hello', 实际: '{result2}'"
        print("✓ 中文和英文字段验证成功")
    except ValidationError as e:
        assert False, f"验证不应该失败: {e.message}"

if __name__ == "__main__":
    test_default_error_messages()
    test_custom_error_messages()
    test_list_field_custom_errors()
    test_dataclass_with_custom_errors()
    test_error_message_inheritance()
    test_complex_error_scenarios()
    test_multilingual_error_messages()
