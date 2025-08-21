# -*- coding: utf-8 -*-
"""
最终测试：无效字段和自定义方法
"""

from fields import StringField, NumberField, ValidationError
from dataclass import dataclass, validate

@dataclass
class TestFinal(object):
    name = StringField(min_length=1, max_length=50)
    age = NumberField(minvalue=0, maxvalue=150)

def test_invalid_fields():
    print("=== 测试无效字段（不做校验）===")
    
    # 测试无效字段
    try:
        obj = TestFinal(name="test", age=25, invalid_field="should_work")
        print("✓ 包含无效字段的对象创建成功:")
        print("  obj.name:", obj.name)
        print("  obj.age:", obj.age)
        print("  obj.__dict__:", obj.__dict__)
        print("  'invalid_field' in obj.__dict__:", 'invalid_field' in obj.__dict__)
        if 'invalid_field' in obj.__dict__:
            print("  obj.__dict__['invalid_field']:", obj.__dict__['invalid_field'])
        try:
            print("  obj.invalid_field:", obj.invalid_field)
        except AttributeError as e:
            print("  obj.invalid_field error:", e)
        try:
            print("  obj['invalid_field']:", obj['invalid_field'])
        except KeyError as e:
            print("  obj['invalid_field'] error:", e)
        print("  obj.to_dict():", obj.to_dict())
        
    except Exception as e:
        print("✗ 创建失败:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_invalid_fields()
