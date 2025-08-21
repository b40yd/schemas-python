# -*- coding: utf-8 -*-
"""
测试在getter方法中直接调用self.属性名
"""

from fields import StringField, NumberField
from dataclass import dataclass

@dataclass
class TestSelfCall(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)
    
    def get_name(self):
        """自定义获取name的方法，可以直接调用self.name"""
        print("在get_name中调用self.name:", self.name)
        print("在get_name中调用self.age:", self.age)
        return self.name.upper() + "_CUSTOM"

def test_self_call():
    print("=== 测试在getter方法中调用self.属性名 ===")
    
    try:
        obj = TestSelfCall(name="test", age=25)
        print("obj创建成功")
        print("obj.__dict__:", obj.__dict__)
        
        print("\n直接访问obj.name:")
        result = obj.name
        print("结果:", result)
        
        print("\n通过索引访问obj['name']:")
        result = obj['name']
        print("结果:", result)
        
        print("\n直接访问obj.age (没有getter):")
        result = obj.age
        print("结果:", result)
        
    except Exception as e:
        print("错误:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_self_call()
