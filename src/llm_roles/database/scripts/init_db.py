#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 确保数据库目录存在
db_dir = project_root / "resource" / "db"
db_dir.mkdir(parents=True, exist_ok=True)

# 数据库文件路径
db_path = db_dir / "llm_roles.db"

# 创建数据库连接
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 创建角色表
cursor.execute('''
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    role_type TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attributes JSON NOT NULL
)
''')

# 创建角色历史版本表
cursor.execute('''
CREATE TABLE IF NOT EXISTS role_versions (
    version_id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    attributes JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
)
''')

# 创建会话表
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    user_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (role_id) REFERENCES roles(id)
)
''')

# 创建消息表
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
)
''')

# 创建提示词模板表
cursor.execute('''
CREATE TABLE IF NOT EXISTS prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    format TEXT NOT NULL,
    role_types TEXT,
    template_content TEXT NOT NULL,
    variables JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
''')

# 创建角色默认模板关联表
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

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"数据库初始化完成: {db_path}") 