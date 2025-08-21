# -*- coding: utf-8 -*-
"""
调试name方法收集问题
"""

from fields import StringField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class TestNameMethod(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)
    
    def name(self):
        """自定义获取name的方法，返回大写形式"""
        print("调用了自定义name方法!")
        name_value = self.__dict__.get('name', '')
        return name_value.upper() + "_CUSTOM"

def debug_name_method():
    print("=== 调试name方法收集 ===")
    
    print("TestNameMethod.__dict__.keys():")
    for key in TestNameMethod.__dict__.keys():
        val = TestNameMethod.__dict__[key]
        print("  {}: {} ({})".format(key, type(val).__name__, val))
    
    print("\nTestNameMethod._dataclass_fields:")
    if hasattr(TestNameMethod, '_dataclass_fields'):
        for key, field in TestNameMethod._dataclass_fields.items():
            print("  {}: {}".format(key, type(field).__name__))
    else:
        print("  没有_dataclass_fields属性")
    
    print("\nTestNameMethod._dataclass_getters:")
    if hasattr(TestNameMethod, '_dataclass_getters'):
        for key, getter in TestNameMethod._dataclass_getters.items():
            print("  {}: {}".format(key, getter))
    else:
        print("  没有_dataclass_getters属性")
    
    print("\n=== 测试name方法调用 ===")
    try:
        obj = TestNameMethod(name="test", age=25)
        print("obj.__dict__:", obj.__dict__)
        print("通过属性访问obj.name:", obj.name)
        print("通过索引访问obj['name']:", obj['name'])

    except Exception as e:
        print("错误:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_name_method()
