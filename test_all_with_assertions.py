# -*- coding: utf-8 -*-
"""
完整的测试用例，包含所有功能的断言判断
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass, validate
from app_site_model import AppSite, AppSiteDecorator, ApiInfo, ApiInfoDecorator

def test_original_dataclass():
    """测试原始DataClass功能"""
    print("=== 测试原始DataClass ===")
    
    # 测试基本创建
    site = AppSite(
        name="MySite",
        url="https://example.com",
        demo=[1, 2, 3]
    )
    
    # 断言：to_dict()包含所有字段
    site_dict = site.to_dict()
    assert 'name' in site_dict, "to_dict()应该包含name字段"
    assert 'url' in site_dict, "to_dict()应该包含url字段"
    assert 'demo' in site_dict, "to_dict()应该包含demo字段"
    assert 'status' in site_dict, "to_dict()应该包含status字段"
    assert site_dict['name'] == 'MySite', "name字段值应该是MySite"
    assert site_dict['url'] == 'https://example.com', "url字段值应该正确"
    assert site_dict['demo'] == [1, 2, 3], "demo字段值应该正确"
    assert site_dict['status'] == 'active', "status字段默认值应该是active"
    print("✓ 原始DataClass基本功能测试通过")
    
    # 测试自定义getter方法
    site = AppSite(name="alice")
    name_result = site.name
    name_index_result = site['name']
    
    assert name_result == "ALICE", "自定义get_name方法应该返回大写的ALICE"
    assert name_index_result == "ALICE", "通过索引访问name也应该调用自定义方法"
    print("✓ 原始DataClass自定义getter方法测试通过")

def test_decorator_version():
    """测试装饰器版本功能"""
    print("\n=== 测试装饰器版本 ===")
    
    # 测试装饰器版本创建
    site_decorator = AppSiteDecorator(
        name="MySite123",
        url="https://example.com",
        demo=[1, 2, 3],
        email="test@example.com"
    )
    
    # 断言：to_dict()包含所有字段包括新增的email
    site_dict = site_decorator.to_dict()
    assert 'email' in site_dict, "装饰器版本应该包含email字段"
    assert site_dict['email'] == 'test@example.com', "email字段值应该正确"
    print("✓ 装饰器版本基本功能测试通过")
    
    # 测试装饰器版本的自定义getter
    site_decorator = AppSiteDecorator(name="alice123")
    name_result = site_decorator.name
    name_index_result = site_decorator['name']
    full_info = site_decorator.get_full_info()
    
    assert name_result == "ALICE123active", "装饰器版本get_name应该返回name+status的大写形式"
    assert name_index_result == "ALICE123active", "通过索引访问也应该调用自定义方法"
    assert "alice123" in full_info.lower(), "get_full_info应该包含name信息"
    assert "no url" in full_info.lower(), "get_full_info应该显示No URL"
    print("✓ 装饰器版本自定义getter方法测试通过")

def test_regex_validation():
    """测试正则表达式验证"""
    print("\n=== 测试正则表达式验证 ===")
    
    # 测试name字段正则验证失败
    try:
        AppSiteDecorator(name="invalid-name!", url="https://example.com", demo=[1, 2, 3])
        assert False, "name字段包含非法字符应该抛出ValidationError"
    except ValidationError as e:
        assert "Value does not match pattern" in str(e), "应该是正则表达式验证错误"
        print("✓ name字段正则验证测试通过")
    
    # 测试URL正则验证失败
    try:
        AppSiteDecorator(name="validname", url="ftp://example.com", demo=[1, 2, 3])
        assert False, "URL不是http/https协议应该抛出ValidationError"
    except ValidationError as e:
        assert "Value does not match pattern" in str(e), "应该是URL正则表达式验证错误"
        print("✓ URL字段正则验证测试通过")
    
    # 测试邮箱正则验证失败
    try:
        AppSiteDecorator(name="validname", url="https://example.com", demo=[1, 2, 3], email="invalid-email")
        assert False, "无效邮箱格式应该抛出ValidationError"
    except ValidationError as e:
        assert "Value does not match pattern" in str(e), "应该是邮箱正则表达式验证错误"
        print("✓ 邮箱字段正则验证测试通过")

def test_custom_validation():
    """测试自定义验证装饰器"""
    print("\n=== 测试装饰器自定义验证 ===")
    
    # 测试name长度验证
    try:
        AppSiteDecorator(name="ab", url="https://example.com", demo=[1, 2, 3])
        assert False, "name长度小于3应该抛出ValidationError"
    except ValidationError as e:
        assert "Name must be at least 3 characters long" in str(e), "应该是name长度验证错误"
        print("✓ name长度自定义验证测试通过")
    
    # 测试URL域名验证
    try:
        AppSiteDecorator(name="validname", url="https://localhost/test", demo=[1, 2, 3])
        assert False, "URL包含localhost应该抛出ValidationError"
    except ValidationError as e:
        assert "URL cannot be localhost or 127.0.0.1" in str(e), "应该是URL域名验证错误"
        print("✓ URL域名自定义验证测试通过")
    
    # 测试邮箱域名验证
    try:
        AppSiteDecorator(name="validname", url="https://example.com", demo=[1, 2, 3], email="test@example.edu")
        assert False, "邮箱域名不是.com/.org/.net应该抛出ValidationError"
    except ValidationError as e:
        assert "Email must end with .com, .org, or .net" in str(e), "应该是邮箱域名验证错误"
        print("✓ 邮箱域名自定义验证测试通过")

def test_dataclass_field_reassignment():
    """测试dataclass字段重新赋值"""
    print("\n=== 测试dataclass字段重新赋值 ===")

    # 创建包含dataclass字段的对象（使用装饰器版本）
    api_info = ApiInfoDecorator(
        api_id="test123",
        app_site={
            "name": "MySite123",
            "url": "https://example.com"
        }
    )

    # 断言：初始创建成功
    assert hasattr(api_info, 'app_site'), "ApiInfoDecorator应该有app_site属性"
    assert api_info.app_site.name == "MYSITE123active", "app_site.name应该调用自定义getter"
    assert api_info.app_site.url == "https://example.com", "app_site.url应该正确"
    assert type(api_info.app_site).__name__ == "AppSiteDecorator", "app_site应该是AppSiteDecorator类型"
    print("✓ ApiInfoDecorator创建成功测试通过")

    # 重新赋值app_site字段
    api_info.app_site = {
        "name": "MySite456",
        "url": "https://example2.com"
    }

    # 断言：重新赋值成功
    assert api_info.app_site.name == "MYSITE456active", "重新赋值后name应该正确"
    assert api_info.app_site.url == "https://example2.com", "重新赋值后url应该正确"
    assert type(api_info.app_site).__name__ == "AppSiteDecorator", "重新赋值后类型应该正确"
    print("✓ 重新赋值成功测试通过")

    # 测试重新赋值时的验证
    try:
        api_info.app_site = {"name": "ab"}  # name长度不足
        assert False, "重新赋值时应该进行验证"
    except ValidationError as e:
        assert "Name must be at least 3 characters long" in str(e), "重新赋值验证错误信息应该正确"
        print("✓ 重新赋值验证测试通过")

def test_listfield_dataclass():
    """测试ListField中的dataclass"""
    print("\n=== 测试ListField中的dataclass ===")

    # 创建包含ListField的对象（使用装饰器版本）
    api_info = ApiInfoDecorator(
        api_id="test123",
        app_site={"name": "MainSite", "url": "https://main.com"},
        lst=[
            {"name": "Site1", "url": "https://site1.com"},
            {"name": "Site2", "url": "https://site2.com"}
        ]
    )

    # 断言：ListField创建成功
    assert hasattr(api_info, 'lst'), "ApiInfoDecorator应该有lst属性"
    assert len(api_info.lst) == 2, "lst应该包含2个元素"
    assert api_info.lst[0].name == "SITE1active", "lst[0].name应该调用自定义getter"
    assert api_info.lst[1].name == "SITE2active", "lst[1].name应该调用自定义getter"
    assert type(api_info.lst[0]).__name__ == "AppSiteDecorator", "lst元素应该是AppSiteDecorator类型"
    print("✓ 包含ListField的ApiInfoDecorator创建成功测试通过")

def test_invalid_fields():
    """测试无效字段（不做校验）"""
    print("\n=== 测试无效字段（不做校验）===")

    # 创建包含无效字段的对象
    site_with_invalid = AppSiteDecorator(
        name="MySite",
        invalid_field="test"  # 这是一个未定义的字段
    )

    # 断言：无效字段被正确处理
    assert hasattr(site_with_invalid, 'invalid_field'), "对象应该有invalid_field属性"
    assert site_with_invalid.invalid_field == "test", "invalid_field属性访问应该正确"
    assert site_with_invalid['invalid_field'] == "test", "invalid_field索引访问应该正确"

    # 断言：to_dict()包含无效字段
    site_dict = site_with_invalid.to_dict()
    assert 'invalid_field' in site_dict, "to_dict()应该包含无效字段"
    assert site_dict['invalid_field'] == "test", "to_dict()中无效字段值应该正确"
    print("✓ 包含无效字段的对象创建成功测试通过")

def test_getter_self_call():
    """测试在getter方法中调用self.属性名"""
    print("\n=== 测试getter方法中的self调用 ===")

    @dataclass
    class TestSelfCall(object):
        name = StringField(min_length=1, max_length=50)
        age = NumberField(minvalue=0, maxvalue=150)

        def get_name(self):
            """可以在getter中直接调用self.name"""
            return self.name.upper() + "_CUSTOM"

    # 创建测试对象
    obj = TestSelfCall(name="test", age=25)

    # 断言：getter方法中可以调用self.属性名
    name_result = obj.name
    assert name_result == "TEST_CUSTOM", "getter方法中调用self.name应该返回原始值"

    # 断言：索引访问也正常
    name_index_result = obj['name']
    assert name_index_result == "TEST_CUSTOM", "索引访问也应该调用getter方法"

    # 断言：没有getter的字段正常访问
    age_result = obj.age
    assert age_result == 25, "没有getter的字段应该返回原始值"
    print("✓ getter方法中的self调用测试通过")

def test_validation_error_paths():
    """测试验证错误路径信息"""
    print("\n=== 测试验证错误路径信息 ===")

    # 测试嵌套字段验证错误（使用装饰器版本）
    try:
        ApiInfoDecorator(
            api_id="test",
            app_site={"name": "ab"}  # name长度不足
        )
        assert False, "嵌套字段验证错误应该抛出ValidationError"
    except ValidationError as e:
        error_msg = str(e)
        assert "app_site" in error_msg or "Name must be at least 3 characters long" in error_msg, \
            "验证错误应该包含字段路径信息或具体错误信息"
        print("✓ 嵌套字段验证错误路径测试通过")

    # 测试ListField中的验证错误（使用装饰器版本）
    try:
        ApiInfoDecorator(
            api_id="test",
            app_site={"name": "MainSite", "url": "https://main.com"},
            lst=[{"name": "ab"}]  # lst中的name长度不足
        )
        assert False, "ListField中的验证错误应该抛出ValidationError"
    except ValidationError as e:
        error_msg = str(e)
        assert "lst" in error_msg or "Name must be at least 3 characters long" in error_msg, \
            "ListField验证错误应该包含字段路径信息"
        print("✓ ListField验证错误路径测试通过")

if __name__ == "__main__":
    test_original_dataclass()
    test_decorator_version()
    test_regex_validation()
    test_custom_validation()
    test_dataclass_field_reassignment()
    test_listfield_dataclass()
    test_invalid_fields()
    test_getter_self_call()
    test_validation_error_paths()
    print("\n🎉 所有测试用例通过！")
