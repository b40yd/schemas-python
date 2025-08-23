#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级功能示例

演示 schema_dataclass 的高级功能：
- 自定义验证装饰器
- 自定义 getter 方法
- 嵌套 dataclass
- 复杂验证场景
"""

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


def example_custom_validation():
    """自定义验证示例"""
    print("=== 自定义验证示例 ===\n")

    @dataclass
    class User(object):
        username = StringField(min_length=3, max_length=20)
        password = StringField(min_length=8)
        email = StringField(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        age = NumberField(minvalue=13, maxvalue=120)

        @validate("username")
        def validate_username_format(self, username):
            """用户名只能包含字母、数字和下划线"""
            if not username.replace("_", "").isalnum():
                raise ValidationError("用户名只能包含字母、数字和下划线")

        @validate("username")
        def validate_username_not_reserved(self, username):
            """用户名不能是保留词"""
            reserved_names = ["admin", "root", "system", "user", "test"]
            if username.lower() in reserved_names:
                raise ValidationError(
                    "用户名 '{}' 是保留词，请选择其他用户名".format(username)
                )

        @validate("password")
        def validate_password_strength(self, password):
            """密码强度验证"""
            if not any(c.isupper() for c in password):
                raise ValidationError("密码必须包含至少一个大写字母")
            if not any(c.islower() for c in password):
                raise ValidationError("密码必须包含至少一个小写字母")
            if not any(c.isdigit() for c in password):
                raise ValidationError("密码必须包含至少一个数字")
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                raise ValidationError("密码必须包含至少一个特殊字符")

        @validate("email")
        def validate_email_domain(self, email):
            """邮箱域名验证"""
            blocked_domains = ["tempmail.com", "10minutemail.com", "guerrillamail.com"]
            domain = email.split("@")[1].lower()
            if domain in blocked_domains:
                raise ValidationError("不允许使用 {} 域名的邮箱".format(domain))

    print("1. 测试有效用户:")
    try:
        user = User(
            username="alice123",
            password="SecurePass123!",
            email="alice@example.com",
            age=25,
        )
        print("  ✓ 用户创建成功: {}".format(user.username))
    except ValidationError as e:
        print("  ✗ 用户创建失败: {}".format(e.message))

    print("\n2. 测试各种验证错误:")

    # 用户名格式错误
    try:
        User(
            username="alice@123",
            password="SecurePass123!",
            email="alice@example.com",
            age=25,
        )
    except ValidationError as e:
        print("  ✗ 用户名格式错误: {}".format(e.message))

    # 保留用户名
    try:
        User(
            username="admin",
            password="SecurePass123!",
            email="alice@example.com",
            age=25,
        )
    except ValidationError as e:
        print("  ✗ 保留用户名: {}".format(e.message))

    # 密码强度不足
    try:
        User(
            username="alice123", password="weakpass", email="alice@example.com", age=25
        )
    except ValidationError as e:
        print("  ✗ 密码强度不足: {}".format(e.message))

    # 被阻止的邮箱域名
    try:
        User(
            username="alice123",
            password="SecurePass123!",
            email="alice@tempmail.com",
            age=25,
        )
    except ValidationError as e:
        print("  ✗ 被阻止的邮箱域名: {}".format(e.message))


def example_custom_getters():
    """自定义 getter 方法示例"""
    print("\n=== 自定义 Getter 方法示例 ===\n")

    @dataclass
    class BlogPost(object):
        title = StringField(min_length=1, max_length=200)
        content = StringField(min_length=1)
        status = StringField(
            choices=["draft", "published", "archived"], default="draft"
        )
        view_count = NumberField(minvalue=0, default=0)

        def get_title(self):
            """自定义标题获取方法 - 添加状态前缀"""
            title = self.__dict__.get("title", "")
            status = self.__dict__.get("status", "draft")
            status_prefix = {
                "draft": "[草稿]",
                "published": "[已发布]",
                "archived": "[已归档]",
            }
            return "{} {}".format(status_prefix.get(status, ""), title).strip()

        def get_summary(self):
            """获取内容摘要"""
            content = self.__dict__.get("content", "")
            if len(content) <= 100:
                return content
            return content[:97] + "..."

        def get_popularity(self):
            """根据浏览量计算受欢迎程度"""
            view_count = self.__dict__.get("view_count", 0)
            if view_count >= 1000:
                return "热门"
            elif view_count >= 100:
                return "受欢迎"
            elif view_count >= 10:
                return "一般"
            else:
                return "新文章"

    print("1. 创建博客文章:")
    post = BlogPost(
        title="Python DataClass 使用指南",
        content="这是一篇关于如何使用 Python DataClass 的详细指南。" * 5,  # 长内容
        status="published",
        view_count=150,
    )

    print("  原始标题: {}".format(post.__dict__.get("title")))
    print("  显示标题: {}".format(post.title))  # 使用自定义 getter
    print("  内容摘要: {}".format(post.get_summary()))  # 使用自定义 getter
    print("  受欢迎程度: {}".format(post.get_popularity()))  # 使用自定义 getter

    print("\n2. 修改状态后的效果:")
    post.status = "archived"
    print("  新的显示标题: {}".format(post.title))

    print("\n3. 高浏览量文章:")
    popular_post = BlogPost(
        title="热门文章",
        content="这是一篇热门文章",
        status="published",
        view_count=2500,
    )
    print("  热门文章标题: {}".format(popular_post.title))
    print("  受欢迎程度: {}".format(popular_post.get_popularity()))


def example_nested_dataclass():
    """嵌套 DataClass 示例"""
    print("\n=== 嵌套 DataClass 示例 ===\n")

    @dataclass
    class Address(object):
        street = StringField(min_length=1, max_length=100)
        city = StringField(min_length=1, max_length=50)
        state = StringField(min_length=2, max_length=50)
        zipcode = StringField(regex=r"^\d{6}?$")

        def get_full_address(self):
            """获取完整地址"""
            return "{}, {}, {} {}".format(
                self.street, self.city, self.state, self.zipcode
            )

    @dataclass
    class Person(object):
        first_name = StringField(min_length=1, max_length=50)
        last_name = StringField(min_length=1, max_length=50)
        age = NumberField(minvalue=0, maxvalue=150)
        email = StringField(regex=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        def get_full_name(self):
            """获取全名"""
            return "{} {}".format(self.first_name, self.last_name)

    @dataclass
    class Company(object):
        name = StringField(min_length=1, max_length=100)
        address = Address  # 嵌套 dataclass
        ceo = Person  # 嵌套 dataclass
        employees = ListField(item_type=Person)  # 包含 dataclass 的列表
        founded_year = NumberField(minvalue=1800, maxvalue=2024)

        def get_employee_count(self):
            """获取员工数量"""
            return len(self.employees) if self.employees else 0

        def get_company_info(self):
            """获取公司信息摘要"""
            return "{} (成立于 {}年，员工 {} 人)".format(
                self.name, self.founded_year, self.get_employee_count()
            )

    print("1. 创建复杂的嵌套结构:")
    try:
        company = Company(
            name="科技创新公司",
            address={
                "street": "123 创新大道",
                "city": "深圳",
                "state": "广东",
                "zipcode": "518000",
            },
            ceo={
                "first_name": "张",
                "last_name": "伟",
                "age": 45,
                "email": "zhang.wei@techcompany.com",
            },
            employees=[
                {
                    "first_name": "李",
                    "last_name": "明",
                    "age": 30,
                    "email": "li.ming@techcompany.com",
                },
                {
                    "first_name": "王",
                    "last_name": "芳",
                    "age": 28,
                    "email": "wang.fang@techcompany.com",
                },
            ],
            founded_year=2015,
        )

        print("  ✓ 公司创建成功!")
        print("    公司信息: {}".format(company.get_company_info()))
        print("    公司地址: {}".format(company.address.get_full_address()))
        print("    CEO: {}".format(company.ceo.get_full_name()))
        print("    员工列表:")
        for i, employee in enumerate(company.employees, 1):
            print(
                "      {}. {} ({})".format(i, employee.get_full_name(), employee.email)
            )

    except ValidationError as e:
        print("  ✗ 公司创建失败: {}".format(e.message))

    print("\n2. 测试嵌套验证:")
    try:
        # 无效的邮编格式
        Company(
            name="测试公司",
            address={
                "street": "测试街道",
                "city": "测试城市",
                "state": "测试省",
                "zipcode": "invalid",  # 无效邮编
            },
            ceo={
                "first_name": "测试",
                "last_name": "CEO",
                "age": 40,
                "email": "ceo@test.com",
            },
            employees=[],
            founded_year=2020,
        )
    except ValidationError as e:
        print("  ✗ 邮编验证失败: {}".format(e.message))

    print("\n3. 测试 to_dict() 方法:")
    if "company" in locals():
        company_dict = company.to_dict()
        print("  公司字典结构:")
        print("    名称: {}".format(company_dict["name"]))
        print("    地址类型: {}".format(type(company_dict["address"])))
        print("    CEO类型: {}".format(type(company_dict["ceo"])))
        print("    员工数量: {}".format(len(company_dict["employees"])))
    else:
        print("  公司对象未创建成功，跳过 to_dict() 测试")


def example_conditional_validation():
    """条件验证示例"""
    print("\n=== 条件验证示例 ===\n")

    @dataclass
    class Product(object):
        name = StringField(min_length=1, max_length=100)
        category = StringField(choices=["electronics", "clothing", "books", "food"])
        price = NumberField(minvalue=0.01)
        weight = NumberField(minvalue=0.01, required=True)  # 某些类别需要重量
        isbn = StringField(required=True)  # 书籍需要 ISBN
        size = StringField(required=True)  # 服装需要尺寸

        @validate("weight")
        def validate_weight_for_category(self, weight):
            """某些类别必须提供重量"""
            category = self.__dict__.get("category")
            if category in ["electronics", "food"] and weight is None:
                raise ValidationError("{} 类别的产品必须提供重量".format(category))

        @validate("isbn")
        def validate_isbn_for_books(self, isbn):
            """书籍必须提供 ISBN"""
            category = self.__dict__.get("category")
            if category == "books":
                if not isbn:
                    raise ValidationError("书籍必须提供 ISBN")
                # 简单的 ISBN 格式验证
                if not (
                    isbn.replace("-", "").isdigit()
                    and len(isbn.replace("-", "")) in [10, 13]
                ):
                    raise ValidationError("ISBN 格式不正确")

        @validate("size")
        def validate_size_for_clothing(self, size):
            """服装必须提供尺寸"""
            category = self.__dict__.get("category")
            if category == "clothing":
                if not size:
                    raise ValidationError("服装必须提供尺寸")
                valid_sizes = ["XS", "S", "M", "L", "XL", "XXL"]
                if size not in valid_sizes:
                    raise ValidationError(
                        "尺寸必须是以下之一: {}".format(", ".join(valid_sizes))
                    )

        @validate("price")
        def validate_price_by_category(self, price):
            """不同类别的价格规则"""
            category = self.__dict__.get("category")
            if category == "electronics" and price < 10:
                raise ValidationError("电子产品价格不能低于 $10")
            elif category == "books" and price > 200:
                raise ValidationError("书籍价格不能超过 $200")

    print("1. 测试不同类别的产品:")

    # 电子产品 - 需要重量
    try:
        electronics = Product(
            name="智能手机", category="electronics", price=599.99, weight=0.18, isbn="978-0-123456-78-9", size="M"
        )
        print("  ✓ 电子产品创建成功: {}".format(electronics.name))
    except ValidationError as e:
        print("  ✗ 电子产品创建失败: {}".format(e.message))

    # 书籍 - 需要 ISBN
    try:
        book = Product(
            name="Python 编程指南",
            category="books",
            price=49.99,
            weight=0.18,
            isbn="978-0-123456-78-9",
            size="M"
        )
        print("  ✓ 书籍创建成功: {}".format(book.name))
    except ValidationError as e:
        print("  ✗ 书籍创建失败: {}".format(e.message))

    # 服装 - 需要尺寸
    try:
        clothing = Product(name="T恤", category="clothing", price=29.99, size="M", isbn="978-0-123456-78-9", weight=0.18,)
        print("  ✓ 服装创建成功: {}".format(clothing.name))
    except ValidationError as e:
        print("  ✗ 服装创建失败: {}".format(e.message))

    print("\n2. 测试条件验证错误:")

    # 电子产品缺少重量
    try:
        Product(name="平板电脑", category="electronics", price=299.99, isbn="978-0-123456-78-9", size="M")
    except ValidationError as e:
        print("  ✗ 电子产品缺少重量: {}".format(e.message))

    # 书籍缺少 ISBN
    try:
        Product(name="小说", category="books", price=19.99, weight=0.18, size="M")
    except ValidationError as e:
        print("  ✗ 书籍缺少 ISBN: {}".format(e.message))

    # 服装缺少尺寸
    try:
        Product(name="牛仔裤", category="clothing", price=79.99, weight=0.18, isbn="978-0-123456-78-9")
    except ValidationError as e:
        print("  ✗ 服装缺少尺寸: {}".format(e.message))


if __name__ == "__main__":
    print("Schemas DataClass - 高级功能示例")
    print("=" * 50)

    example_custom_validation()
    example_custom_getters()
    example_nested_dataclass()
    example_conditional_validation()

    print("\n" + "=" * 50)
    print("高级功能示例运行完成！")
    print("\n这些示例展示了 schema_dataclass 的强大功能：")
    print("- 自定义验证逻辑")
    print("- 自定义 getter 方法")
    print("- 嵌套 dataclass 结构")
    print("- 条件验证和跨字段验证")
    print("\n您可以根据这些模式构建复杂的数据验证和处理逻辑。")
