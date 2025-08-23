# -*- coding: utf-8 -*-
"""
pytest 配置文件和共享 fixtures
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from schema_dataclass import (
    StringField,
    NumberField,
    ListField,
    ValidationError,
    dataclass,
    validate,
)


@pytest.fixture
def sample_string_field():
    """创建一个示例 StringField"""
    return StringField(min_length=2, max_length=50, regex=r"^[a-zA-Z][a-zA-Z0-9_]*$")


@pytest.fixture
def sample_number_field():
    """创建一个示例 NumberField"""
    return NumberField(minvalue=0, maxvalue=120)


@pytest.fixture
def sample_list_field():
    """创建一个示例 ListField"""
    return ListField(item_type=str, min_length=1, max_length=5)


@pytest.fixture
def custom_error_messages():
    """自定义错误消息示例"""
    return {
        "required": "这个字段是必填的",
        "min_length": "长度至少需要 {min_length} 个字符",
        "max_length": "长度不能超过 {max_length} 个字符",
        "minvalue": "数值不能小于 {minvalue}",
        "maxvalue": "数值不能大于 {maxvalue}",
        "regex": "格式不正确",
        "choices": "请选择有效的选项: {choices}",
        "invalid_type": "类型必须是 {expected_type}",
        "invalid_list_item": "列表第 {index} 项类型错误，期望 {expected_type}",
    }


@pytest.fixture
def sample_dataclass():
    """创建一个示例 dataclass"""

    @dataclass
    class User(object):
        # 必填字段
        name = StringField(min_length=2, max_length=50, required=True)
        email = StringField(
            regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", required=True
        )
        # 可选字段 (默认 required=False)
        age = NumberField(minvalue=0, maxvalue=120)
        tags = ListField(item_type=str)

    return User


@pytest.fixture
def sample_dataclass_with_custom_errors():
    """创建一个带自定义错误消息的示例 dataclass"""

    @dataclass
    class Product(object):
        name = StringField(
            min_length=1,
            max_length=100,
            error_messages={
                "required": "产品名称不能为空",
                "min_length": "产品名称至少需要 {min_length} 个字符",
                "max_length": "产品名称不能超过 {max_length} 个字符",
            },
        )

        price = NumberField(
            minvalue=0.01,
            error_messages={
                "required": "价格是必填项",
                "minvalue": "价格必须大于 {minvalue} 元",
                "invalid_type": "价格必须是数字",
            },
        )

        category = StringField(
            choices=["电子产品", "服装", "食品", "图书"],
            error_messages={
                "required": "请选择产品类别",
                "choices": "产品类别必须是以下之一: {choices}",
            },
        )

    return Product


# 跳过条件
def pytest_configure(config):
    """pytest 配置"""
    config.addinivalue_line("markers", "skipif_python2: skip if running on Python 2")
    config.addinivalue_line("markers", "skipif_python3: skip if running on Python 3")


def pytest_collection_modifyitems(config, items):
    """修改测试项目"""
    for item in items:
        # 为所有测试添加默认标记
        if "unit" not in item.keywords:
            item.add_marker(pytest.mark.unit)


# Python 版本检查工具
def is_python2():
    """检查是否为 Python 2"""
    return sys.version_info[0] == 2


def is_python3():
    """检查是否为 Python 3"""
    return sys.version_info[0] == 3


# 导出工具函数
pytest.is_python2 = is_python2
pytest.is_python3 = is_python3
