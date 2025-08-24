# -*- coding: utf-8 -*-
"""
Schemas DataClass - Python 2 兼容的 DataClass 库

这是一个专为 Python 2 设计的 dataclass 库实现，支持完整的数据校验功能、
装饰器语法和自定义错误消息。

主要特性:
- 完整的字段类型支持 (StringField, NumberField, ListField)
- 自定义错误消息和多语言支持
- Python 2/3 兼容性
- 装饰器语法支持
- 自定义验证和 getter 方法
"""

__version__ = "0.0.2"
__author__ = "Schemas DataClass Team"
__email__ = "bb.qnyd@gmail.com"

# 导入核心组件
from .fields import Field, StringField, NumberField, ListField, ValidationError

from .dataclass import dataclass, validate

# 定义公共 API
__all__ = [
    # 字段类型
    "Field",
    "StringField",
    "NumberField",
    "ListField",
    # 装饰器
    "dataclass",
    "validate",
    # 异常
    "ValidationError",
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
]

# 版本兼容性检查
import sys

if sys.version_info[0] < 2 or (sys.version_info[0] == 2 and sys.version_info[1] < 7):
    raise ImportError("schema_dataclass requires Python 2.7 or higher")


# 显示版本信息
def get_version():
    """获取版本信息"""
    return __version__


def get_info():
    """获取包信息"""
    return {
        "name": "schema_dataclass",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "python_version": "{}.{}.{}".format(*sys.version_info[:3]),
        "description": "Python 2 兼容的 DataClass 库，支持完整的数据校验功能和自定义错误消息",
    }
