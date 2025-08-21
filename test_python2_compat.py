# -*- coding: utf-8 -*-
"""
Python 2兼容性测试
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass, validate

@dataclass
class SimpleUser(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)
    email = StringField(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @validate("name")
    def validate_name_alpha(self, name):
        if not name.replace(' ', '').isalpha():
            raise ValidationError("Name must contain only letters and spaces")

@dataclass
class UserProfile(object):
    user = SimpleUser  # dataclass字段
    bio = StringField(required=False, max_length=200)

def test_python2_compatibility():
    print("=== Python 2兼容性测试 ===\n")
    
    # 测试基础dataclass创建
    print("1. 测试基础dataclass创建:")
    try:
        user = SimpleUser(
            name="John Doe",
            age=30,
            email="john@example.com"
        )
        print("✓ SimpleUser创建成功!")
        print("  name:", user.name)
        print("  age:", user.age)
        print("  email:", user.email)
    except Exception as e:
        print("✗ SimpleUser创建失败:", e)
        return
    
    # 测试dataclass字段
    print("\n2. 测试dataclass字段:")
    try:
        profile = UserProfile(
            user={
                "name": "Alice Smith",
                "age": 25,
                "email": "alice@example.com"
            },
            bio="Software developer"
        )
        print("✓ UserProfile创建成功!")
        print("  user.name:", profile.user.name)
        print("  user.age:", profile.user.age)
        print("  bio:", profile.bio)
        print("  type(profile.user):", type(profile.user).__name__)
    except Exception as e:
        print("✗ UserProfile创建失败:", e)
        return
    
    # 测试重新赋值
    print("\n3. 测试dataclass字段重新赋值:")
    try:
        profile.user = {
            "name": "Bob Johnson",
            "age": 35,
            "email": "bob@example.com"
        }
        print("✓ 重新赋值成功!")
        print("  新user.name:", profile.user.name)
        print("  新user.age:", profile.user.age)
        print("  type(profile.user):", type(profile.user).__name__)
    except Exception as e:
        print("✗ 重新赋值失败:", e)
    
    # 测试验证
    print("\n4. 测试验证功能:")
    try:
        profile.user = {
            "name": "Invalid123",  # 包含数字，应该失败
            "age": 30,
            "email": "test@example.com"
        }
        print("✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("✓ 正确捕获验证错误:", e)
    except Exception as e:
        print("✗ 意外错误:", e)
    
    # 测试to_dict
    print("\n5. 测试to_dict方法:")
    try:
        result = profile.to_dict()
        print("✓ to_dict成功!")
        print("  结果类型:", type(result).__name__)
        print("  包含字段:", list(result.keys()))
    except Exception as e:
        print("✗ to_dict失败:", e)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_python2_compatibility()
