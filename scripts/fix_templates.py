#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
import json
import uuid
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 确保数据库目录存在
db_dir = project_root / "resource" / "db"
db_path = db_dir / "llm_roles.db"

print(f"检查数据库：{db_path}")

if not db_path.exists():
    print(f"错误：数据库文件不存在，请先运行初始化脚本：python src/llm_roles/database/scripts/init_db.py")
    sys.exit(1)

# 创建数据库连接
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 创建一个修复后的模板
def create_fixed_template():
    print("创建修复后的提示词模板...")
    template_id = str(uuid.uuid4())
    
    # 模板内容使用正确的Mustache格式
    template_content = """你是一位名为{{{name}}}的{{{role_type}}}。

**角色描述**：{{{description}}}

**主要职责**：
- 提供{{{role_type}}}相关的专业帮助
- 使用{{{language_style}}}的沟通风格
- 确保回答专业且有帮助

{{#knowledge_domains}}
**知识领域**：{{{.}}}
{{/knowledge_domains}}

{{#allowed_topics}}
**可讨论的主题**：{{{.}}}
{{/allowed_topics}}

{{#forbidden_topics}}
**禁止讨论的主题**：{{{.}}}
{{/forbidden_topics}}

请始终保持友好和专业的态度，尽可能提供有价值的信息和建议。"""

    # 变量定义
    variables = [
        {"name": "name", "source": "name"},
        {"name": "role_type", "source": "role_type"},
        {"name": "description", "source": "description"},
        {"name": "language_style", "source": "language_style"},
        {"name": "knowledge_domains", "source": "knowledge_domains"},
        {"name": "allowed_topics", "source": "allowed_topics"},
        {"name": "forbidden_topics", "source": "forbidden_topics"}
    ]
    
    cursor.execute('''
    INSERT INTO prompt_templates 
    (id, name, description, format, is_default, template_content, variables, role_types) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        template_id,
        "修复后的助理模板",
        "适用于各种助理角色的修复后模板，支持变量替换",
        "openai",
        1,  # 设为默认模板
        template_content,
        json.dumps(variables),
        "assistant,advisor,helper"
    ))
    
    print(f"已创建修复后的模板，ID: {template_id}")
    return template_id

# 创建修复后的模板
template_id = create_fixed_template()

# 获取所有角色
cursor.execute("SELECT id FROM roles")
role_ids = [row[0] for row in cursor.fetchall()]

# 为每个角色设置默认模板
for role_id in role_ids:
    # 先删除现有的关联
    cursor.execute("DELETE FROM role_default_templates WHERE role_id = ?", (role_id,))
    
    # 添加新的关联
    cursor.execute('''
    INSERT INTO role_default_templates (role_id, template_id)
    VALUES (?, ?)
    ''', (role_id, template_id))
    
    print(f"为角色 {role_id} 设置了默认模板")

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"模板修复完成。现在可以使用提示词API生成正确的提示词了。") 