# 自定义错误消息功能文档

## 概述

本文档介绍了 Python2 兼容的 Field 类型系统中的自定义错误消息功能。该功能允许开发者为字段验证失败时提供自定义的、用户友好的错误消息。

## 功能特性

- ✅ 支持所有验证类型的自定义错误消息
- ✅ 错误消息模板格式化（支持参数替换）
- ✅ 多语言支持
- ✅ 与 dataclass 完美集成
- ✅ Python 2/3 兼容性
- ✅ 向后兼容（不影响现有代码）

## 基础用法

### 1. 创建带有自定义错误消息的字段

```python
from fields import StringField, NumberField, ValidationError

# 基础用法
username_field = StringField(
    min_length=3,
    max_length=20,
    error_messages={
        'required': '用户名是必填项',
        'min_length': '用户名至少需要 {min_length} 个字符',
        'max_length': '用户名不能超过 {max_length} 个字符'
    }
)

# 测试验证
try:
    username_field.validate("ab")  # 太短
except ValidationError as e:
    print(e.message)  # 输出: 用户名至少需要 3 个字符
```

### 2. 支持的错误消息键

每种字段类型支持以下错误消息键：

#### 通用错误消息键
- `required`: 必填字段为空时
- `invalid_type`: 类型不匹配时

#### StringField 特有
- `min_length`: 字符串长度小于最小值时
- `max_length`: 字符串长度大于最大值时
- `regex`: 正则表达式匹配失败时
- `choices`: 值不在允许的选择项中时

#### NumberField 特有
- `minvalue`: 数值小于最小值时
- `maxvalue`: 数值大于最大值时
- `choices`: 值不在允许的选择项中时

#### ListField 特有
- `min_length`: 列表长度小于最小值时
- `max_length`: 列表长度大于最大值时
- `invalid_list_item`: 列表项类型不匹配时

### 3. 错误消息模板格式化

错误消息支持使用 `{参数名}` 格式进行参数替换：

```python
field = NumberField(
    minvalue=18,
    maxvalue=65,
    error_messages={
        'minvalue': '年龄必须满 {minvalue} 周岁',
        'maxvalue': '年龄不能超过 {maxvalue} 周岁'
    }
)

# 验证失败时，{minvalue} 会被替换为实际的最小值 18
```

#### 可用的格式化参数

- `min_length`, `max_length`: 长度限制值
- `minvalue`, `maxvalue`: 数值范围限制值
- `choices`: 允许的选择项列表
- `regex`: 正则表达式模式
- `expected_type`: 期望的类型名称
- `index`: 列表项索引（仅用于 `invalid_list_item`）

## 高级用法

### 1. 在 dataclass 中使用

```python
from dataclass import dataclass
from fields import StringField, NumberField

@dataclass
class User(object):
    name = StringField(
        min_length=2,
        max_length=50,
        error_messages={
            'required': '姓名是必填项',
            'min_length': '姓名至少需要 {min_length} 个字符',
            'max_length': '姓名不能超过 {max_length} 个字符'
        }
    )
    
    age = NumberField(
        minvalue=0,
        maxvalue=120,
        error_messages={
            'minvalue': '年龄不能小于 {minvalue} 岁',
            'maxvalue': '年龄不能大于 {maxvalue} 岁'
        }
    )

# 使用
try:
    user = User(name="A", age=25)  # 姓名太短
except ValidationError as e:
    print(e.message)  # 输出: 姓名至少需要 2 个字符
```

### 2. 多语言支持

```python
# 中文错误消息
chinese_field = StringField(
    required=True,
    min_length=2,
    error_messages={
        'required': '此字段为必填项',
        'min_length': '长度不能少于{min_length}个字符'
    }
)

# 英文错误消息
english_field = StringField(
    required=True,
    min_length=2,
    error_messages={
        'required': 'This field is required',
        'min_length': 'Must be at least {min_length} characters long'
    }
)
```

### 3. 复杂验证场景

```python
# 邮箱验证
email_field = StringField(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    error_messages={
        'required': '邮箱地址是必填项',
        'regex': '请输入有效的邮箱地址格式 (例: user@example.com)',
        'invalid_type': '邮箱地址必须是字符串类型'
    }
)

# 列表字段验证
tags_field = ListField(
    item_type=str,
    min_length=1,
    max_length=5,
    error_messages={
        'min_length': '至少需要 {min_length} 个标签',
        'max_length': '最多只能有 {max_length} 个标签',
        'invalid_list_item': '第 {index} 个标签必须是字符串类型'
    }
)
```

## 默认错误消息

如果没有提供自定义错误消息，系统会使用以下默认消息：

- `required`: "This field is required"
- `min_length`: "Length must be at least {min_length}"
- `max_length`: "Length must be at most {max_length}"
- `minvalue`: "Value must be at least {minvalue}"
- `maxvalue`: "Value must be at most {maxvalue}"
- `choices`: "Value must be one of: {choices}"
- `regex`: "Value does not match pattern: {regex}"
- `invalid_type`: "Value must be a {expected_type}"
- `invalid_list_item`: "Item at index {index} has invalid type, expected {expected_type}"

## 错误处理

### 格式化失败处理

如果错误消息模板中的参数名不存在，系统会返回原始模板而不是抛出异常：

```python
field = StringField(
    min_length=5,
    error_messages={
        'min_length': '长度至少 {wrong_param} 个字符'  # 错误的参数名
    }
)

# 验证失败时会返回: "长度至少 {wrong_param} 个字符"
```

### 空错误消息处理

如果 `error_messages` 参数为 `None` 或空字典，系统会使用默认错误消息。

## 最佳实践

1. **保持消息简洁明了**: 错误消息应该清楚地说明问题和解决方案
2. **使用用户友好的语言**: 避免技术术语，使用用户容易理解的表达
3. **提供具体的指导**: 告诉用户期望的格式或范围
4. **考虑国际化**: 为不同语言环境准备相应的错误消息
5. **测试错误消息**: 确保所有错误情况都有适当的消息

## 测试文件

项目包含完整的测试套件：

### 1. 断言方式测试
- **文件**: `test_custom_error_messages.py`
- **描述**: 使用断言方式的完整测试用例
- **包含**: 默认消息、自定义消息、多语言、复杂场景等测试

### 2. 标准单元测试
- **文件**: `test_custom_error_messages_unittest.py`
- **描述**: 使用 Python unittest 框架的标准单元测试
- **包含**: 25 个测试用例，覆盖所有功能点

### 3. 功能演示
- **文件**: `demo_custom_error_messages.py`
- **描述**: 完整的功能演示和使用示例
- **包含**: 基础用法、dataclass 集成、多语言支持、高级功能

### 4. 兼容性测试
- **文件**: `test_dataclass_fields.py`
- **描述**: 验证新功能不影响现有功能
- **包含**: 现有 dataclass 字段功能的完整测试

### 5. 测试运行器
- **文件**: `run_custom_error_tests.py`
- **描述**: 一键运行所有相关测试的脚本
- **功能**: 自动运行所有测试并生成总结报告

## 运行测试

### 运行所有测试
```bash
python3 run_custom_error_tests.py
```

### 运行单个测试文件
```bash
# 断言方式测试
python3 test_custom_error_messages.py

# 标准单元测试
python3 test_custom_error_messages_unittest.py

# 功能演示
python3 demo_custom_error_messages.py

# 兼容性测试
python3 test_dataclass_fields.py
```

## 测试覆盖率

测试套件包含 **25+ 个测试用例**，覆盖：

- ✅ 所有字段类型的默认错误消息
- ✅ 所有字段类型的自定义错误消息
- ✅ 错误消息模板格式化功能
- ✅ 格式化参数缺失的边界情况
- ✅ 空/None 错误消息的处理
- ✅ 多语言错误消息支持
- ✅ dataclass 集成功能
- ✅ 列表字段的复杂验证
- ✅ 向后兼容性验证

## Python 2 兼容性

该功能完全兼容 Python 2.7，使用了以下兼容性技术：
- 使用 `format()` 方法而不是 f-strings
- 兼容 Python 2 的字符串类型检查
- 使用 `__future__` 导入确保兼容性
- 兼容 Python 2 的异常处理语法

## 性能影响

- **零性能影响**: 不使用自定义错误消息时，性能与原版本完全相同
- **最小开销**: 使用自定义错误消息时，仅增加字符串格式化的微小开销
- **内存友好**: 错误消息模板仅在字段初始化时创建一次
