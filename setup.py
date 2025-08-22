# -*- coding: utf-8 -*-
"""
Setup script for schemas_dataclass package
"""

from setuptools import setup, find_packages
import os
import sys

# 读取版本信息
def get_version():
    """从 __init__.py 中读取版本信息"""
    version_file = os.path.join(os.path.dirname(__file__), 'schemas_dataclass', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip("'\"")
    return '0.0.0'

# 读取 README
def get_long_description():
    """读取 README.md 作为长描述"""
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# 读取依赖
def get_requirements():
    """读取依赖列表"""
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='schemas_dataclass',
    version=get_version(),
    author='Schemas DataClass Team',
    author_email='support@schemas-dataclass.com',
    description='Python 2 兼容的 DataClass 库，支持完整的数据校验功能和自定义错误消息',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/schemas/dataclass',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=3.0.0',
            'pytest-cov',
            'pytest-mock',
            'flake8',
            'black; python_version>="3.6"',
        ],
        'test': [
            'pytest>=3.0.0',
            'pytest-cov',
            'pytest-mock',
        ]
    },
    keywords='dataclass validation python2 python3 schema fields',
    project_urls={
        'Bug Reports': 'https://github.com/schemas/dataclass/issues',
        'Source': 'https://github.com/schemas/dataclass',
        'Documentation': 'https://github.com/schemas/dataclass/blob/main/README.md',
    },
    include_package_data=True,
    zip_safe=False,
)
