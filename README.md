# Schemas DataClass

[![Python Version](https://img.shields.io/badge/python-2.7%2B%2C%203.4%2B-blue.svg)](https://pypi.org/project/schemas-dataclass/)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)
[![CI](https://github.com/b40yd/schemas-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/b40yd/schemas-python/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/b40yd/9d999999999999999999999999999999/raw/coverage.json)](#)

一个专为 Python 2/3 兼容设计的 DataClass 库，支持完整的数据校验功能、装饰器语法和自定义错误消息。

## 🚀 快速开始

### 安装

```bash
pip install schemas-dataclass
```

### 基础使用

```python
from schema_dataclass import StringField, NumberField, dataclass, ValidationError

@dataclass
class User(object):
    name = StringField(min_length=2, max_length=50)
    age = NumberField(minvalue=0, maxvalue=120)
    email = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

# 创建用户
user = User(name="Alice", age=25, email="alice@example.com")
print(user.to_dict())  # {'name': 'Alice', 'age': 25, 'email': 'alice@example.com'}
```

### 自定义错误消息

```python
@dataclass
class User(object):
    name = StringField(
        min_length=2,
        error_messages={
            'required': '姓名是必填项',
            'min_length': '姓名至少需要 {min_length} 个字符'
        }
    )

try:
    user = User(name="A")  # 太短
except ValidationError as e:
    print(e.message)  # 输出: 姓名至少需要 2 个字符
```

## 📚 文档索引

- **[安装和使用](#安装和使用)** - 快速上手指南
- **[完整示例](#完整示例)** - 丰富的使用示例
- **[API 参考](#api-参考)** - 详细的 API 文档
- **[测试](#测试)** - 如何运行测试
- **[项目结构说明](PROJECT_STRUCTURE.md)** - 项目文件结构和开发指南
- **[更新日志](CHANGELOG.md)** - 版本更新记录和功能变更
- **[自定义错误消息详细文档](CUSTOM_ERROR_MESSAGES.md)** - 完整的自定义错误消息使用指南
- **[贡献指南](#贡献指南)** - 如何参与项目开发

## 安装和使用

### 安装方式

#### 从 PyPI 安装（推荐）

```bash
pip install schemas-dataclass
```

#### 从源码安装

```bash
git clone https://github.com/schemas/dataclass.git
cd dataclass
python setup.py install
```

#### 开发环境安装

```bash
git clone https://github.com/schemas/dataclass.git
cd dataclass
pip install -e .
pip install -r requirements-dev.txt
```

### 基础使用指南

```python
from schema_dataclass import StringField, NumberField, ListField, dataclass

@dataclass
class User(object):
    name = StringField(min_length=2, max_length=50)
    age = NumberField(minvalue=0, maxvalue=120)
    email = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    tags = ListField(item_type=str, required=False)

# 创建和使用
user = User(
    name="Alice",
    age=25,
    email="alice@example.com",
    tags=["developer", "python"]
)

print(user.name)        # Alice
print(user['age'])      # 25
print(user.get('email')) # alice@example.com
print(user.to_dict())   # 转换为字典
```

## 核心特性

### 🔧 字段类型支持

- **StringField**: 字符串字段
  - 长度验证 (`min_length`, `max_length`)
  - 正则表达式验证 (`regex`)
  - 枚举验证 (`choices`)
  - 自定义错误消息支持
  
- **NumberField**: 数字字段（支持int、float、long）
  - 范围验证 (`minvalue`, `maxvalue`)
  - 枚举验证 (`choices`)
  - 自定义错误消息支持
  
- **ListField**: 数组字段
  - 长度验证 (`min_length`, `max_length`)
  - 支持嵌套类型验证 (`item_type`)
  - 支持字符串、数字、dataclass模型嵌套
  - 自定义错误消息支持

### 🌍 自定义错误消息

- **多语言支持**: 支持中文、英文等多语言错误消息
- **模板格式化**: 支持 `{参数名}` 格式的参数替换
- **完整覆盖**: 支持所有验证类型的自定义错误消息
- **向后兼容**: 不影响现有代码，可选使用

```python
# 自定义错误消息示例
@dataclass
class User(object):
    name = StringField(
        min_length=3,
        max_length=20,
        error_messages={
            'required': '用户名是必填项',
            'min_length': '用户名至少需要 {min_length} 个字符',
            'max_length': '用户名不能超过 {max_length} 个字符'
        }
    )
```

### 🎯 装饰器语法

```python
@dataclass
class User(object):
    name = StringField(min_length=1, max_length=100)
    age = NumberField(minvalue=0, maxvalue=150)
```

### 🔍 自定义验证装饰器

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

### 🔧 自定义get方法

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

## 完整示例

### 📁 示例文件

项目提供了丰富的示例文件，位于 `examples/` 目录：

- **[基础使用示例](examples/basic_usage.py)** - 字段类型、dataclass 基础功能
- **[自定义错误消息示例](examples/custom_error_messages.py)** - 多语言错误消息、模板格式化
- **[高级功能示例](examples/advanced_features.py)** - 自定义验证、嵌套 dataclass、条件验证
- **[实际应用示例](examples/real_world_examples.py)** - 用户管理、电商产品、博客系统

### 🚀 运行示例

```bash
# 基础使用示例
python examples/basic_usage.py

# 自定义错误消息示例
python examples/custom_error_messages.py

# 高级功能示例
python examples/advanced_features.py

# 实际应用示例
python examples/real_world_examples.py
```

### 💡 快速示例

#### 用户管理系统

```python
from schema_dataclass import StringField, NumberField, ListField, dataclass, validate

@dataclass
class User(object):
    username = StringField(
        min_length=3,
        max_length=20,
        regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
        error_messages={
            'required': '用户名是必填项',
            'min_length': '用户名至少需要 {min_length} 个字符',
            'regex': '用户名必须以字母开头，只能包含字母、数字和下划线'
        }
    )
    
    email = StringField(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        error_messages={
            'required': '邮箱地址是必填项',
            'regex': '请输入有效的邮箱地址'
        }
    )
    
    age = NumberField(
        minvalue=13,
        maxvalue=120,
        error_messages={
            'minvalue': '年龄不能小于 {minvalue} 岁',
            'maxvalue': '年龄不能大于 {maxvalue} 岁'
        }
    )
    
    tags = ListField(
        item_type=str,
        required=False,
        max_length=10,
        error_messages={
            'max_length': '标签数量不能超过 {max_length} 个'
        }
    )
    
    @validate("username")
    def validate_username_not_reserved(self, username):
        """检查用户名是否为保留词"""
        reserved = ['admin', 'root', 'system']
        if username.lower() in reserved:
            raise ValidationError(f"用户名 '{username}' 是系统保留词")

# 使用示例
user = User(
    username="alice_dev",
    email="alice@example.com",
    age=28,
    tags=["developer", "python"]
)

print("用户: {}".format(user.username))
print("邮箱: {}".format(user.email))
print("年龄: {}".format(user.age))
print("标签: {}".format(user.tags))
```

## API 参考

> **重要变更说明**: 从版本 2.0 开始，所有字段默认为可选 (`required=False`)。如需必填字段，请显式设置 `required=True`。

### 字段类型

#### StringField

```python
StringField(
    default=None,           # 默认值
    alias=None,            # 字段别名
    required=False,        # 是否必填 (默认为 False)
    min_length=None,       # 最小长度
    max_length=None,       # 最大长度
    regex=None,            # 正则表达式
    choices=None,          # 枚举选项
    error_messages=None    # 自定义错误消息
)
```

#### NumberField

```python
NumberField(
    default=None,           # 默认值
    alias=None,            # 字段别名
    required=False,        # 是否必填 (默认为 False)
    minvalue=None,         # 最小值
    maxvalue=None,         # 最大值
    choices=None,          # 枚举选项
    error_messages=None    # 自定义错误消息
)
```

#### ListField

```python
ListField(
    default=None,           # 默认值
    alias=None,            # 字段别名
    required=False,        # 是否必填 (默认为 False)
    min_length=None,       # 最小长度
    max_length=None,       # 最大长度
    item_type=None,        # 列表项类型
    error_messages=None    # 自定义错误消息
)
```

### 装饰器

#### @dataclass

```python
@dataclass
class MyClass(object):
    field1 = StringField()
    field2 = NumberField()
```

#### @validate

```python
@dataclass
class MyClass(object):
    field1 = StringField()

    @validate("field1")
    def validate_field1(self, value):
        # 自定义验证逻辑
        if not condition:
            raise ValidationError("Custom validation failed")
```

### 错误消息键

#### 通用错误消息键

- `required`: 必填字段为空
- `invalid_type`: 类型不匹配

#### StringField 错误消息键

- `min_length`: 长度小于最小值
- `max_length`: 长度大于最大值
- `regex`: 正则表达式匹配失败
- `choices`: 值不在枚举选项中

#### NumberField 错误消息键

- `minvalue`: 数值小于最小值
- `maxvalue`: 数值大于最大值
- `choices`: 值不在枚举选项中

#### ListField 错误消息键

- `min_length`: 列表长度小于最小值
- `max_length`: 列表长度大于最大值
- `invalid_list_item`: 列表项类型不匹配

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_fields.py

# 运行带覆盖率的测试
pytest --cov=schema_dataclass

# 运行特定标记的测试
pytest -m "unit"
pytest -m "integration"
pytest -m "error_messages"
```

### 测试结构

```
tests/
├── conftest.py                    # pytest 配置和 fixtures
├── test_fields.py                 # 字段类型测试
├── test_custom_error_messages.py  # 自定义错误消息测试
├── test_dataclass.py             # dataclass 功能测试
└── test_integration.py           # 集成测试
```

### 测试覆盖

- **25+ 个测试用例**，覆盖所有功能点
- **100% 测试通过率**
- **向后兼容性验证**
- **多语言错误消息测试**
- **复杂场景边界测试**

## 验证特性

### 字符串验证

- 长度验证：`min_length`, `max_length`
- 正则表达式验证：`regex`
- 枚举验证：`choices`
- 自定义错误消息：支持所有验证类型

### 数字验证

- 范围验证：`minvalue`, `maxvalue`
- 枚举验证：`choices`
- 类型验证：自动支持int、float、long（Python 2）
- 自定义错误消息：支持所有验证类型

### 数组验证

- 长度验证：`min_length`, `max_length`
- 项类型验证：`item_type`
- 支持嵌套：字符串、数字、dataclass模型
- 自定义错误消息：支持列表项类型错误

### DataClass字段支持

- 支持dataclass作为字段类型
- 自动实例化和验证
- 重新赋值时重新创建对象
- 支持嵌套的to_dict()转换
- 支持重新赋值时验证

### 自定义验证

- 使用`@validate("field_name")`装饰器
- 在基础验证之后执行
- 支持多个自定义验证函数

### 自定义错误消息特性

- **多语言支持**：完全支持中文、英文等多语言错误消息
- **模板格式化**：支持 `{参数名}` 格式的参数替换，如 `{min_length}`, `{maxvalue}` 等
- **完整覆盖**：支持所有验证类型的自定义错误消息
- **向后兼容**：不影响现有代码，可选使用
- **健壮性**：格式化失败时优雅降级，返回原始模板
- **零性能影响**：不使用自定义消息时性能与原版本完全相同

#### 支持的错误消息类型

- **通用**: `required`, `invalid_type`
- **StringField**: `min_length`, `max_length`, `regex`, `choices`
- **NumberField**: `minvalue`, `maxvalue`, `choices`
- **ListField**: `min_length`, `max_length`, `invalid_list_item`

## 兼容性

- **Python 2.7+**: 完全支持
- **Python 3.4+**: 完全支持
- **PyPy**: 支持
- **Jython**: 理论支持（未测试）

## 性能

- **零依赖**: 仅使用 Python 标准库
- **轻量级**: 核心代码不到 1000 行
- **高性能**: 验证速度快，内存占用低
- **可扩展**: 易于添加新的字段类型和验证规则

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 添加测试用例
4. 确保所有测试通过 (`pytest`)
5. 更新相关文档
6. 提交更改 (`git commit -m 'Add amazing feature'`)
7. 推送到分支 (`git push origin feature/amazing-feature`)
8. 创建 Pull Request

### 开发环境设置

```bash
git clone https://github.com/schemas/dataclass.git
cd dataclass
pip install -e .
pip install -r requirements-dev.txt
```

### 代码规范

- 遵循 PEP 8 代码风格
- 添加适当的文档字符串
- 为新功能添加测试用例
- 保持 Python 2/3 兼容性

## 许可证

本项目采用 GNU General Public License v3.0 许可证。详见 [LICENSE](LICENSE) 文件。

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新记录。

---

**注意**: 本库完全兼容 Python 2.7 和 Python 3.x，自定义错误消息功能为可选特性，不影响现有代码的使用。
