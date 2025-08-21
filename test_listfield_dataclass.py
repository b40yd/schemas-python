# -*- coding: utf-8 -*-
"""
专门测试ListField中的dataclass功能
"""

from fields import StringField, ListField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class AppSiteDecorator(object):
    """使用装饰器定义的AppSite类"""
    name = StringField(min_length=1, max_length=128, regex=r'^[a-zA-Z0-9_]+$')
    demo = ListField(min_length=1, max_length=128, item_type=NumberField(choices=[1,2,3]))
    url = StringField(min_length=1, max_length=256, regex=r'^https?://.+')
    status = StringField(default='active', choices=['active', 'inactive', 'pending'])

@dataclass(repr=True, eq=True)
class ApiInfoDecorator(object):
    """使用装饰器定义的ApiInfo类"""
    api_id = StringField(max_length=27)
    app_site = AppSiteDecorator  # dataclass字段
    lst = ListField(item_type=AppSiteDecorator)  # ListField包含dataclass

def test_listfield_dataclass():
    print("=== 测试ListField中的dataclass功能 ===\n")
    
    # 1. 测试基本创建
    print("1. 测试基本创建:")
    try:
        api_info = ApiInfoDecorator(
            api_id='test123',
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
        
        print("✓ 创建成功!")
        print("  api_id:", api_info.api_id)
        print("  app_site.name:", api_info.app_site.name)
        print("  lst长度:", len(api_info.lst))
        print("  lst[0].name:", api_info.lst[0].name)
        print("  lst[1].name:", api_info.lst[1].name)
        print("  type(api_info.app_site):", type(api_info.app_site).__name__)
        print("  type(api_info.lst[0]):", type(api_info.lst[0]).__name__)
        print("  type(api_info.lst[1]):", type(api_info.lst[1]).__name__)
        
    except Exception as e:
        print("✗ 创建失败:", e)
        import traceback
        traceback.print_exc()
        return
    
    # 2. 测试to_dict功能
    print("\n2. 测试to_dict功能:")
    try:
        result = api_info.to_dict()
        print("✓ to_dict成功!")
        print("  结果类型:", type(result).__name__)
        print("  包含字段:", list(result.keys()))
        print("  app_site类型:", type(result['app_site']).__name__)
        print("  lst类型:", type(result['lst']).__name__)
        print("  lst长度:", len(result['lst']))
        if result['lst']:
            print("  lst[0]类型:", type(result['lst'][0]).__name__)
    except Exception as e:
        print("✗ to_dict失败:", e)
    
    # 3. 测试字段访问
    print("\n3. 测试字段访问:")
    try:
        print("  通过属性访问 api_info.lst[0].name:", api_info.lst[0].name)
        print("  通过索引访问 api_info['lst'][0].name:", api_info['lst'][0].name)
        print("  通过get方法访问 api_info.get('lst')[0].name:", api_info.get('lst')[0].name)
        print("✓ 字段访问成功!")
    except Exception as e:
        print("✗ 字段访问失败:", e)
    
    # 4. 测试验证功能
    print("\n4. 测试验证功能:")
    try:
        # 测试无效的lst项
        ApiInfoDecorator(
            api_id='test123',
            app_site={
                'name': "MainSite",
                'url': "https://main.com", 
                'demo': [1,2,3]
            },
            lst=[
                {
                    'name': "Invalid-Name!",  # 包含特殊字符，应该失败
                    'url': "https://site1.com",
                    'demo': [1,2]
                }
            ]
        )
        print("✗ 应该失败但没有失败!")
    except ValidationError as e:
        print("✓ 正确捕获验证错误:", e)
    except Exception as e:
        print("✗ 意外错误:", e)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_listfield_dataclass()
