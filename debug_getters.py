# -*- coding: utf-8 -*-
"""
调试getter方法收集
"""

from fields import StringField, ListField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class TestGetters(object):
    name = StringField(min_length=1, max_length=128)
    age = NumberField(minvalue=0, maxvalue=150)
    
    def name(self):
        """自定义获取name的方法，返回大写形式"""
        name = self.__dict__.get('name', '')
        return name.upper()

def debug_getters():
    print("=== 调试getter方法收集 ===")
    
    print("TestGetters._dataclass_fields:")
    for key, field in TestGetters._dataclass_fields.items():
        print("  {}: {}".format(key, type(field).__name__))
    
    print("\nTestGetters._dataclass_getters:")
    if hasattr(TestGetters, '_dataclass_getters'):
        for key, getter in TestGetters._dataclass_getters.items():
            print("  {}: {}".format(key, getter))
    else:
        print("  没有_dataclass_getters属性")
    
    print("\n=== 测试getter调用 ===")
    try:
        obj = TestGetters(name="test", age=25)
        print("obj.name:", obj.name)
        print("obj['name']:", obj['name'])
        print("obj.__dict__['name']:", obj.__dict__.get('name'))
        
    except Exception as e:
        print("错误:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_getters()
