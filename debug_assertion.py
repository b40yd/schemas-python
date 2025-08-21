# -*- coding: utf-8 -*-
"""
调试断言失败的问题
"""

from app_site_model import ApiInfo

# 创建包含dataclass字段的对象
api_info = ApiInfo(
    api_id="test123",
    app_site={
        "name": "MySite123",
        "url": "https://example.com"
    }
)

print("api_info.app_site.name 实际值:", repr(api_info.app_site.name))
print("api_info.app_site.name 类型:", type(api_info.app_site.name))
print("期望值:", repr("MYSITE123active"))

# 检查app_site对象
print("api_info.app_site:", api_info.app_site)
print("api_info.app_site.__dict__:", api_info.app_site.__dict__)
print("type(api_info.app_site):", type(api_info.app_site))
