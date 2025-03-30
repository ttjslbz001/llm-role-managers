#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
from pathlib import Path

# 查找数据库文件
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resource', 'db', 'llm_roles.db')
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
    sys.exit(1)

# 新的模板内容 - 使用双花括号格式
new_template_content = '''你是一位名为{{name}}的{{role_type}}。

**角色描述**：{{description}}

**主要职责**：
- 提供{{role_type}}相关的专业帮助
- 使用{{language_style}}的沟通风格
- 确保回答专业且有帮助

{{#knowledge_domains}}
**知识领域**：{{.}}
{{/knowledge_domains}}

{{#allowed_topics}}
**可讨论的主题**：{{.}}
{{/allowed_topics}}

{{#forbidden_topics}}
**禁止讨论的主题**：{{.}}
{{/forbidden_topics}}

请始终保持友好和专业的态度，尽可能提供有价值的信息和建议。'''

# 目标模板ID
template_id = 'f793a2b9-4172-43d9-aea9-ddb79b3d06ab'

# 连接数据库并更新模板
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 更新模板内容
    cursor.execute('UPDATE prompt_templates SET template_content = ? WHERE id = ?', 
                   (new_template_content, template_id))
    conn.commit()
    
    # 验证更新是否成功
    cursor.execute('SELECT name, template_content FROM prompt_templates WHERE id = ?', (template_id,))
    result = cursor.fetchone()
    
    if result:
        print(f"模板 '{result[0]}' 更新成功!")
        print("模板内容:")
        print("-" * 40)
        print(result[1])
        print("-" * 40)
    else:
        print(f"未找到ID为 {template_id} 的模板")
        
except Exception as e:
    print(f"更新失败: {str(e)}")
    conn.rollback()
finally:
    conn.close() 