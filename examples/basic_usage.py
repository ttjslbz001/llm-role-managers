#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm_roles.core.role import Role
from src.llm_roles.database.sqlite import SQLiteDatabase

def main():
    # 初始化数据库
    db_path = project_root / "resource" / "db" / "llm_roles.db"
    db = SQLiteDatabase(str(db_path))
    
    # 确保数据库初始化
    if not db_path.exists():
        print("数据库不存在，请先运行初始化脚本: src/llm_roles/database/scripts/init_db.py")
        return
    
    # 创建一个测试角色
    test_role = Role(
        name="技术顾问",
        description="提供技术咨询和问题解决方案",
        role_type="advisor",
        language_style="专业",
        knowledge_domains=["编程", "软件开发", "系统架构"],
        response_mode="详细",
        allowed_topics=["技术问题", "编程语言", "最佳实践"],
        forbidden_topics=["非技术话题", "个人信息"],
    )
    
    # 输出角色信息
    print("创建角色:")
    print(f"ID: {test_role.id}")
    print(f"名称: {test_role.name}")
    print(f"描述: {test_role.description}")
    print(f"类型: {test_role.role_type}")
    print(f"属性: {test_role.attributes}")
    
    # 保存到数据库
    print("\n保存到数据库...")
    with db:
        role_id = db.create_role(test_role.to_dict())
        print(f"角色ID: {role_id}")
        
        # 查询角色
        print("\n从数据库查询角色:")
        role_data = db.get_role(role_id)
        if role_data:
            retrieved_role = Role.from_dict(role_data)
            print(f"查询到角色: {retrieved_role}")
            print(f"角色属性: {retrieved_role.attributes}")
            
            # 创建会话
            print("\n创建会话...")
            session_id = db.create_session(role_id)
            print(f"会话ID: {session_id}")
            
            # 添加消息
            print("\n添加消息...")
            user_msg_id = db.add_message(session_id, "user", "我需要帮助解决一个Python并发问题")
            print(f"用户消息ID: {user_msg_id}")
            
            asst_msg_id = db.add_message(session_id, "assistant", 
                                       "我能帮你解决Python并发问题。请提供更多关于你遇到的具体问题的信息。")
            print(f"助手消息ID: {asst_msg_id}")
            
            # 获取会话消息
            print("\n获取会话消息:")
            messages = db.get_session_messages(session_id)
            for i, msg in enumerate(messages, 1):
                print(f"{i}. [{msg['sender']}]: {msg['content']}")
        else:
            print(f"未找到角色: {role_id}")

if __name__ == "__main__":
    main() 