#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import argparse
import os
from pathlib import Path


def discover_and_run_tests(test_type="all"):
    """发现并运行测试

    Args:
        test_type: 测试类型，可选值：'unit', 'integration', 'all'
    
    Returns:
        bool: 测试是否全部通过
    """
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 创建测试加载器
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 根据测试类型加载测试
    if test_type in ["unit", "all"]:
        unit_tests_dir = current_dir / "tests" / "unit"
        if unit_tests_dir.exists():
            print(f"发现单元测试目录: {unit_tests_dir}")
            unit_tests = loader.discover(str(unit_tests_dir), pattern="test_*.py")
            suite.addTests(unit_tests)
        else:
            print(f"警告: 单元测试目录不存在: {unit_tests_dir}")
    
    if test_type in ["integration", "all"]:
        integration_tests_dir = current_dir / "tests" / "integration"
        if integration_tests_dir.exists():
            print(f"发现集成测试目录: {integration_tests_dir}")
            integration_tests = loader.discover(str(integration_tests_dir), pattern="test_*.py")
            suite.addTests(integration_tests)
        else:
            print(f"警告: 集成测试目录不存在: {integration_tests_dir}")
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印测试结果摘要
    print("\n" + "="*80)
    print(f"测试结果摘要:")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 如果有失败或错误，返回False
    return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行LLM角色管理系统的测试")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="指定要运行的测试类型: unit(单元测试), integration(集成测试), all(所有测试)"
    )
    
    args = parser.parse_args()
    
    # 确保测试目录存在
    for test_dir in ["tests/unit", "tests/integration"]:
        os.makedirs(test_dir, exist_ok=True)
    
    print(f"开始运行{args.type}测试...")
    success = discover_and_run_tests(args.type)
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 