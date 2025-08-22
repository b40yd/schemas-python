# -*- coding: utf-8 -*-
"""
自定义错误消息功能的标准单元测试
使用 unittest 框架
"""

import unittest
from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass


class TestDefaultErrorMessages(unittest.TestCase):
    """测试默认错误消息"""
    
    def test_required_field_error(self):
        """测试必填字段错误"""
        field = StringField(required=True)
        with self.assertRaises(ValidationError) as cm:
            field.validate(None)
        self.assertEqual(cm.exception.message, "This field is required")
    
    def test_min_length_error(self):
        """测试最小长度错误"""
        field = StringField(min_length=5)
        with self.assertRaises(ValidationError) as cm:
            field.validate("abc")
        self.assertEqual(cm.exception.message, "Length must be at least 5")
    
    def test_max_length_error(self):
        """测试最大长度错误"""
        field = StringField(max_length=10)
        with self.assertRaises(ValidationError) as cm:
            field.validate("abcdefghijk")
        self.assertEqual(cm.exception.message, "Length must be at most 10")
    
    def test_minvalue_error(self):
        """测试最小值错误"""
        field = NumberField(minvalue=10)
        with self.assertRaises(ValidationError) as cm:
            field.validate(5)
        self.assertEqual(cm.exception.message, "Value must be at least 10")
    
    def test_maxvalue_error(self):
        """测试最大值错误"""
        field = NumberField(maxvalue=100)
        with self.assertRaises(ValidationError) as cm:
            field.validate(150)
        self.assertEqual(cm.exception.message, "Value must be at most 100")
    
    def test_choices_error(self):
        """测试选择项错误"""
        field = StringField(choices=['red', 'green', 'blue'])
        with self.assertRaises(ValidationError) as cm:
            field.validate('yellow')
        self.assertEqual(cm.exception.message, "Value must be one of: ['red', 'green', 'blue']")
    
    def test_regex_error(self):
        """测试正则表达式错误"""
        field = StringField(regex=r'^\d{3}-\d{4}$')
        with self.assertRaises(ValidationError) as cm:
            field.validate('abc-defg')
        self.assertEqual(cm.exception.message, "Value does not match pattern: ^\d{3}-\d{4}$")
    
    def test_invalid_type_error(self):
        """测试类型错误"""
        field = StringField()
        with self.assertRaises(ValidationError) as cm:
            field.validate(123)
        self.assertEqual(cm.exception.message, "Value must be a string")


class TestCustomErrorMessages(unittest.TestCase):
    """测试自定义错误消息"""
    
    def test_custom_required_error(self):
        """测试自定义必填字段错误"""
        field = StringField(
            required=True,
            error_messages={'required': '这个字段是必填的，请提供一个值'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate(None)
        self.assertEqual(cm.exception.message, '这个字段是必填的，请提供一个值')
    
    def test_custom_length_errors(self):
        """测试自定义长度错误"""
        field = StringField(
            min_length=5,
            max_length=10,
            error_messages={
                'min_length': '字符串长度不能少于 {min_length} 个字符',
                'max_length': '字符串长度不能超过 {max_length} 个字符'
            }
        )
        
        # 测试最小长度
        with self.assertRaises(ValidationError) as cm:
            field.validate("abc")
        self.assertEqual(cm.exception.message, '字符串长度不能少于 5 个字符')
        
        # 测试最大长度
        with self.assertRaises(ValidationError) as cm:
            field.validate("abcdefghijk")
        self.assertEqual(cm.exception.message, '字符串长度不能超过 10 个字符')
    
    def test_custom_value_range_errors(self):
        """测试自定义数值范围错误"""
        field = NumberField(
            minvalue=10,
            maxvalue=100,
            error_messages={
                'minvalue': '数值必须大于等于 {minvalue}',
                'maxvalue': '数值必须小于等于 {maxvalue}'
            }
        )
        
        # 测试最小值
        with self.assertRaises(ValidationError) as cm:
            field.validate(5)
        self.assertEqual(cm.exception.message, '数值必须大于等于 10')
        
        # 测试最大值
        with self.assertRaises(ValidationError) as cm:
            field.validate(150)
        self.assertEqual(cm.exception.message, '数值必须小于等于 100')
    
    def test_custom_choices_error(self):
        """测试自定义选择项错误"""
        field = StringField(
            choices=['红色', '绿色', '蓝色'],
            error_messages={'choices': '请选择以下选项之一: {choices}'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate('黄色')
        self.assertEqual(cm.exception.message, "请选择以下选项之一: ['红色', '绿色', '蓝色']")
    
    def test_custom_regex_error(self):
        """测试自定义正则表达式错误"""
        field = StringField(
            regex=r'^\d{3}-\d{4}$',
            error_messages={'regex': '请输入正确的电话号码格式 (例: 123-4567)'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate('abc-defg')
        self.assertEqual(cm.exception.message, '请输入正确的电话号码格式 (例: 123-4567)')
    
    def test_custom_type_error(self):
        """测试自定义类型错误"""
        field = StringField(
            error_messages={'invalid_type': '输入值必须是 {expected_type} 类型'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate(123)
        self.assertEqual(cm.exception.message, '输入值必须是 string 类型')


class TestListFieldCustomErrors(unittest.TestCase):
    """测试列表字段的自定义错误消息"""
    
    def test_custom_list_item_error(self):
        """测试自定义列表项错误"""
        field = ListField(
            item_type=int,
            error_messages={'invalid_list_item': '列表中第 {index} 项的类型错误，期望类型: {expected_type}'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate([1, 2, "three", 4])
        self.assertEqual(cm.exception.message, '列表中第 2 项的类型错误，期望类型: int')


class TestDataclassIntegration(unittest.TestCase):
    """测试与 dataclass 的集成"""
    
    def setUp(self):
        """设置测试用的 dataclass"""
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
        
        self.User = User
    
    def test_name_length_error(self):
        """测试用户名长度错误"""
        with self.assertRaises(ValidationError) as cm:
            self.User(name="A", age=25, email="test@example.com")
        self.assertEqual(cm.exception.message, '用户名至少需要 2 个字符')
    
    def test_age_range_error(self):
        """测试年龄范围错误"""
        with self.assertRaises(ValidationError) as cm:
            self.User(name="Alice", age=150, email="alice@example.com")
        self.assertEqual(cm.exception.message, '年龄不能大于 120 岁')
    
    def test_email_format_error(self):
        """测试邮箱格式错误"""
        with self.assertRaises(ValidationError) as cm:
            self.User(name="Bob", age=30, email="invalid-email")
        self.assertEqual(cm.exception.message, '请输入有效的邮箱地址格式')
    
    def test_successful_creation(self):
        """测试成功创建用户"""
        user = self.User(name="Charlie", age=28, email="charlie@example.com")
        self.assertEqual(user.name, "Charlie")
        self.assertEqual(user.age, 28)
        self.assertEqual(user.email, "charlie@example.com")


class TestComplexScenarios(unittest.TestCase):
    """测试复杂场景"""
    
    def test_format_parameter_missing(self):
        """测试格式化参数缺失"""
        field = StringField(
            min_length=5,
            error_messages={'min_length': '长度至少 {missing_param} 个字符'}
        )
        with self.assertRaises(ValidationError) as cm:
            field.validate("abc")
        # 格式化失败时应该返回原始模板
        self.assertEqual(cm.exception.message, '长度至少 {missing_param} 个字符')
    
    def test_empty_error_messages(self):
        """测试空错误消息字典"""
        field = StringField(required=True, error_messages={})
        with self.assertRaises(ValidationError) as cm:
            field.validate(None)
        # 应该使用默认消息
        self.assertEqual(cm.exception.message, 'This field is required')
    
    def test_none_error_messages(self):
        """测试 None 错误消息"""
        field = StringField(required=True, error_messages=None)
        with self.assertRaises(ValidationError) as cm:
            field.validate(None)
        # 应该使用默认消息
        self.assertEqual(cm.exception.message, 'This field is required')


class TestMultilingualSupport(unittest.TestCase):
    """测试多语言支持"""
    
    def test_chinese_error_messages(self):
        """测试中文错误消息"""
        field = StringField(
            min_length=2,
            regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
            error_messages={
                'min_length': '长度不能少于{min_length}个字符',
                'regex': '只能包含字母和中文字符'
            }
        )
        
        # 测试最小长度错误
        with self.assertRaises(ValidationError) as cm:
            field.validate("a")
        self.assertEqual(cm.exception.message, '长度不能少于2个字符')
        
        # 测试正则错误
        with self.assertRaises(ValidationError) as cm:
            field.validate("hello123")
        self.assertEqual(cm.exception.message, '只能包含字母和中文字符')
    
    def test_english_error_messages(self):
        """测试英文错误消息"""
        field = StringField(
            min_length=2,
            regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
            error_messages={
                'min_length': 'Must be at least {min_length} characters long',
                'regex': 'Only letters and Chinese characters are allowed'
            }
        )
        
        # 测试最小长度错误
        with self.assertRaises(ValidationError) as cm:
            field.validate("a")
        self.assertEqual(cm.exception.message, 'Must be at least 2 characters long')
        
        # 测试正则错误
        with self.assertRaises(ValidationError) as cm:
            field.validate("hello123")
        self.assertEqual(cm.exception.message, 'Only letters and Chinese characters are allowed')
    
    def test_successful_validation(self):
        """测试成功验证"""
        chinese_field = StringField(
            min_length=2,
            regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
            error_messages={'min_length': '长度不能少于{min_length}个字符'}
        )
        
        english_field = StringField(
            min_length=2,
            regex=r'^[a-zA-Z\u4e00-\u9fa5]+$',
            error_messages={'min_length': 'Must be at least {min_length} characters long'}
        )
        
        # 测试成功验证
        result1 = chinese_field.validate("你好")
        result2 = english_field.validate("Hello")
        
        self.assertEqual(result1, "你好")
        self.assertEqual(result2, "Hello")


if __name__ == '__main__':
    unittest.main(verbosity=2)
