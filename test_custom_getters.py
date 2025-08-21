# -*- coding: utf-8 -*-
"""
测试自定义get方法的调用
"""

from fields import StringField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class TestCustomGetters(object):
    """测试自定义get方法"""
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)
    email = StringField(required=False)
    
    def get_name(self):
        """自定义获取name的方法，返回大写形式"""
        name = self.__dict__.get('name', '')
        return name.upper()
    
    def get_age(self):
        """自定义获取age的方法，添加后缀"""
        age = self.__dict__.get('age', 0)
        return "{} years old".format(age)
    
    def get_display_info(self):
        """非字段的自定义方法"""
        name = self.__dict__.get('name', 'Unknown')
        age = self.__dict__.get('age', 0)
        return "{} is {} years old".format(name, age)

def test_custom_getters():
    print("=== 测试自定义get方法调用 ===\n")
    
    # 1. 创建测试对象
    print("1. 创建测试对象:")
    try:
        obj = TestCustomGetters(
            name="john",
            age=25,
            email="john@example.com"
        )
        print("✓ 对象创建成功!")
        print("  原始name值:", obj.__dict__.get('name'))
        print("  原始age值:", obj.__dict__.get('age'))
        
    except Exception as e:
        print("✗ 对象创建失败:", e)
        return
    
    # 2. 测试属性访问调用自定义get方法
    print("\n2. 测试属性访问:")
    print("  obj.name (应该调用get_name()):", obj.name)
    print("  obj.age (应该调用get_age()):", obj.age)
    print("  obj.email (没有get_email，直接返回值):", obj.email)
    
    # 3. 测试索引访问调用自定义get方法
    print("\n3. 测试索引访问:")
    print("  obj['name'] (应该调用get_name()):", obj['name'])
    print("  obj['age'] (应该调用get_age()):", obj['age'])
    print("  obj['email'] (没有get_email，直接返回值):", obj['email'])
    
    # 4. 测试get方法访问
    print("\n4. 测试get方法访问:")
    print("  obj.get('name') (应该调用get_name()):", obj.get('name'))
    print("  obj.get('age') (应该调用get_age()):", obj.get('age'))
    print("  obj.get('email') (没有get_email，直接返回值):", obj.get('email'))
    
    # 5. 测试非字段的自定义方法
    print("\n5. 测试非字段的自定义方法:")
    print("  obj.get_display_info():", obj.get_display_info())
    
    # 6. 测试to_dict方法
    print("\n6. 测试to_dict方法:")
    result = obj.to_dict()
    print("  to_dict结果:", result)
    print("  name字段值 (应该是大写):", result.get('name'))
    print("  age字段值 (应该有后缀):", result.get('age'))
    
    # 7. 测试修改属性后的get方法调用
    print("\n7. 测试修改属性后的get方法调用:")
    obj.name = "alice"
    obj.age = 30
    print("  修改后 obj.name:", obj.name)
    print("  修改后 obj['name']:", obj['name'])
    print("  修改后 obj.age:", obj.age)
    print("  修改后 obj['age']:", obj['age'])
    
    print("\n=== 测试完成 ===")

def test_inheritance():
    print("\n=== 测试继承情况下的get方法 ===\n")
    
    @dataclass
    class BaseClass(object):
        name = StringField()
        
        def get_name(self):
            name = self.__dict__.get('name', '')
            return "Base: {}".format(name.upper())
    
    @dataclass  
    class DerivedClass(BaseClass):
        age = NumberField()
        
        def get_name(self):
            name = self.__dict__.get('name', '')
            return "Derived: {}".format(name.upper())
        
        def get_age(self):
            age = self.__dict__.get('age', 0)
            return "Age: {}".format(age)
    
    try:
        base = BaseClass(name="base")
        derived = DerivedClass(name="derived", age=25)
        
        print("基类对象:")
        print("  base.name:", base.name)
        print("  base['name']:", base['name'])
        
        print("\n派生类对象:")
        print("  derived.name:", derived.name)
        print("  derived['name']:", derived['name'])
        print("  derived.age:", derived.age)
        print("  derived['age']:", derived['age'])
        
        print("✓ 继承测试成功!")
        
    except Exception as e:
        print("✗ 继承测试失败:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_custom_getters()
    test_inheritance()
