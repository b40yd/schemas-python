# -*- coding: utf-8 -*-
import abc
import inspect
import types
import sys

from fields import Field, StringField, ListField, NumberField, ValidationError

from dataclass import dataclass, validate

@dataclass
class AppSite(object):
    # 定义字段验证
    name = StringField(min_length=1, max_length=128, regex=r'^[a-zA-Z0-9]+$')
    demo = ListField(min_length=1, max_length=128, item_type=NumberField(choices=[1,2,3]))
    url = StringField(min_length=1, max_length=256, regex=r'^https?://')
    status = StringField(default='active', choices=['active', 'inactive', 'pending'])

    # 使用装饰器的自定义验证方法
    @validate("name")
    def validate_name_custom(self, name):
        """额外验证：名称不能包含特殊字符"""
        if not name.isalnum():
            raise ValidationError("Name must be alphanumeric")

    @validate("url")
    def validate_url_custom(self, url):
        """URL字段的自定义验证"""
        if not url.startswith(('http://', 'https://')):
            raise ValidationError("URL must start with http:// or https://")

    # 自定义获取方法示例（直接使用属性名）
    def get_name(self):
        """自定义获取name的方法，返回大写形式"""
        # 直接从实例字典获取，避免递归调用
        return self.name.upper()

    def get_full_info(self):
        """自定义方法，返回完整信息"""
        name = self.__dict__.get('name', 'Unknown')
        url = self.__dict__.get('url', 'No URL')
        return "{0} - {1}".format(name, url)

@dataclass
class ApiInfo(object):
    api_id = StringField(max_length=27)
    app_site = AppSite  # dataclass字段
    lst = ListField(item_type=AppSite)


# 使用装饰器的新版本示例
@dataclass
class AppSiteDecorator(object):
    """使用装饰器定义的AppSite类，展示新的用法"""
    # 定义字段验证，包含正则表达式验证
    name = StringField(min_length=1, max_length=128, regex=r'^[a-zA-Z0-9_]+$')
    demo = ListField(min_length=1, max_length=128, item_type=NumberField(choices=[1,2,3]))
    url = StringField(min_length=1, max_length=256, regex=r'^https?://.+')
    status = StringField(default='active', choices=['active', 'inactive', 'pending'])
    email = StringField(required=False, regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # 使用装饰器的自定义验证方法
    @validate("name")
    def validate_name_length(self, name):
        """额外验证：名称长度必须大于3"""
        if len(name) < 3:
            raise ValidationError("Name must be at least 3 characters long")

    @validate("url")
    def validate_url_domain(self, url):
        """URL字段的自定义验证：检查域名"""
        if 'localhost' in url or '127.0.0.1' in url:
            raise ValidationError("URL cannot be localhost or 127.0.0.1")

    @validate("email")
    def validate_email_domain(self, email):
        """邮箱域名验证"""
        if email and not email.endswith(('.com', '.org', '.net')):
            raise ValidationError("Email must end with .com, .org, or .net")

    # 自定义获取方法示例（直接使用属性名）
    def get_name(self):
        """自定义获取name的方法，返回大写形式"""
        # 现在可以直接调用self.name，系统会自动避免递归
        print("Calling get_name()! " + self.name.upper() + self.status)
        return self.name.upper() + self.status

    def get_full_info(self):
        """自定义方法，返回完整信息"""
        name = self.__dict__.get('name', 'Unknown')
        url = self.__dict__.get('url', 'No URL')
        return "{0} - {1}".format(name, url)


@dataclass(repr=True, eq=True)
class ApiInfoDecorator(object):
    """使用装饰器定义的ApiInfo类"""
    api_id = StringField(max_length=27)
    app_site = AppSiteDecorator  # dataclass字段
    lst = ListField(item_type=AppSiteDecorator)

# 使用示例
if __name__ == "__main__":
    print("=== 测试原始DataClass ===")
    # 正确示例
    site = AppSite(
        name="MySite",
        url="https://example.com",
        demo=[1,2,3]
    )
    print("Original DataClass site.to_dict():", site.to_dict())

    site = AppSite(name="alice")
    print("site.name:", site.name)      # → Calling get_name()! \n ALICE
    print("site['name']:", site['name'])   # → Calling get_name()! \n ALICE

    print("\n=== 测试装饰器版本 ===")
    # 测试装饰器版本
    site_decorator = AppSiteDecorator(
        name="MySite123",
        url="https://example.com",
        demo=[1,2,3],
        email="test@example.com"
    )
    print("Decorator version site.to_dict():", site_decorator.to_dict())

    site_decorator = AppSiteDecorator(name="alice123")
    print("decorator site.name:", site_decorator.name)      # → Calling get_name()! \n ALICE123
    print("decorator site['name']:", site_decorator['name'])   # → Calling get_name()! \n ALICE123
    print("decorator site.get_full_info():", site_decorator.get_full_info())

    print("\n=== 测试正则表达式验证 ===")
    try:
        # 测试正则表达式验证失败
        AppSiteDecorator(name="invalid-name!", url="https://example.com", demo=[1,2,3])
    except ValidationError as e:
        print("正则验证错误 (name):", e)

    try:
        # 测试URL正则验证失败
        AppSiteDecorator(name="validname", url="ftp://example.com", demo=[1,2,3])
    except ValidationError as e:
        print("正则验证错误 (url):", e)

    try:
        # 测试邮箱正则验证失败
        AppSiteDecorator(name="validname", url="https://example.com", demo=[1,2,3], email="invalid-email")
    except ValidationError as e:
        print("正则验证错误 (email):", e)

    try:
        # 测试邮箱正则验证失败
        AppSiteDecorator(name="validname", url="https://example.com", demo=[1,2,3], email="xxx@email.cc")
    except ValidationError as e:
        print("正则验证错误 (email):", e)

    print("\n=== 测试装饰器自定义验证 ===")
    try:
        # 测试名称长度验证
        AppSiteDecorator(name="ab", url="https://example.com", demo=[1,2,3])
    except ValidationError as e:
        print("自定义验证错误 (name length):", e)

    try:
        # 测试URL域名验证
        AppSiteDecorator(name="validname", url="https://localhost:8080", demo=[1,2,3])
    except ValidationError as e:
        print("自定义验证错误 (url domain):", e)

    try:
        # 测试邮箱域名验证
        AppSiteDecorator(name="validname", url="https://example.com", demo=[1,2,3], email="test@example.xyz")
    except ValidationError as e:
        print("自定义验证错误 (email domain):", e)

    print("\n=== 测试dataclass字段重新赋值 ===")
    # 测试dataclass字段的创建和重新赋值
    try:
        api_info = ApiInfoDecorator(
            api_id='a'*27,
            app_site={
                'name': "MySite123",
                'url': "https://example.com",
                'demo': [1,2,3]
            }
        )
        print("✓ ApiInfo创建成功:")
        print("  api_info.app_site.name:", api_info.app_site.name)
        print("  api_info.app_site.url:", api_info.app_site.url)
        print("  type(api_info.app_site):", type(api_info.app_site).__name__)

        # 重新赋值dataclass字段
        print("\n重新赋值app_site字段...")
        api_info.app_site = {
            'name': "MySite456",
            'url': "https://example2.com",
            'demo': [1,2,3]
        }
        print("✓ 重新赋值成功:")
        print("  api_info.app_site.name:", api_info.app_site.name)
        print("  api_info.app_site.url:", api_info.app_site.url)
        print("  type(api_info.app_site):", type(api_info.app_site).__name__)

        # 测试重新赋值时的验证
        print("\n测试重新赋值时的验证...")
        try:
            api_info.app_site = {
                'name': "ab",  # 名称太短，应该失败
                'url': "https://example3.com",
                'demo': [1,2,3]
            }
        except ValidationError as e:
            print("✓ 重新赋值验证成功，捕获错误:", e)

    except ValidationError as e:
        print("✗ ApiInfo测试失败:", e)

    print("\n=== 测试ListField中的dataclass ===")
    try:
        api_info = ApiInfoDecorator(
            api_id='b'*27,
            app_site={
                'name': "MainSite",
                'url': "https://main.com",
                'demo': [1,2,3]
            },
            lst=[
                {
                    'name': "Site1",
                    'url': "https://site1.com",
                    'demo': [1,2]
                },
                {
                    'name': "Site2",
                    'url': "https://site2.com",
                    'demo': [2,3]
                }
            ]
        )
        print("✓ 包含ListField的ApiInfo创建成功:")
        print("  lst长度:", len(api_info.lst))
        print("  lst[0].name:", api_info.lst[0].name)
        print("  lst[1].name:", api_info.lst[1].name)
        print("  type(api_info.lst[0]):", type(api_info.lst[0]).__name__)

    except ValidationError as e:
        print("✗ ListField测试失败:")
        print(e)
        
    # 错误示例（demo 不在枚举中）
    try:
        AppSite(name="", url="https://example.com", demo=[1,2,4])
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))
    

    # 错误示例（demo为空）
    try:
        AppSite(name="", url="https://example.com", demo=[])
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))
    

    # 错误示例（名称为空）
    try:
        AppSite(name="", url="https://example.com")
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))
    

    # 错误示例（名称包含特殊字符）
    try:
        AppSite(name="My@Site", url="https://example.com")
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))
    
    # 错误示例（URL格式错误）
    try:
        AppSite(name="MySite", url="ftp://example.com")
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))
    
    # 错误示例（无效字段）
    try:
        AppSite(name="MySite", invalid_field="test")
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))

    # 嵌套模型
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's001',
            'url': 'http://example.com'
        })
        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error api info: {e}".format(e=e))

    # 嵌套模型 错误示例（名称包含特殊字符）
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's-001',
            'url': 'http://example.com'
        })
        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error app_site name: {e}".format(e=e))

    # 嵌套模型 错误示例（URL格式错误）
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's001',
            'url': 'ht://example.com'
        })
        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error app_site url: {e}".format(e=e))

    # 数组嵌套模型
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's001',
            'url': 'http://example.com'
        },
        lst=[{'name': 's001', 'url': 'http://example.com'}]
        )

        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error lst: {e}".format(e=e))

    # 数组嵌套模型  错误示例（名称包含特殊字符）
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's001',
            'url': 'http://example.com'
        },
        lst=[{'name': 's-001', 'url': 'http://example.com'}]
        )
        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error lst name: {e}".format(e=e))

    # 数组嵌套模型 错误示例（URL格式错误）
    try:
        api_info = ApiInfo(api_id='a'*27, app_site={
            'name': 's001',
            'url': 'http://example.com'
        },
        lst=[{'name': 's001', 'url': 'ftp://example.com'}]
        )
        print(api_info.to_dict())
    except ValidationError as e:
        print("Validation error lst url: {e}".format(e=e))

    print("\n=== 测试无效字段（不做校验）===")
    # 错误示例（无效字段）
    try:
        site_with_invalid = AppSite(name="MySite", invalid_field="test")
        print("✓ 包含无效字段的对象创建成功:")
        print("  site_with_invalid.name:", site_with_invalid.name)
        print("  site_with_invalid.invalid_field:", site_with_invalid.invalid_field)
        print("  site_with_invalid['invalid_field']:", site_with_invalid['invalid_field'])
        print("  site_with_invalid.to_dict():", site_with_invalid.to_dict())
    except ValidationError as e:
        print("Validation error: {e}".format(e=e))