# -*- coding: utf-8 -*-
"""
全面的测试用例，包含边界情况和详细断言
"""

from fields import StringField, NumberField, ListField, ValidationError
from dataclass import dataclass
from app_site_model import AppSite, AppSiteDecorator, ApiInfoDecorator

def test_field_defaults():
    """测试字段默认值"""
    print("=== 测试字段默认值 ===")

    # 创建只提供必需字段的对象
    site = AppSite(name="TestSite")

    # 断言：默认值正确设置
    assert site.status == "active", "status字段默认值应该是active"

    # 检查未设置字段的行为（返回Field对象或默认值）
    from fields import ListField, StringField
    assert isinstance(site.demo, ListField) or site.demo is None, "demo字段应该返回Field对象或None"
    assert isinstance(site.url, StringField) or site.url is None, "url字段应该返回Field对象或None"

    # 检查__dict__中只包含实际设置的字段
    assert 'name' in site.__dict__, "__dict__应该包含设置的name字段"
    assert 'status' in site.__dict__, "__dict__应该包含默认的status字段"
    assert 'demo' not in site.__dict__ or site.__dict__['demo'] is None, "__dict__中demo应该不存在或为None"
    print("✓ 字段默认值测试通过")

def test_field_validation_boundaries():
    """测试字段验证边界条件"""
    print("\n=== 测试字段验证边界条件 ===")
    
    # 测试StringField长度边界
    try:
        AppSiteDecorator(name="")  # 空字符串
        assert False, "空字符串应该抛出ValidationError"
    except ValidationError as e:
        assert "Length must be at least 1" in str(e), "应该是长度验证错误"
        print("✓ StringField最小长度验证测试通过")
    
    # 测试StringField最大长度
    long_name = "a" * 129  # 超过max_length=128
    try:
        AppSiteDecorator(name=long_name)
        assert False, "超长字符串应该抛出ValidationError"
    except ValidationError as e:
        assert "Length must be at most 128" in str(e), "应该是最大长度验证错误"
        print("✓ StringField最大长度验证测试通过")
    
    # 测试边界值成功情况
    boundary_name = "a" * 128  # 正好128个字符
    site = AppSiteDecorator(name=boundary_name)
    assert len(site.__dict__['name']) == 128, "边界长度字符串应该被接受"
    print("✓ StringField边界值成功测试通过")

def test_to_dict_completeness():
    """测试to_dict()方法的完整性"""
    print("\n=== 测试to_dict()方法完整性 ===")
    
    # 创建包含所有字段的对象
    site = AppSiteDecorator(
        name="TestSite",
        url="https://test.com",
        demo=[1, 2, 3],
        email="test@example.com",
        invalid_field="should_be_included"
    )
    
    site_dict = site.to_dict()
    
    # 断言：所有字段都在to_dict()中
    expected_fields = ['name', 'url', 'demo', 'status', 'email', 'invalid_field']
    for field in expected_fields:
        assert field in site_dict, f"to_dict()应该包含{field}字段"
    
    # 断言：私有字段不在to_dict()中
    private_fields = ['_initializing', '_in_getter_call', '_dataclass_fields']
    for field in private_fields:
        assert field not in site_dict, f"to_dict()不应该包含私有字段{field}"
    
    print("✓ to_dict()方法完整性测试通过")

def test_nested_dataclass_validation():
    """测试嵌套dataclass的验证"""
    print("\n=== 测试嵌套dataclass验证 ===")
    
    # 测试嵌套对象的深度验证
    try:
        ApiInfoDecorator(
            api_id="test123",
            app_site={
                "name": "ValidName",
                "url": "https://example.com",
                "email": "invalid@example.xyz"  # 无效的邮箱域名
            }
        )
        assert False, "嵌套对象的邮箱验证应该失败"
    except ValidationError as e:
        error_msg = str(e)
        assert "Email must end with .com, .org, or .net" in error_msg, "应该是邮箱域名验证错误"
        print("✓ 嵌套dataclass验证测试通过")

def test_listfield_validation():
    """测试ListField的验证"""
    print("\n=== 测试ListField验证 ===")
    
    # 测试ListField中每个元素的验证
    try:
        ApiInfoDecorator(
            api_id="test123",
            app_site={"name": "MainSite", "url": "https://main.com"},
            lst=[
                {"name": "ValidSite1", "url": "https://site1.com"},
                {"name": "InvalidSite", "url": "ftp://invalid.com"}  # 无效URL协议
            ]
        )
        assert False, "ListField中的URL验证应该失败"
    except ValidationError as e:
        error_msg = str(e)
        assert "Value does not match pattern" in error_msg, "应该是URL正则验证错误"
        print("✓ ListField元素验证测试通过")
    
    # 测试空ListField
    api_info = ApiInfoDecorator(
        api_id="test123",
        app_site={"name": "MainSite", "url": "https://main.com"},
        lst=[]
    )
    assert len(api_info.lst) == 0, "空ListField应该被正确处理"
    print("✓ 空ListField测试通过")

def test_getter_method_edge_cases():
    """测试getter方法的边界情况"""
    print("\n=== 测试getter方法边界情况 ===")
    
    @dataclass
    class EdgeCaseTest(object):
        name = StringField(min_length=1, max_length=50)
        value = NumberField(minvalue=0, maxvalue=100)
        
        def get_name(self):
            """测试在getter中访问不存在的属性"""
            try:
                # 尝试访问不存在的属性
                nonexistent = self.nonexistent_field
                return f"ERROR: {nonexistent}"
            except AttributeError:
                return self.name.upper() + "_SAFE"
    
    obj = EdgeCaseTest(name="test", value=50)
    result = obj.name
    assert result == "TEST_SAFE", "getter方法应该正确处理AttributeError"
    print("✓ getter方法边界情况测试通过")

def test_type_validation():
    """测试类型验证"""
    print("\n=== 测试类型验证 ===")

    @dataclass
    class TypeTest(object):
        count = NumberField(minvalue=0, maxvalue=1000)

    # 测试正确的数字类型
    obj = TypeTest(count=123)
    assert obj.count == 123, "NumberField应该接受正确的数字"
    assert isinstance(obj.count, int), "应该保持整数类型"

    # 测试错误的类型
    try:
        TypeTest(count="123")  # 字符串不被接受
        assert False, "NumberField应该拒绝字符串类型"
    except ValidationError as e:
        assert "Value must be a number" in str(e), "应该是类型验证错误"

    print("✓ 类型验证测试通过")

def test_error_message_clarity():
    """测试错误信息的清晰度"""
    print("\n=== 测试错误信息清晰度 ===")
    
    # 测试多个验证错误的情况
    try:
        AppSiteDecorator(
            name="ab",  # 长度不足
            url="ftp://invalid.com",  # 协议错误
            email="invalid-email"  # 格式错误
        )
        assert False, "多个验证错误应该抛出ValidationError"
    except ValidationError as e:
        error_msg = str(e)
        # 至少应该包含一个具体的错误信息
        has_specific_error = any([
            "Name must be at least 3 characters long" in error_msg,
            "Value does not match pattern" in error_msg,
            "Email must end with" in error_msg
        ])
        assert has_specific_error, f"错误信息应该包含具体的验证错误: {error_msg}"
        print("✓ 错误信息清晰度测试通过")

if __name__ == "__main__":
    test_field_defaults()
    test_field_validation_boundaries()
    test_to_dict_completeness()
    test_nested_dataclass_validation()
    test_listfield_validation()
    test_getter_method_edge_cases()
    test_type_validation()
    test_error_message_clarity()
    print("\n🎉 所有全面测试用例通过！")
