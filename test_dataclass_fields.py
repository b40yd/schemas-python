# -*- coding: utf-8 -*-
"""
测试dataclass字段的重新赋值和嵌套功能
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass, validate

# 定义基础dataclass
@dataclass
class Address(object):
    street = StringField(min_length=1, max_length=100)
    city = StringField(min_length=1, max_length=50)
    zipcode = StringField(regex=r'^\d{5}$')  # 5位数字邮编

@dataclass
class Person(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)
    email = StringField(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @validate("name")
    def validate_name_alpha(self, name):
        if not name.replace(' ', '').isalpha():
            raise ValidationError("Name must contain only letters and spaces")

# 定义包含dataclass字段的复合类
@dataclass
class Company(object):
    name = StringField(min_length=1, max_length=100)
    address = Address  # dataclass字段
    ceo = Person      # dataclass字段
    employees = ListField(item_type=Person)  # 包含dataclass的列表字段

def test_dataclass_field_assignment():
    print("=== 测试dataclass字段的创建和重新赋值 ===\n")
    
    # 1. 创建包含dataclass字段的对象
    print("1. 创建Company对象:")
    try:
        company = Company(
            name="Tech Corp",
            address={
                "street": "123 Main St",
                "city": "San Francisco", 
                "zipcode": "94105"
            },
            ceo={
                "name": "John Doe",
                "age": 45,
                "email": "john@techcorp.com"
            },
            employees=[
                {
                    "name": "Alice Smith",
                    "age": 30,
                    "email": "alice@techcorp.com"
                },
                {
                    "name": "Bob Johnson", 
                    "age": 28,
                    "email": "bob@techcorp.com"
                }
            ]
        )
        
        print("✓ Company创建成功!")
        print("  公司名称:", company.name)
        print("  地址:", company.address.street, company.address.city)
        print("  CEO:", company.ceo.name, "年龄:", company.ceo.age)
        print("  员工数量:", len(company.employees))
        print("  第一个员工:", company.employees[0].name)
        print("  类型检查:")
        print("    type(company.address):", type(company.address).__name__)
        print("    type(company.ceo):", type(company.ceo).__name__)
        print("    type(company.employees[0]):", type(company.employees[0]).__name__)
        
    except ValidationError as e:
        print("✗ Company创建失败:", e)
        return
    
    print("\n2. 测试dataclass字段重新赋值:")
    
    # 2.1 重新赋值address字段
    print("  2.1 重新赋值address字段:")
    try:
        company.address = {
            "street": "456 Oak Ave",
            "city": "Los Angeles",
            "zipcode": "90210"
        }
        print("  ✓ address重新赋值成功!")
        print("    新地址:", company.address.street, company.address.city)
        print("    type(company.address):", type(company.address).__name__)
    except ValidationError as e:
        print("  ✗ address重新赋值失败:", e)
    
    # 2.2 重新赋值ceo字段
    print("  2.2 重新赋值ceo字段:")
    try:
        company.ceo = {
            "name": "Jane Wilson",
            "age": 38,
            "email": "jane@techcorp.com"
        }
        print("  ✓ ceo重新赋值成功!")
        print("    新CEO:", company.ceo.name, "年龄:", company.ceo.age)
        print("    type(company.ceo):", type(company.ceo).__name__)
    except ValidationError as e:
        print("  ✗ ceo重新赋值失败:", e)
    
    print("\n3. 测试重新赋值时的验证:")
    
    # 3.1 测试无效的邮编
    print("  3.1 测试无效邮编:")
    try:
        company.address = {
            "street": "789 Pine St",
            "city": "Seattle",
            "zipcode": "invalid"  # 无效邮编
        }
        print("  ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("  ✓ 正确捕获邮编验证错误:", e)
    
    # 3.2 测试无效的姓名
    print("  3.2 测试无效姓名:")
    try:
        company.ceo = {
            "name": "John123",  # 包含数字，应该失败
            "age": 40,
            "email": "john123@techcorp.com"
        }
        print("  ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("  ✓ 正确捕获姓名验证错误:", e)
    
    # 3.3 测试无效的年龄
    print("  3.3 测试无效年龄:")
    try:
        company.ceo = {
            "name": "John Smith",
            "age": 200,  # 年龄超出范围
            "email": "john@techcorp.com"
        }
        print("  ✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("  ✓ 正确捕获年龄验证错误:", e)
    
    print("\n4. 测试to_dict()方法:")
    company_dict = company.to_dict()
    print("  ✓ to_dict()成功!")
    print("  公司字典结构:")
    for key, value in company_dict.items():
        if isinstance(value, dict):
            print("    {}: {{...}} (嵌套字典)".format(key))
        elif isinstance(value, list):
            print("    {}: [...] (列表，长度: {})".format(key, len(value)))
        else:
            print("    {}: {}".format(key, value))
    
    print("\n5. 测试字段访问方式:")
    print("  通过属性访问 company.ceo.name:", company.ceo.name)
    print("  通过索引访问 company['ceo'].name:", company['ceo'].name)
    print("  通过get方法访问 company.get('ceo').name:", company.get('ceo').name)

def test_nested_dataclass_validation():
    print("\n=== 测试嵌套dataclass的深度验证 ===\n")
    
    # 测试多层嵌套的验证
    print("测试多层嵌套验证:")
    try:
        # 这应该失败，因为员工的邮箱格式错误
        Company(
            name="Bad Corp",
            address={
                "street": "123 Bad St",
                "city": "Bad City",
                "zipcode": "12345"
            },
            ceo={
                "name": "Bad CEO",
                "age": 50,
                "email": "bad-email"  # 无效邮箱
            },
            employees=[]
        )
        print("✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("✓ 正确捕获嵌套验证错误:", e)

if __name__ == "__main__":
    test_dataclass_field_assignment()
    test_nested_dataclass_validation()
