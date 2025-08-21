# -*- coding: utf-8 -*-
"""
完整演示Python 2兼容的dataclass库，支持数据校验和装饰器功能
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass, validate

# 演示1：基础字段验证
@dataclass
class User(object):
    # 字符串字段：长度验证、正则验证、枚举验证
    username = StringField(
        min_length=3, 
        max_length=20, 
        regex=r'^[a-zA-Z0-9_]+$'  # 只允许字母、数字、下划线
    )
    
    # 数字字段：范围验证、枚举验证
    age = NumberField(
        minvalue=0, 
        maxvalue=150
    )
    
    # 字符串字段：正则验证邮箱格式
    email = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # 字符串字段：枚举验证
    role = StringField(
        choices=['admin', 'user', 'guest'],
        default='user'
    )

# 演示2：数组类型验证
@dataclass
class Project(object):
    name = StringField(min_length=1, max_length=100)
    
    # 数组字段：包含数字类型，支持枚举
    priority_levels = ListField(
        item_type=NumberField(choices=[1, 2, 3, 4, 5]),
        min_length=1,
        max_length=5
    )
    
    # 数组字段：包含字符串类型
    tags = ListField(
        item_type=StringField(min_length=1, max_length=50),
        required=False
    )

# 演示3：使用装饰器自定义验证
@dataclass
class Product(object):
    name = StringField(min_length=1, max_length=100)
    price = NumberField(minvalue=0)
    category = StringField(choices=['electronics', 'clothing', 'books'])
    
    @validate("name")
    def validate_name_no_special_chars(self, name):
        """自定义验证：产品名称不能包含特殊字符"""
        if not name.replace(' ', '').replace('-', '').isalnum():
            raise ValidationError("Product name can only contain letters, numbers, spaces, and hyphens")
    
    @validate("price")
    def validate_price_reasonable(self, price):
        """自定义验证：价格必须合理"""
        if price > 10000:
            raise ValidationError("Price cannot exceed $10,000")
        if price < 0.01:
            raise ValidationError("Price must be at least $0.01")
    
    @validate("category")
    def validate_category_specific_rules(self, category):
        """自定义验证：特定类别的额外规则"""
        if category == 'electronics' and self.__dict__.get('price', 0) < 10:
            raise ValidationError("Electronics must cost at least $10")

# 演示4：嵌套dataclass模型
@dataclass
class Address(object):
    street = StringField(min_length=1, max_length=200)
    city = StringField(min_length=1, max_length=100)
    zipcode = StringField(regex=r'^\d{5}(-\d{4})?$')  # 美国邮编格式

@dataclass
class Company(object):
    name = StringField(min_length=1, max_length=200)
    
    # 嵌套dataclass模型
    addresses = ListField(item_type=Address, min_length=1)
    
    # 员工列表
    employees = ListField(item_type=User, required=False)

# 演示5：自定义get方法
@dataclass
class BlogPost(object):
    title = StringField(min_length=1, max_length=200)
    content = StringField(min_length=10)
    author = StringField(min_length=1, max_length=100)
    status = StringField(choices=['draft', 'published', 'archived'], default='draft')
    
    def get_title(self):
        """自定义获取标题的方法，返回格式化的标题"""
        title = self.__dict__.get('title', '')
        status = self.__dict__.get('status', 'draft')
        return "[{0}] {1}".format(status.upper(), title)
    
    def get_summary(self):
        """获取内容摘要"""
        content = self.__dict__.get('content', '')
        return content[:100] + '...' if len(content) > 100 else content

def demo_all_features():
    print("=== Python 2兼容的DataClass库完整演示 ===\n")
    
    # 1. 基础字段验证
    print("1. 基础字段验证:")
    try:
        user = User(
            username="john_doe",
            age=25,
            email="john@example.com",
            role="admin"
        )
        print("✓ 用户创建成功:", user.to_dict())
    except ValidationError as e:
        print("✗ 验证失败:", e)
    
    # 测试验证失败的情况
    try:
        User(username="jo", age=25, email="john@example.com")  # 用户名太短
    except ValidationError as e:
        print("✗ 用户名长度验证:", e)
    
    try:
        User(username="john_doe", age=25, email="invalid-email")  # 邮箱格式错误
    except ValidationError as e:
        print("✗ 邮箱格式验证:", e)
    
    print()
    
    # 2. 数组类型验证
    print("2. 数组类型验证:")
    try:
        project = Project(
            name="Web App",
            priority_levels=[1, 3, 5],
            tags=["web", "javascript", "react"]
        )
        print("✓ 项目创建成功:", project.to_dict())
    except ValidationError as e:
        print("✗ 验证失败:", e)
    
    try:
        Project(name="Test", priority_levels=[1, 6])  # 优先级超出范围
    except ValidationError as e:
        print("✗ 数组项验证:", e)

    try:
        Project(name="Test", priority_levels=[])  # 数组长度不足
    except ValidationError as e:
        print("✗ 数组长度验证:", e)
    
    print()
    
    # 3. 装饰器自定义验证
    print("3. 装饰器自定义验证:")
    try:
        product = Product(
            name="iPhone 15",
            price=999.99,
            category="electronics"
        )
        print("✓ 产品创建成功:", product.to_dict())
    except ValidationError as e:
        print("✗ 验证失败:", e)
    
    try:
        Product(name="Test@Product", price=50, category="electronics")  # 名称包含特殊字符
    except ValidationError as e:
        print("✗ 自定义名称验证:", e)
    
    try:
        Product(name="Cheap Electronics", price=5, category="electronics")  # 电子产品价格太低
    except ValidationError as e:
        print("✗ 自定义价格验证:", e)
    
    print()
    
    # 4. 自定义get方法
    print("4. 自定义get方法:")
    post = BlogPost(
        title="Python DataClass Tutorial",
        content="This is a comprehensive tutorial about implementing dataclass in Python 2...",
        author="John Doe"
    )
    print("原始标题:", post.__dict__.get('title'))
    print("格式化标题:", post.title)  # 调用get_title()
    print("内容摘要:", post.get_summary())
    print()
    
    # 5. 字段访问方式
    print("5. 字段访问方式:")
    print("通过属性访问 post.title:", post.title)
    print("通过索引访问 post['title']:", post['title'])
    print("使用get方法 post.get('title'):", post.get('title'))
    print()

if __name__ == "__main__":
    demo_all_features()
