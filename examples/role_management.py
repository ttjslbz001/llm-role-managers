#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm_roles.core.role import Role
from src.llm_roles.database.sqlite import SQLiteDatabase
from src.llm_roles.services.role_manager import RoleManager
from src.llm_roles.api.role_api import RoleAPI


def print_response(response: Dict[str, Any]) -> None:
    """打印API响应，格式化JSON输出"""
    print("\n响应状态:", response.get('status'))
    print("消息:", response.get('message'))
    print("成功:", response.get('success'))
    
    if 'data' in response:
        print("\n数据:")
        # 格式化JSON输出
        formatted_data = json.dumps(response['data'], ensure_ascii=False, indent=2)
        print(formatted_data)
    print("-" * 50)


def main():
    # 初始化数据库
    db_path = project_root / "resource" / "db" / "llm_roles.db"
    db = SQLiteDatabase(str(db_path))
    
    # 确保数据库初始化
    if not db_path.exists():
        print("数据库不存在，请先运行初始化脚本: src/llm_roles/database/scripts/init_db.py")
        return
    
    # 初始化角色管理器
    role_manager = RoleManager(db)
    
    # 初始化角色API
    role_api = RoleAPI(role_manager)
    
    print("=" * 50)
    print("LLM角色管理演示")
    print("=" * 50)
    
    # 1. 创建角色示例
    print("\n1. 创建角色")
    create_data = {
        'name': '技术顾问',
        'description': '提供技术咨询和问题解决方案',
        'role_type': 'advisor',
        'language_style': '专业',
        'knowledge_domains': ['编程', '软件开发', '系统架构'],
        'response_mode': '详细',
        'allowed_topics': ['技术问题', '编程语言', '最佳实践'],
        'forbidden_topics': ['非技术话题', '个人信息'],
    }
    
    response = role_api.create_role(create_data)
    print_response(response)
    
    # 保存创建的角色ID用于后续操作
    if response['success']:
        role_id = response['data']['id']
        print(f"创建的角色ID: {role_id}")
    else:
        print("角色创建失败，无法继续演示")
        return
    
    # 2. 获取角色示例
    print("\n2. 获取角色")
    response = role_api.get_role(role_id)
    print_response(response)
    
    # 3. 更新角色示例
    print("\n3. 更新角色")
    update_data = {
        'description': '提供专业的技术咨询和问题解决方案',
        'response_mode': '简洁',
        'additional_context': '熟悉最新技术趋势'
    }
    
    response = role_api.update_role(role_id, update_data)
    print_response(response)
    
    # 4. 获取更新后的角色
    print("\n4. 获取更新后的角色")
    response = role_api.get_role(role_id)
    print_response(response)
    
    # 5. 创建第二个角色
    print("\n5. 创建第二个角色")
    create_data2 = {
        'name': '创意助手',
        'description': '提供创意建议和灵感',
        'role_type': 'assistant',
        'language_style': '友好',
        'knowledge_domains': ['创意写作', '设计', '艺术'],
        'response_mode': '启发式',
    }
    
    response = role_api.create_role(create_data2)
    print_response(response)
    
    # 6. 列出所有角色
    print("\n6. 列出所有角色")
    response = role_api.list_roles()
    print_response(response)
    
    # 7. 搜索角色
    print("\n7. 搜索角色 (关键词: 技术)")
    response = role_api.search_roles("技术")
    print_response(response)
    
    # 8. 删除角色示例
    print("\n8. 删除角色")
    response = role_api.delete_role(role_id)
    print_response(response)
    
    # 9. 确认删除结果
    print("\n9. 确认删除结果 (尝试获取已删除的角色)")
    response = role_api.get_role(role_id)
    print_response(response)
    
    print("\n演示完成!")


if __name__ == "__main__":
    main() 