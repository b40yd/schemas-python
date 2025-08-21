# -*- coding: utf-8 -*-
"""
演示增强版dataclass的新功能
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass

# 1. 使用传统继承方式
@dataclass
class UserProfile(object):
    username = StringField(min_length=3, max_length=20)
    age = NumberField(minvalue=0, maxvalue=150)
    email = StringField()
    
    def validate_email(self, email):
        """自定义邮箱验证"""
        if '@' not in email:
            raise ValidationError("Invalid email format")
    
    def get_username(self):
        """自定义获取用户名的方法，返回大写形式"""
        return self.__dict__.get('username', '').upper()

# 2. 使用装饰器方式
@dataclass
class Product:
    name = StringField(min_length=1, max_length=100)
    price = NumberField(minvalue=0)
    tags = ListField(item_type=StringField())
    
    def get_name(self):
        """自定义获取产品名的方法，添加前缀"""
        name = self.__dict__.get('name', '')
        return f"Product: {name}"
    
    def get_display_price(self):
        """计算显示价格"""
        price = self.__dict__.get('price', 0)
        return f"${price:.2f}"

# 3. 使用装饰器并禁用某些功能
@dataclass(repr=False, eq=False)
class Config:
    debug = StringField(default='false', choices=['true', 'false'])
    timeout = NumberField(default=30, minvalue=1)
    
    def __repr__(self):
        """自定义repr"""
        return f"Config(debug={self.debug}, timeout={self.timeout})"

def demo_enhanced_features():
    print("=== 演示增强版DataClass功能 ===\n")
    
    # 测试传统继承方式
    print("1. 传统继承方式:")
    user = UserProfile(username="alice", age=25, email="alice@example.com")
    print(f"user.username: {user.username}")  # 调用get_username() -> ALICE
    print(f"user['username']: {user['username']}")  # 同样调用get_username() -> ALICE
    print(f"user.to_dict(): {user.to_dict()}")
    print()
    
    # 测试装饰器方式
    print("2. 装饰器方式:")
    product = Product(name="laptop", price=999.99, tags=["electronics", "computer"])
    print(f"product.name: {product.name}")  # 调用get_name() -> Product: laptop
    print(f"product['name']: {product['name']}")  # 同样调用get_name()
    print(f"product.get_display_price(): {product.get_display_price()}")
    print(f"product.to_dict(): {product.to_dict()}")
    print()
    
    # 测试自定义装饰器选项
    print("3. 自定义装饰器选项:")
    config = Config()  # 使用默认值
    print(f"config: {config}")  # 使用自定义__repr__
    print(f"config.debug: {config.debug}")
    print(f"config.timeout: {config.timeout}")
    print()
    
    # 测试Field的get_value方法
    print("4. Field的get_value方法测试:")
    # 直接调用Field的get_value方法
    username_field = UserProfile.username
    print(f"直接调用Field.get_value(): {username_field.get_value(user, 'username')}")
    print()
    
    # 测试验证错误
    print("5. 验证错误测试:")
    try:
        UserProfile(username="ab", age=25, email="invalid-email")  # 用户名太短
    except ValidationError as e:
        print(f"用户名长度验证错误: {e}")
    
    try:
        UserProfile(username="alice", age=25, email="invalid-email")  # 邮箱格式错误
    except ValidationError as e:
        print(f"邮箱格式验证错误: {e}")
    
    try:
        Product(name="", price=-10)  # 名称为空，价格为负
    except ValidationError as e:
        print(f"产品验证错误: {e}")

if __name__ == "__main__":
    demo_enhanced_features()
