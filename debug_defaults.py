# -*- coding: utf-8 -*-
"""
调试字段默认值
"""

from app_site_model import AppSite

site = AppSite(name="TestSite")
print("site.demo:", repr(site.demo))
print("site.url:", repr(site.url))
print("site.status:", repr(site.status))
print("site.__dict__:", site.__dict__)
