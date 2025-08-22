#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实际应用示例

演示 schemas_dataclass 在真实业务场景中的应用：
- 用户管理系统
- 电商产品管理
- 博客系统
- API 数据验证
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schemas_dataclass import StringField, NumberField, ListField, ValidationError, dataclass, validate


def example_user_management_system():
    """用户管理系统示例"""
    print("=== 用户管理系统示例 ===\n")
    
    @dataclass
    class UserProfile(object):
        # 基本信息
        username = StringField(
            min_length=3,
            max_length=20,
            regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
            error_messages={
                'required': '用户名是必填项',
                'min_length': '用户名至少需要 {min_length} 个字符',
                'max_length': '用户名不能超过 {max_length} 个字符',
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
        
        password = StringField(
            min_length=8,
            max_length=128,
            error_messages={
                'required': '密码是必填项',
                'min_length': '密码至少需要 {min_length} 个字符',
                'max_length': '密码不能超过 {max_length} 个字符'
            }
        )
        
        # 个人信息
        first_name = StringField(
            min_length=1,
            max_length=50,
            error_messages={
                'required': '名字是必填项',
                'max_length': '名字不能超过 {max_length} 个字符'
            }
        )
        
        last_name = StringField(
            min_length=1,
            max_length=50,
            error_messages={
                'required': '姓氏是必填项',
                'max_length': '姓氏不能超过 {max_length} 个字符'
            }
        )
        
        age = NumberField(
            minvalue=13,
            maxvalue=120,
            error_messages={
                'required': '年龄是必填项',
                'minvalue': '年龄不能小于 {minvalue} 岁',
                'maxvalue': '年龄不能大于 {maxvalue} 岁'
            }
        )
        
        phone = StringField(
            regex=r'^\+?1?-?\d{3}-?\d{3}-?\d{4}$',
            required=False,
            error_messages={
                'regex': '请输入有效的电话号码格式 (如: 123-456-7890)'
            }
        )
        
        # 系统信息
        role = StringField(
            choices=['user', 'admin', 'moderator'],
            default='user',
            error_messages={
                'choices': '角色必须是: user, admin, 或 moderator'
            }
        )
        
        is_active = StringField(
            choices=['true', 'false'],
            default='true',
            error_messages={
                'choices': '状态必须是: true 或 false'
            }
        )
        
        tags = ListField(
            item_type=str,
            required=False,
            max_length=10,
            error_messages={
                'max_length': '标签数量不能超过 {max_length} 个',
                'invalid_list_item': '第 {index} 个标签必须是字符串'
            }
        )
        
        # 自定义验证
        @validate("username")
        def validate_username_not_reserved(self, username):
            """检查用户名是否为保留词"""
            reserved = ['admin', 'root', 'system', 'api', 'www', 'mail', 'ftp']
            if username.lower() in reserved:
                raise ValidationError(f"用户名 '{username}' 是系统保留词")
        
        @validate("password")
        def validate_password_strength(self, password):
            """密码强度验证"""
            if not any(c.isupper() for c in password):
                raise ValidationError("密码必须包含至少一个大写字母")
            if not any(c.islower() for c in password):
                raise ValidationError("密码必须包含至少一个小写字母")
            if not any(c.isdigit() for c in password):
                raise ValidationError("密码必须包含至少一个数字")
        
        @validate("email")
        def validate_email_domain(self, email):
            """检查邮箱域名"""
            blocked_domains = ['tempmail.com', '10minutemail.com']
            domain = email.split('@')[1].lower()
            if domain in blocked_domains:
                raise ValidationError(f"不允许使用 {domain} 域名")
        
        # 自定义 getter 方法
        def get_full_name(self):
            """获取全名"""
            return f"{self.first_name} {self.last_name}"
        
        def get_display_name(self):
            """获取显示名称"""
            return f"{self.get_full_name()} (@{self.username})"
        
        def get_is_admin(self):
            """检查是否为管理员"""
            return self.role == 'admin'
    
    print("1. 创建用户档案:")
    try:
        user = UserProfile(
            username="alice_dev",
            email="alice@example.com",
            password="SecurePass123",
            first_name="Alice",
            last_name="Johnson",
            age=28,
            phone="123-456-7890",
            role="user",
            tags=["developer", "python", "web"]
        )
        
        print(f"  ✓ 用户创建成功!")
        print(f"    显示名称: {user.get_display_name()}")
        print(f"    邮箱: {user.email}")
        print(f"    角色: {user.role}")
        print(f"    是否管理员: {user.get_is_admin()}")
        print(f"    标签: {user.tags}")
        
    except ValidationError as e:
        print(f"  ✗ 用户创建失败: {e.message}")
    
    print("\n2. 测试各种验证错误:")
    
    # 保留用户名
    try:
        UserProfile(
            username="admin",
            email="test@example.com",
            password="SecurePass123",
            first_name="Test",
            last_name="User",
            age=25
        )
    except ValidationError as e:
        print(f"  ✗ 保留用户名: {e.message}")
    
    # 弱密码
    try:
        UserProfile(
            username="testuser",
            email="test@example.com",
            password="weakpass",
            first_name="Test",
            last_name="User",
            age=25
        )
    except ValidationError as e:
        print(f"  ✗ 弱密码: {e.message}")


def example_ecommerce_product_system():
    """电商产品管理系统示例"""
    print("\n=== 电商产品管理系统示例 ===\n")
    
    @dataclass
    class ProductCategory(object):
        name = StringField(min_length=1, max_length=50)
        description = StringField(required=False, max_length=200)
        parent_id = NumberField(required=False, minvalue=1)
    
    @dataclass
    class ProductImage(object):
        url = StringField(
            regex=r'^https?://.+\.(jpg|jpeg|png|gif|webp)$',
            error_messages={
                'regex': '图片URL必须是有效的HTTP(S)链接，支持jpg、png、gif、webp格式'
            }
        )
        alt_text = StringField(max_length=100, required=False)
        is_primary = StringField(choices=['true', 'false'], default='false')
    
    @dataclass
    class Product(object):
        # 基本信息
        name = StringField(
            min_length=1,
            max_length=200,
            error_messages={
                'required': '产品名称不能为空',
                'max_length': '产品名称不能超过 {max_length} 个字符'
            }
        )
        
        description = StringField(
            min_length=10,
            max_length=2000,
            error_messages={
                'required': '产品描述是必填项',
                'min_length': '产品描述至少需要 {min_length} 个字符',
                'max_length': '产品描述不能超过 {max_length} 个字符'
            }
        )
        
        # 价格信息
        price = NumberField(
            minvalue=0.01,
            error_messages={
                'required': '价格是必填项',
                'minvalue': '价格必须大于 {minvalue} 元'
            }
        )
        
        original_price = NumberField(
            required=False,
            minvalue=0.01,
            error_messages={
                'minvalue': '原价必须大于 {minvalue} 元'
            }
        )
        
        # 库存信息
        stock_quantity = NumberField(
            minvalue=0,
            error_messages={
                'required': '库存数量是必填项',
                'minvalue': '库存数量不能小于 {minvalue}'
            }
        )
        
        # 分类和标签
        category = ProductCategory
        
        tags = ListField(
            item_type=str,
            required=False,
            max_length=20,
            error_messages={
                'max_length': '标签数量不能超过 {max_length} 个'
            }
        )
        
        # 图片
        images = ListField(
            item_type=ProductImage,
            min_length=1,
            max_length=10,
            error_messages={
                'required': '产品必须至少有一张图片',
                'min_length': '产品至少需要 {min_length} 张图片',
                'max_length': '产品图片不能超过 {max_length} 张'
            }
        )
        
        # 产品属性
        sku = StringField(
            regex=r'^[A-Z0-9]{6,12}$',
            error_messages={
                'required': 'SKU是必填项',
                'regex': 'SKU必须是6-12位大写字母和数字组合'
            }
        )
        
        status = StringField(
            choices=['draft', 'active', 'inactive', 'discontinued'],
            default='draft',
            error_messages={
                'choices': '状态必须是: draft, active, inactive, 或 discontinued'
            }
        )
        
        # 自定义验证
        @validate("original_price")
        def validate_original_price_higher(self, original_price):
            """原价必须高于现价"""
            if original_price is not None:
                current_price = self.__dict__.get('price')
                if current_price and original_price <= current_price:
                    raise ValidationError("原价必须高于现价")
        
        @validate("images")
        def validate_primary_image(self, images):
            """确保有且仅有一张主图"""
            if not images:
                return
            
            primary_count = sum(1 for img in images if img.is_primary == 'true')
            if primary_count == 0:
                raise ValidationError("必须设置一张主图")
            elif primary_count > 1:
                raise ValidationError("只能设置一张主图")
        
        # 自定义 getter 方法
        def get_discount_percentage(self):
            """计算折扣百分比"""
            if self.original_price and self.original_price > self.price:
                discount = (self.original_price - self.price) / self.original_price
                return round(discount * 100, 1)
            return 0
        
        def get_is_in_stock(self):
            """检查是否有库存"""
            return self.stock_quantity > 0
        
        def get_primary_image(self):
            """获取主图"""
            for image in self.images:
                if image.is_primary == 'true':
                    return image
            return self.images[0] if self.images else None
    
    print("1. 创建产品:")
    try:
        product = Product(
            name="iPhone 15 Pro",
            description="最新款iPhone，配备A17 Pro芯片，钛金属设计，专业级摄像系统。",
            price=7999.00,
            original_price=8999.00,
            stock_quantity=50,
            category={
                "name": "智能手机",
                "description": "各品牌智能手机"
            },
            tags=["苹果", "智能手机", "5G", "专业摄影"],
            images=[
                {
                    "url": "https://example.com/iphone15pro-1.jpg",
                    "alt_text": "iPhone 15 Pro 正面",
                    "is_primary": "true"
                },
                {
                    "url": "https://example.com/iphone15pro-2.jpg",
                    "alt_text": "iPhone 15 Pro 背面",
                    "is_primary": "false"
                }
            ],
            sku="IPH15PRO001",
            status="active"
        )
        
        print(f"  ✓ 产品创建成功!")
        print(f"    产品名称: {product.name}")
        print(f"    价格: ¥{product.price}")
        print(f"    折扣: {product.get_discount_percentage()}%")
        print(f"    库存状态: {'有货' if product.get_is_in_stock() else '缺货'}")
        print(f"    分类: {product.category.name}")
        print(f"    主图: {product.get_primary_image().url}")
        
    except ValidationError as e:
        print(f"  ✗ 产品创建失败: {e.message}")
    
    print("\n2. 测试验证错误:")
    
    # 原价低于现价
    try:
        Product(
            name="测试产品",
            description="这是一个测试产品的描述",
            price=100.00,
            original_price=80.00,  # 原价低于现价
            stock_quantity=10,
            category={"name": "测试分类"},
            images=[{"url": "https://example.com/test.jpg", "is_primary": "true"}],
            sku="TEST001"
        )
    except ValidationError as e:
        print(f"  ✗ 原价验证错误: {e.message}")


def example_blog_system():
    """博客系统示例"""
    print("\n=== 博客系统示例 ===\n")
    
    @dataclass
    class Author(object):
        name = StringField(min_length=1, max_length=100)
        email = StringField(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        bio = StringField(required=False, max_length=500)
        
        def get_display_name(self):
            return self.name
    
    @dataclass
    class BlogPost(object):
        title = StringField(
            min_length=5,
            max_length=200,
            error_messages={
                'required': '文章标题是必填项',
                'min_length': '标题至少需要 {min_length} 个字符',
                'max_length': '标题不能超过 {max_length} 个字符'
            }
        )
        
        content = StringField(
            min_length=50,
            error_messages={
                'required': '文章内容是必填项',
                'min_length': '文章内容至少需要 {min_length} 个字符'
            }
        )
        
        author = Author
        
        category = StringField(
            choices=['技术', '生活', '旅行', '美食', '读书'],
            error_messages={
                'required': '请选择文章分类',
                'choices': '分类必须是: {choices}'
            }
        )
        
        tags = ListField(
            item_type=str,
            min_length=1,
            max_length=10,
            error_messages={
                'min_length': '至少需要 {min_length} 个标签',
                'max_length': '标签不能超过 {max_length} 个'
            }
        )
        
        status = StringField(
            choices=['draft', 'published', 'archived'],
            default='draft'
        )
        
        view_count = NumberField(minvalue=0, default=0)
        
        # 自定义验证
        @validate("tags")
        def validate_tag_format(self, tags):
            """标签格式验证"""
            for tag in tags:
                if len(tag) < 2 or len(tag) > 20:
                    raise ValidationError("每个标签长度必须在2-20个字符之间")
                if not tag.replace('-', '').replace('_', '').isalnum():
                    raise ValidationError("标签只能包含字母、数字、连字符和下划线")
        
        # 自定义 getter 方法
        def get_word_count(self):
            """获取字数统计"""
            return len(self.content.split())
        
        def get_reading_time(self):
            """估算阅读时间（分钟）"""
            words_per_minute = 200
            return max(1, round(self.get_word_count() / words_per_minute))
        
        def get_summary(self):
            """获取文章摘要"""
            if len(self.content) <= 150:
                return self.content
            return self.content[:147] + '...'
    
    print("1. 创建博客文章:")
    try:
        post = BlogPost(
            title="Python DataClass 完全指南",
            content="在这篇文章中，我们将深入探讨Python DataClass的使用方法和最佳实践。" * 10,
            author={
                "name": "张三",
                "email": "zhangsan@example.com",
                "bio": "Python开发者，专注于Web开发和数据科学"
            },
            category="技术",
            tags=["python", "dataclass", "编程", "教程"],
            status="published",
            view_count=1250
        )
        
        print(f"  ✓ 文章创建成功!")
        print(f"    标题: {post.title}")
        print(f"    作者: {post.author.get_display_name()}")
        print(f"    分类: {post.category}")
        print(f"    标签: {', '.join(post.tags)}")
        print(f"    字数: {post.get_word_count()}")
        print(f"    预计阅读时间: {post.get_reading_time()} 分钟")
        print(f"    摘要: {post.get_summary()}")
        
    except ValidationError as e:
        print(f"  ✗ 文章创建失败: {e.message}")


if __name__ == "__main__":
    print("Schemas DataClass - 实际应用示例")
    print("=" * 60)
    
    example_user_management_system()
    example_ecommerce_product_system()
    example_blog_system()
    
    print("\n" + "=" * 60)
    print("实际应用示例运行完成！")
    print("\n这些示例展示了 schemas_dataclass 在真实业务场景中的应用：")
    print("- 用户管理系统：完整的用户档案验证")
    print("- 电商产品管理：复杂的产品数据结构")
    print("- 博客系统：内容管理和验证")
    print("\n您可以根据这些模式构建自己的业务应用。")
