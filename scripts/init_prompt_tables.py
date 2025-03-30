#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
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

# 检查prompt_templates表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompt_templates'")
if cursor.fetchone() is None:
    print("创建提示词模板表 (prompt_templates)...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompt_templates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        format TEXT,
        is_default BOOLEAN DEFAULT 0,
        role_types TEXT,
        template_content TEXT NOT NULL,
        variables JSON,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    ''')
else:
    print("提示词模板表 (prompt_templates) 已存在")

# 检查role_default_templates表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='role_default_templates'")
if cursor.fetchone() is None:
    print("创建角色默认模板关联表 (role_default_templates)...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS role_default_templates (
        role_id TEXT NOT NULL,
        template_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (role_id, template_id),
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (template_id) REFERENCES prompt_templates(id)
    )
    ''')
else:
    print("角色默认模板关联表 (role_default_templates) 已存在")

# 创建示例模板
def insert_example_template():
    cursor.execute("SELECT COUNT(*) FROM prompt_templates")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("添加示例提示词模板...")
        import uuid
        import json
        template_id = str(uuid.uuid4())
        
        cursor.execute('''
        INSERT INTO prompt_templates 
        (id, name, description, format, is_default, template_content, variables, role_types) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            template_id,
            "基础系统提示词模板",
            "通用的系统提示词模板，适用于大多数角色",
            "openai",
            1,  # 设为默认模板
            "你是{{name}}，一个{{role_type}}。你的职责是{{description}}。\n\n使用{{language_style}}的语言风格。\n\n{{#knowledge_domains}}你精通以下领域：{{.}}。{{/knowledge_domains}}\n\n{{#allowed_topics}}你可以讨论：{{.}}。{{/allowed_topics}}\n\n{{#forbidden_topics}}不要讨论：{{.}}。{{/forbidden_topics}}",
            json.dumps([
                {"name": "name", "source": "name"},
                {"name": "role_type", "source": "role_type"},
                {"name": "description", "source": "description"},
                {"name": "language_style", "source": "language_style"},
                {"name": "knowledge_domains", "source": "knowledge_domains"},
                {"name": "allowed_topics", "source": "allowed_topics"},
                {"name": "forbidden_topics", "source": "forbidden_topics"}
            ]),
            "assistant,advisor,expert"
        ))
        
        print(f"已创建示例模板，ID: {template_id}")
    else:
        print("数据库中已有提示词模板，跳过添加示例模板")

# 添加示例模板
insert_example_template()

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"数据库表初始化完成。现在可以使用提示词模板API了。") 