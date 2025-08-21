# Python 2兼容的DataClass库

这是一个专为Python 2设计的dataclass库实现，支持完整的数据校验功能和装饰器语法。

## 特性

### 1. 字段类型支持

- **StringField**: 字符串字段
  - 长度验证 (`min_length`, `max_length`)
  - 正则表达式验证 (`regex`)
  - 枚举验证 (`choices`)
  
- **NumberField**: 数字字段（支持int、float、long）
  - 范围验证 (`minvalue`, `maxvalue`)
  - 枚举验证 (`choices`)
  
- **ListField**: 数组字段
  - 长度验证 (`min_length`, `max_length`)
  - 支持嵌套类型验证 (`item_type`)
  - 支持字符串、数字、dataclass模型嵌套

### 2. 装饰器语法

```python
@dataclass
class User(object):
    name = StringField(min_length=1, max_length=100)
    age = NumberField(minvalue=0, maxvalue=150)
```

### 3. 自定义验证装饰器

```python
@dataclass
class Product(object):
    name = StringField()
    price = NumberField()
    
    @validate("name")
    def validate_name_custom(self, name):
        if not name.isalnum():
            raise ValidationError("Name must be alphanumeric")
    
    @validate("price")
    def validate_price_custom(self, price):
        if price <= 0:
            raise ValidationError("Price must be positive")
```

### 4. 自定义get方法

```python
@dataclass
class BlogPost(object):
    title = StringField()
    status = StringField(default='draft')
    
    def get_title(self):
        """自定义获取标题的方法"""
        title = self.__dict__.get('title', '')
        status = self.__dict__.get('status', 'draft')
        return "[{0}] {1}".format(status.upper(), title)
```

## 使用示例

### 基础用法

```python
from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass, validate

@dataclass
class User(object):
    # 字符串验证：长度 + 正则表达式
    username = StringField(
        min_length=3, 
        max_length=20, 
        regex=r'^[a-zA-Z0-9_]+$'
    )
    
    # 数字验证：范围
    age = NumberField(minvalue=0, maxvalue=150)
    
    # 字符串验证：邮箱格式
    email = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # 枚举验证
    role = StringField(
        choices=['admin', 'user', 'guest'],
        default='user'
    )

# 创建实例
user = User(
    username="john_doe",
    age=25,
    email="john@example.com",
    role="admin"
)

print(user.to_dict())
# 输出: {'username': 'john_doe', 'age': 25, 'email': 'john@example.com', 'role': 'admin'}
```

### 数组类型验证

```python
@dataclass
class Project(object):
    name = StringField(min_length=1)
    
    # 数组包含数字，支持枚举
    priority_levels = ListField(
        item_type=NumberField(choices=[1, 2, 3, 4, 5]),
        min_length=1,
        max_length=5
    )
    
    # 数组包含字符串
    tags = ListField(
        item_type=StringField(min_length=1, max_length=50),
        required=False
    )

project = Project(
    name="Web App",
    priority_levels=[1, 3, 5],
    tags=["web", "javascript"]
)
```

### DataClass字段

```python
@dataclass
class Address(object):
    street = StringField(min_length=1, max_length=100)
    city = StringField(min_length=1, max_length=50)
    zipcode = StringField(regex=r'^\d{5}$')

@dataclass
class Person(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)

@dataclass
class Company(object):
    name = StringField(min_length=1, max_length=100)
    address = Address  # dataclass字段
    ceo = Person      # dataclass字段
    employees = ListField(item_type=Person)  # 包含dataclass的列表

# 创建对象
company = Company(
    name="Tech Corp",
    address={
        "street": "123 Main St",
        "city": "San Francisco",
        "zipcode": "94105"
    },
    ceo={
        "name": "John Doe",
        "age": 45
    },
    employees=[
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 28}
    ]
)

# 重新赋值dataclass字段（会重新创建对象并验证）
company.address = {
    "street": "456 Oak Ave",
    "city": "Los Angeles",
    "zipcode": "90210"
}
```

### 自定义验证

```python
@dataclass
class Product(object):
    name = StringField()
    price = NumberField(minvalue=0)
    category = StringField(choices=['electronics', 'clothing', 'books'])
    
    @validate("name")
    def validate_name_no_special_chars(self, name):
        """产品名称不能包含特殊字符"""
        if not name.replace(' ', '').replace('-', '').isalnum():
            raise ValidationError("Name can only contain letters, numbers, spaces, and hyphens")
    
    @validate("price")
    def validate_price_reasonable(self, price):
        """价格必须合理"""
        if price > 10000:
            raise ValidationError("Price cannot exceed $10,000")
    
    @validate("category")
    def validate_category_rules(self, category):
        """特定类别的规则"""
        if category == 'electronics' and self.__dict__.get('price', 0) < 10:
            raise ValidationError("Electronics must cost at least $10")
```

### 字段访问方式

```python
# 支持多种访问方式
print(user.username)        # 属性访问
print(user['username'])     # 索引访问
print(user.get('username')) # get方法访问

# 自定义get方法
@dataclass
class BlogPost(object):
    title = StringField()
    status = StringField(default='draft')
    
    def get_title(self):
        title = self.__dict__.get('title', '')
        status = self.__dict__.get('status', 'draft')
        return "[{0}] {1}".format(status.upper(), title)

post = BlogPost(title="Hello World")
print(post.title)  # 调用get_title() -> "[DRAFT] Hello World"
```

## 验证特性

### 1. 字符串验证
- 长度验证：`min_length`, `max_length`
- 正则表达式验证：`regex`
- 枚举验证：`choices`

### 2. 数字验证
- 范围验证：`minvalue`, `maxvalue`
- 枚举验证：`choices`
- 类型验证：自动支持int、float、long（Python 2）

### 3. 数组验证
- 长度验证：`min_length`, `max_length`
- 项类型验证：`item_type`
- 支持嵌套：字符串、数字、dataclass模型

### 4. DataClass字段支持
- 支持dataclass作为字段类型
- 自动实例化和验证
- 重新赋值时重新创建对象
- 支持嵌套的to_dict()转换

### 5. 自定义验证
- 使用`@validate("field_name")`装饰器
- 在基础验证之后执行
- 支持多个自定义验证函数

## Python 2/3 兼容性

这个库完全兼容Python 2和Python 3，自动处理：
- 字符串类型差异（str/unicode）
- 数字类型差异（int/long）
- 元类语法差异

## 运行演示

```bash
# 运行完整演示
python demo_complete.py

# 运行应用示例
python app_site_model.py

# 运行dataclass字段测试
python test_dataclass_fields.py
```
