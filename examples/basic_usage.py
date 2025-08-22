#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础使用示例

演示 schemas_dataclass 的基本功能：
- 字段类型定义
- 基础验证
- dataclass 装饰器使用
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schemas_dataclass import StringField, NumberField, ListField, ValidationError, dataclass


def example_basic_fields():
    """基础字段使用示例"""
    print("=== 基础字段使用示例 ===\n")
    
    # 1. StringField 示例
    print("1. StringField 示例:")
    name_field = StringField(min_length=2, max_length=50)
    
    try:
        result = name_field.validate("Alice")
        print(f"  ✓ 有效姓名: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        name_field.validate("A")  # 太短
    except ValidationError as e:
        print(f"  ✗ 姓名太短: {e.message}")
    
    # 2. NumberField 示例
    print("\n2. NumberField 示例:")
    age_field = NumberField(minvalue=0, maxvalue=120)
    
    try:
        result = age_field.validate(25)
        print(f"  ✓ 有效年龄: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        age_field.validate(150)  # 太大
    except ValidationError as e:
        print(f"  ✗ 年龄超出范围: {e.message}")
    
    # 3. ListField 示例
    print("\n3. ListField 示例:")
    tags_field = ListField(item_type=str, min_length=1, max_length=5)
    
    try:
        result = tags_field.validate(["python", "programming"])
        print(f"  ✓ 有效标签: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        tags_field.validate([])  # 太短
    except ValidationError as e:
        print(f"  ✗ 标签列表为空: {e.message}")


def example_dataclass_basic():
    """基础 dataclass 示例"""
    print("\n=== 基础 DataClass 示例 ===\n")
    
    @dataclass
    class User(object):
        name = StringField(min_length=2, max_length=50)
        age = NumberField(minvalue=0, maxvalue=120)
        email = StringField(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        tags = ListField(item_type=str, required=False)
    
    print("1. 创建有效用户:")
    try:
        user = User(
            name="Alice Smith",
            age=28,
            email="alice@example.com",
            tags=["developer", "python"]
        )
        print(f"  ✓ 用户创建成功!")
        print(f"    姓名: {user.name}")
        print(f"    年龄: {user.age}")
        print(f"    邮箱: {user.email}")
        print(f"    标签: {user.tags}")
    except ValidationError as e:
        print(f"  ✗ 用户创建失败: {e.message}")
    
    print("\n2. 测试验证错误:")
    try:
        User(name="A", age=28, email="alice@example.com")  # 姓名太短
    except ValidationError as e:
        print(f"  ✗ 姓名验证失败: {e.message}")
    
    try:
        User(name="Bob", age=150, email="bob@example.com")  # 年龄超出范围
    except ValidationError as e:
        print(f"  ✗ 年龄验证失败: {e.message}")
    
    try:
        User(name="Charlie", age=30, email="invalid-email")  # 邮箱格式错误
    except ValidationError as e:
        print(f"  ✗ 邮箱验证失败: {e.message}")
    
    print("\n3. 字段访问方式:")
    user = User(name="David", age=35, email="david@example.com")
    
    print(f"  属性访问: user.name = {user.name}")
    print(f"  索引访问: user['name'] = {user['name']}")
    print(f"  get方法访问: user.get('name') = {user.get('name')}")
    print(f"  get方法默认值: user.get('nonexistent', 'default') = {user.get('nonexistent', 'default')}")
    
    print("\n4. to_dict() 方法:")
    user_dict = user.to_dict()
    print(f"  用户字典: {user_dict}")


def example_advanced_validation():
    """高级验证示例"""
    print("\n=== 高级验证示例 ===\n")
    
    # 1. 正则表达式验证
    print("1. 正则表达式验证:")
    phone_field = StringField(
        regex=r'^\d{3}-\d{3}-\d{4}$',
        error_messages={'regex': '电话号码格式应为: XXX-XXX-XXXX'}
    )
    
    try:
        result = phone_field.validate("123-456-7890")
        print(f"  ✓ 有效电话: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        phone_field.validate("1234567890")  # 格式错误
    except ValidationError as e:
        print(f"  ✗ 格式错误: {e.message}")
    
    # 2. 选择项验证
    print("\n2. 选择项验证:")
    status_field = StringField(
        choices=['draft', 'published', 'archived'],
        error_messages={'choices': '状态必须是: draft, published, 或 archived'}
    )
    
    try:
        result = status_field.validate("published")
        print(f"  ✓ 有效状态: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        status_field.validate("invalid")  # 无效选择
    except ValidationError as e:
        print(f"  ✗ 无效状态: {e.message}")
    
    # 3. 嵌套列表验证
    print("\n3. 嵌套列表验证:")
    scores_field = ListField(
        item_type=NumberField(minvalue=0, maxvalue=100),
        min_length=1,
        max_length=10
    )
    
    try:
        result = scores_field.validate([85, 92, 78, 96])
        print(f"  ✓ 有效分数: {result}")
    except ValidationError as e:
        print(f"  ✗ 验证失败: {e.message}")
    
    try:
        scores_field.validate([85, 150, 78])  # 150 超出范围
    except ValidationError as e:
        print(f"  ✗ 分数超出范围: {e.message}")


def example_optional_fields():
    """可选字段示例"""
    print("\n=== 可选字段示例 ===\n")
    
    @dataclass
    class Product(object):
        name = StringField(min_length=1, max_length=100)
        price = NumberField(minvalue=0.01)
        description = StringField(required=False, default="No description")
        tags = ListField(item_type=str, required=False, default=lambda: [])
        category = StringField(required=False)
    
    print("1. 只提供必填字段:")
    product1 = Product(name="Basic Product", price=19.99)
    print(f"  产品名称: {product1.name}")
    print(f"  价格: ${product1.price}")
    print(f"  描述: {product1.description}")  # 使用默认值
    print(f"  标签: {product1.tags}")  # 使用默认值
    print(f"  类别: {product1.category}")  # None
    
    print("\n2. 提供所有字段:")
    product2 = Product(
        name="Premium Product",
        price=99.99,
        description="High-quality premium product",
        tags=["premium", "quality"],
        category="electronics"
    )
    print(f"  产品名称: {product2.name}")
    print(f"  价格: ${product2.price}")
    print(f"  描述: {product2.description}")
    print(f"  标签: {product2.tags}")
    print(f"  类别: {product2.category}")


if __name__ == "__main__":
    print("Schemas DataClass - 基础使用示例")
    print("=" * 50)
    
    example_basic_fields()
    example_dataclass_basic()
    example_advanced_validation()
    example_optional_fields()
    
    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("\n更多示例请查看 examples/ 目录下的其他文件。")
