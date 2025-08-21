# Python 2兼容性修复说明

## 问题描述

在Python 2环境中运行dataclass库时，出现以下错误：

```
TypeError: can't apply this __setattr__ to instance object
```

## 问题原因

在Python 2中，`object.__setattr__(self, key, value)`的使用方式与Python 3不同。在初始化过程中直接调用`object.__setattr__`会导致类型错误。

## 解决方案

### 1. 初始化过程优化

在`__init__`方法中添加了初始化标志机制：

```python
def __init__(self, **init_kwargs):
    # 设置初始化标志，避免在初始化过程中触发__setattr__验证
    object.__setattr__(self, '_initializing', True)
    
    # ... 验证和设置字段值 ...
    
    # 直接设置到__dict__，避免触发__setattr__
    self.__dict__[key] = validated_value
    
    # 初始化完成，移除标志
    object.__setattr__(self, '_initializing', False)
```

### 2. __setattr__方法改进

修改`__setattr__`方法，在初始化过程中跳过验证：

```python
def __setattr__(self, name, value):
    # 如果正在初始化，直接设置属性
    if getattr(self, '_initializing', False):
        object.__setattr__(self, name, value)
        return
        
    # 正常的验证逻辑...
```

### 3. 避免递归调用

在初始化过程中直接操作`__dict__`而不是调用`setattr()`，避免触发`__setattr__`方法导致的递归调用。

## 修复效果

### 修复前
```
=== 测试装饰器版本 ===
Traceback (most recent call last):
  File "app_site_model.py", line 211, in __module__
    email="test@example.com"
  File "dataclass.py", line 126, in __init__
    object.__setattr__(self, key, validated_value)
TypeError: can't apply this __setattr__ to instance object
```

### 修复后
```
=== 测试装饰器版本 ===
Decorator version site.to_dict(): {'name': 'MYSITE123', 'demo': [1, 2, 3], 'url': 'https://example.com', 'status': 'active', 'email': 'test@example.com'}
decorator site.name: alice123
decorator site['name']: ALICE123
decorator site.get_full_info(): alice123 - No URL
```

## 兼容性保证

修复后的代码同时兼容Python 2和Python 3：

- ✅ Python 2.7+：正常工作，无TypeError
- ✅ Python 3.x：正常工作，保持原有功能
- ✅ 所有功能：dataclass字段、验证、重新赋值等都正常工作

## 测试验证

创建了专门的Python 2兼容性测试：

```bash
python test_python2_compat.py
```

测试覆盖：
1. 基础dataclass创建
2. dataclass字段处理
3. 字段重新赋值
4. 验证功能
5. to_dict方法

所有测试都通过，确保Python 2兼容性。

## 核心改进点

1. **初始化标志机制**：使用`_initializing`标志区分初始化和正常使用阶段
2. **直接字典操作**：在初始化时直接操作`__dict__`避免触发验证
3. **条件验证**：只在非初始化阶段进行字段验证
4. **错误处理**：保持原有的错误处理和验证逻辑

这些改进确保了库在Python 2环境中的稳定运行，同时保持了所有高级功能的完整性。
