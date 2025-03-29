#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import urllib.parse
from pprint import pprint
from typing import Dict, Any
import os

# API基础URL
BASE_URL = "http://localhost:8000"

# 修复可能的代理问题
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

# 辅助函数
def pretty_print_response(response):
    """美化输出响应"""
    print("\n状态码:", response.status_code)
    
    try:
        data = response.json()
        print("\n响应数据:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except:
        print("\n响应内容:", response.text)
    
    print("-" * 50)

def test_health_check():
    """测试健康检查API"""
    print("\n测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    pretty_print_response(response)

def test_create_role():
    """测试创建角色API"""
    print("\n测试创建角色...")
    data = {
        "name": "技术顾问",
        "description": "提供技术咨询和问题解决方案",
        "role_type": "advisor",
        "language_style": "专业",
        "knowledge_domains": ["编程", "软件开发", "系统架构"],
        "response_mode": "详细",
        "allowed_topics": ["技术问题", "编程语言", "最佳实践"],
        "forbidden_topics": ["非技术话题", "个人信息"]
    }
    
    response = requests.post(f"{BASE_URL}/roles", json=data)
    pretty_print_response(response)
    
    # 返回创建的角色ID，用于后续测试
    if response.status_code == 200 and response.json().get("success"):
        return response.json().get("data", {}).get("id")
    return None

def test_get_role(role_id):
    """测试获取角色API"""
    print(f"\n测试获取角色 (ID: {role_id})...")
    response = requests.get(f"{BASE_URL}/roles/{role_id}")
    pretty_print_response(response)

def test_update_role(role_id):
    """测试更新角色API"""
    print(f"\n测试更新角色 (ID: {role_id})...")
    data = {
        "description": "提供专业的技术咨询和解决方案",
        "response_mode": "简洁",
        "additional_context": "熟悉最新技术趋势"
    }
    
    response = requests.put(f"{BASE_URL}/roles/{role_id}", json=data)
    pretty_print_response(response)

def test_list_roles():
    """测试列出角色API"""
    print("\n测试列出所有角色...")
    response = requests.get(f"{BASE_URL}/roles?limit=10&offset=0")
    pretty_print_response(response)

def test_search_roles(query):
    """测试搜索角色API"""
    print(f"\n测试搜索角色 (查询: {query})...")
    # 正确地编码查询参数
    encoded_query = urllib.parse.quote(query)
    response = requests.get(f"{BASE_URL}/search-roles?query={encoded_query}")
    pretty_print_response(response)

def test_delete_role(role_id):
    """测试删除角色API"""
    print(f"\n测试删除角色 (ID: {role_id})...")
    response = requests.delete(f"{BASE_URL}/roles/{role_id}")
    pretty_print_response(response)

def main():
    """主函数"""
    print("=" * 50)
    print("LLM角色管理API测试客户端")
    print("=" * 50)
    
    # 测试健康检查
    test_health_check()
    
    # 测试创建角色
    role_id = test_create_role()
    if not role_id:
        print("创建角色失败，无法继续测试!")
        return
    
    print(f"成功创建角色，ID: {role_id}")
    
    # 测试获取角色
    test_get_role(role_id)
    
    # 测试更新角色
    test_update_role(role_id)
    
    # 测试获取更新后的角色
    test_get_role(role_id)
    
    # 创建第二个角色用于测试
    data = {
        "name": "创意助手",
        "description": "提供创意建议和灵感",
        "role_type": "assistant",
        "language_style": "友好",
        "knowledge_domains": ["创意写作", "设计", "艺术"],
        "response_mode": "启发式"
    }
    
    response = requests.post(f"{BASE_URL}/roles", json=data)
    if response.status_code == 200 and response.json().get("success"):
        print("\n成功创建第二个角色")
    
    # 测试列出所有角色
    test_list_roles()
    
    # 测试搜索角色
    test_search_roles("技术")
    
    # 测试删除角色
    test_delete_role(role_id)
    
    # 确认删除结果
    test_get_role(role_id)
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 