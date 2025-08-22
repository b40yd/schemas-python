#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有自定义错误消息相关的测试
"""

import sys
import subprocess
import os

def run_test_file(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行 {description}")
    print(f"文件: {test_file}")
    print('='*60)
    
    try:
        # 检查文件是否存在
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        # 运行测试
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ 测试通过!")
            if result.stdout:
                print("\n输出:")
                print(result.stdout)
        else:
            print("❌ 测试失败!")
            if result.stdout:
                print("\n标准输出:")
                print(result.stdout)
            if result.stderr:
                print("\n错误输出:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 测试超时!")
        return False
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 开始运行自定义错误消息功能测试套件")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 定义要运行的测试文件
    test_files = [
        {
            'file': 'test_custom_error_messages.py',
            'description': '自定义错误消息功能测试 (断言方式)'
        },
        {
            'file': 'test_custom_error_messages_unittest.py',
            'description': '自定义错误消息功能测试 (unittest 框架)'
        },
        {
            'file': 'demo_custom_error_messages.py',
            'description': '自定义错误消息功能演示'
        },
        {
            'file': 'test_dataclass_fields.py',
            'description': '现有功能兼容性测试'
        }
    ]
    
    # 运行所有测试
    passed_tests = 0
    total_tests = len(test_files)
    
    for test_info in test_files:
        if run_test_file(test_info['file'], test_info['description']):
            passed_tests += 1
    
    # 输出总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print('='*60)
    print(f"总测试文件数: {total_tests}")
    print(f"通过测试数: {passed_tests}")
    print(f"失败测试数: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试都通过了！")
        print("\n✨ 自定义错误消息功能已成功实现并通过所有测试:")
        print("   • 默认错误消息功能")
        print("   • 自定义错误消息功能")
        print("   • 错误消息模板格式化")
        print("   • 多语言支持")
        print("   • dataclass 集成")
        print("   • 列表字段验证")
        print("   • 复杂场景处理")
        print("   • 向后兼容性")
        return 0
    else:
        print(f"\n❌ 有 {total_tests - passed_tests} 个测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
