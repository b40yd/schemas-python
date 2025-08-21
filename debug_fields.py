# -*- coding: utf-8 -*-
"""
调试字段收集问题
"""

from fields import StringField, ListField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class AppSiteDecorator(object):
    """使用装饰器定义的AppSite类，展示新的用法"""
    # 定义字段验证，包含正则表达式验证
    name = StringField(min_length=1, max_length=128, regex=r'^[a-zA-Z0-9_]+$')
    demo = ListField(min_length=1, max_length=128, item_type=NumberField(choices=[1,2,3]))
    url = StringField(min_length=1, max_length=256, regex=r'^https?://.+')
    status = StringField(default='active', choices=['active', 'inactive', 'pending'])

    def get_name(self):
        return self.name.upper()

@dataclass(repr=True, eq=True)
class ApiInfoDecorator(object):
    """使用装饰器定义的ApiInfo类"""
    api_id = StringField(max_length=27)
    app_site = AppSiteDecorator  # dataclass字段
    lst = ListField(item_type=AppSiteDecorator)

def debug_fields():
    print("=== 调试字段收集 ===")
    
    print("AppSiteDecorator._dataclass_fields:")
    for key, field in AppSiteDecorator._dataclass_fields.items():
        print("  {}: {}".format(key, type(field).__name__))
    
    print("\nApiInfoDecorator._dataclass_fields:")
    for key, field in ApiInfoDecorator._dataclass_fields.items():
        print("  {}: {}".format(key, type(field).__name__))
    
    print("\n=== 测试创建 ===")
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
                }
            ]
        )
        print("✓ 创建成功!")
        print("  api_info.api_id:", api_info.api_id)
        print("  type(api_info.app_site):", type(api_info.app_site).__name__, api_info.app_site.name)
        print("  type(api_info.lst[0]):", type(api_info.lst[0]).__name__)
        
    except Exception as e:
        print("✗ 创建失败:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fields()
