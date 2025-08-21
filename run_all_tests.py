# -*- coding: utf-8 -*-
"""
运行所有测试用例的主入口
"""

import sys
import traceback

def run_test_file(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行 {description}")
    print(f"文件: {test_file}")
    print('='*60)
    
    try:
        # 动态导入并运行测试
        if test_file == "test_all_with_assertions.py":
            from test_all_with_assertions import (
                test_original_dataclass, test_decorator_version, 
                test_regex_validation, test_custom_validation,
                test_dataclass_field_reassignment, test_listfield_dataclass,
                test_invalid_fields, test_getter_self_call, test_validation_error_paths
            )
            
            test_original_dataclass()
            test_decorator_version()
            test_regex_validation()
            test_custom_validation()
            test_dataclass_field_reassignment()
            test_listfield_dataclass()
            test_invalid_fields()
            test_getter_self_call()
            test_validation_error_paths()
            
        elif test_file == "test_comprehensive_assertions.py":
            from test_comprehensive_assertions import (
                test_field_defaults, test_field_validation_boundaries,
                test_to_dict_completeness, test_nested_dataclass_validation,
                test_listfield_validation, test_getter_method_edge_cases,
                test_type_validation, test_error_message_clarity
            )
            
            test_field_defaults()
            test_field_validation_boundaries()
            test_to_dict_completeness()
            test_nested_dataclass_validation()
            test_listfield_validation()
            test_getter_method_edge_cases()
            test_type_validation()
            test_error_message_clarity()
            
        print(f"\n✅ {description} - 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ {description} - 测试失败！")
        print(f"错误: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始运行所有测试用例...")
    
    test_files = [
        ("test_all_with_assertions.py", "基础功能测试"),
        ("test_comprehensive_assertions.py", "全面边界测试")
    ]
    
    passed = 0
    failed = 0
    
    for test_file, description in test_files:
        if run_test_file(test_file, description):
            passed += 1
        else:
            failed += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    print(f"✅ 通过: {passed} 个测试文件")
    print(f"❌ 失败: {failed} 个测试文件")
    print(f"📊 总计: {passed + failed} 个测试文件")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！系统功能正常！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试文件失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
