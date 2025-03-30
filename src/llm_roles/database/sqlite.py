#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class SQLiteDatabase:
    """SQLite数据库实现"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化SQLite数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为项目resource/db目录下的llm_roles.db
        """
        if db_path is None:
            # 默认数据库路径
            project_root = Path(__file__).parent.parent.parent.parent
            db_dir = project_root / "resource" / "db"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "llm_roles.db")
            
        self.db_path = db_path
        self.conn = None
        
    def connect(self) -> None:
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        # 启用外键约束
        self.conn.execute("PRAGMA foreign_keys = ON")
        # 配置连接返回Row对象
        self.conn.row_factory = sqlite3.Row
        print(f"Connected to database: {self.db_path}")
        
    def disconnect(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Database connection closed")
            
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    def create_role(self, role_data: Dict[str, Any]) -> str:
        """创建新角色
        
        Args:
            role_data: 角色数据字典
            
        Returns:
            str: 创建的角色ID
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        # 生成ID如果没有提供
        role_id = role_data.get('id', str(uuid.uuid4()))
        name = role_data.get('name', '')
        description = role_data.get('description', '')
        role_type = role_data.get('role_type', '')
        
        # 提取主要字段后，其余放入JSON属性
        attributes = {k: v for k, v in role_data.items() 
                    if k not in ('id', 'name', 'description', 'role_type')}
        
        try:
            cursor.execute("""
                INSERT INTO roles (id, name, description, role_type, attributes)
                VALUES (?, ?, ?, ?, ?)
            """, (role_id, name, description, role_type, json.dumps(attributes)))
            
            self.conn.commit()
            print(f"Created role: {role_id}")
            return role_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating role: {e}")
            raise
    
    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """获取角色信息
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色信息字典，如果不存在返回None
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, role_type, attributes
            FROM roles WHERE id = ?
        """, (role_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        # 构建完整角色对象
        role = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'role_type': row[3],
        }
        
        # 解析JSON属性并合并到角色对象
        attributes = json.loads(row[4])
        role.update(attributes)
        
        return role
    
    def update_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """更新角色信息
        
        Args:
            role_id: 角色ID
            role_data: 更新的角色数据
            
        Returns:
            是否成功更新
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        # 提取主要字段
        name = role_data.get('name')
        description = role_data.get('description')
        role_type = role_data.get('role_type')
        
        # 提取属性数据
        attributes = {k: v for k, v in role_data.items() 
                     if k not in ('id', 'name', 'description', 'role_type')}
        
        # 准备更新语句
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = ?")
            params.append(name)
            
        if description is not None:
            update_fields.append("description = ?")
            params.append(description)
            
        if role_type is not None:
            update_fields.append("role_type = ?")
            params.append(role_type)
            
        if attributes:
            update_fields.append("attributes = ?")
            params.append(json.dumps(attributes))
            
        if not update_fields:
            # 没有要更新的字段
            return False
            
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # 添加角色ID到参数列表
        params.append(role_id)
        
        # 执行更新
        try:
            cursor.execute(f"""
                UPDATE roles 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)
            
            if cursor.rowcount == 0:
                # 没有找到要更新的角色
                return False
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating role: {e}")
            raise
    
    def delete_role(self, role_id: str) -> bool:
        """删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            是否成功删除
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
            if cursor.rowcount == 0:
                # 没有找到要删除的角色
                return False
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting role: {e}")
            raise
    
    def list_roles(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """列出角色
        
        Args:
            limit: 返回的最大记录数
            offset: 偏移量
            
        Returns:
            角色列表
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, role_type, attributes
            FROM roles
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        roles = []
        for row in cursor.fetchall():
            role = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'role_type': row[3],
            }
            
            # 解析JSON属性并合并到结果中
            attributes = json.loads(row[4])
            role.update(attributes)
            
            roles.append(role)
            
        return roles
    
    def search_roles(self, query: str) -> List[Dict[str, Any]]:
        """搜索角色
        
        Args:
            query: 搜索关键词
            
        Returns:
            符合条件的角色列表
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        search_term = f"%{query}%"
        
        cursor.execute("""
            SELECT id, name, description, role_type, attributes
            FROM roles
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name
        """, (search_term, search_term))
        
        roles = []
        for row in cursor.fetchall():
            role = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'role_type': row[3],
            }
            
            # 解析JSON属性并合并到角色对象
            attributes = json.loads(row[4])
            role.update(attributes)
            roles.append(role)
            
        return roles
    
    def create_session(self, role_id: str, user_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建会话
        
        Args:
            role_id: 角色ID
            user_id: 用户ID
            metadata: 会话元数据
            
        Returns:
            会话ID
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        session_id = str(uuid.uuid4())
        
        # 默认空元数据
        if metadata is None:
            metadata = {}
            
        try:
            cursor.execute("""
                INSERT INTO sessions (id, role_id, user_id, metadata)
                VALUES (?, ?, ?, ?)
            """, (session_id, role_id, user_id, json.dumps(metadata)))
            
            self.conn.commit()
            return session_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating session: {e}")
            raise
    
    def add_message(self, session_id: str, sender: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """添加消息
        
        Args:
            session_id: 会话ID
            sender: 发送者 ('user' 或 'assistant')
            content: 消息内容
            metadata: 消息元数据
            
        Returns:
            消息ID
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        message_id = str(uuid.uuid4())
        
        # 默认空元数据
        if metadata is None:
            metadata = {}
            
        try:
            # 插入消息
            cursor.execute("""
                INSERT INTO messages (id, session_id, sender, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, session_id, sender, content, json.dumps(metadata)))
            
            # 更新会话最后活动时间
            cursor.execute("""
                UPDATE sessions
                SET last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (session_id,))
            
            self.conn.commit()
            return message_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding message: {e}")
            raise
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话消息
        
        Args:
            session_id: 会话ID
            
        Returns:
            消息列表
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, sender, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message = {
                'id': row[0],
                'sender': row[1],
                'content': row[2],
                'timestamp': row[3],
            }
            
            # 解析元数据
            metadata = json.loads(row[4])
            if metadata:
                message['metadata'] = metadata
                
            messages.append(message)
            
        return messages
    
    # =========== 提示词模板操作 ===========
    
    def create_template(self, template_data: Dict[str, Any]) -> str:
        """创建新提示词模板
        
        Args:
            template_data: 模板数据字典
            
        Returns:
            str: 创建的模板ID
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        # 生成ID如果没有提供
        template_id = template_data.get('id', str(uuid.uuid4()))
        name = template_data.get('name', '')
        description = template_data.get('description', '')
        format = template_data.get('format', 'openai')
        role_types = json.dumps(template_data.get('role_types', []))
        template_content = template_data.get('template_content', '')
        variables = json.dumps(template_data.get('variables', []))
        
        try:
            cursor.execute("""
                INSERT INTO prompt_templates (id, name, description, format, role_types, template_content, variables)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (template_id, name, description, format, role_types, template_content, variables))
            
            self.conn.commit()
            print(f"Created prompt template: {template_id}")
            return template_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating prompt template: {e}")
            raise
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取提示词模板信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板信息字典，如果不存在返回None
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, format, role_types, template_content, variables, created_at, updated_at
            FROM prompt_templates WHERE id = ?
        """, (template_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        # 安全解析JSON，确保空值或无效值时返回默认值
        def safe_json_loads(json_str, default=None):
            if not json_str:
                return default
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return default
            
        # 处理角色类型，如果是逗号分隔的字符串，转换为列表
        role_types = row[4]
        if role_types and isinstance(role_types, str) and ',' in role_types:
            role_types = [rt.strip() for rt in role_types.split(',')]
        else:
            role_types = safe_json_loads(role_types, [])
            
        # 构建完整模板对象
        template = {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'format': row[3] or 'openai',  # 默认格式
            'role_types': role_types,
            'template_content': row[5],
            'variables': safe_json_loads(row[6], []),
            'created_at': row[7],
            'updated_at': row[8]
        }
        
        return template
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """更新提示词模板信息
        
        Args:
            template_id: 模板ID
            template_data: 更新的模板数据
            
        Returns:
            是否成功更新
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        # 提取字段
        update_fields = []
        params = []
        
        # 处理各个可更新字段
        field_map = {
            'name': 'name',
            'description': 'description',
            'format': 'format',
            'role_types': 'role_types',
            'template_content': 'template_content',
            'variables': 'variables'
        }
        
        for key, field in field_map.items():
            if key in template_data:
                value = template_data[key]
                if key in ('role_types', 'variables') and value is not None:
                    value = json.dumps(value)
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            # 没有要更新的字段
            return False
            
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # 添加模板ID到参数列表
        params.append(template_id)
        
        # 执行更新
        try:
            cursor.execute(f"""
                UPDATE prompt_templates 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)
            
            if cursor.rowcount == 0:
                # 没有找到要更新的模板
                return False
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating prompt template: {e}")
            raise
    
    def delete_template(self, template_id: str) -> bool:
        """删除提示词模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否成功删除
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            # 先删除相关的角色默认模板关联
            cursor.execute("DELETE FROM role_default_templates WHERE template_id = ?", (template_id,))
            
            # 再删除模板本身
            cursor.execute("DELETE FROM prompt_templates WHERE id = ?", (template_id,))
            if cursor.rowcount == 0:
                # 没有找到要删除的模板
                self.conn.rollback()
                return False
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting prompt template: {e}")
            raise
    
    def list_templates(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """列出提示词模板
        
        Args:
            limit: 返回的最大记录数
            offset: 偏移量
            
        Returns:
            模板列表
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, description, format, role_types, template_content, variables, is_default, created_at, updated_at
            FROM prompt_templates
            ORDER BY name
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        templates = []
        for row in cursor.fetchall():
            # 安全解析JSON，确保空值或无效值时返回默认值
            def safe_json_loads(json_str, default=None):
                if not json_str:
                    return default
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return default
            
            # 处理角色类型，如果是逗号分隔的字符串，转换为列表
            role_types = row[4]
            if role_types and isinstance(role_types, str) and ',' in role_types:
                role_types = [rt.strip() for rt in role_types.split(',')]
            else:
                role_types = safe_json_loads(role_types, [])
            
            template = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'format': row[3] or 'openai',  # 默认格式
                'role_types': role_types,
                'template_content': row[5],
                'variables': safe_json_loads(row[6], []),
                'is_default': bool(row[7]),
                'created_at': row[8],
                'updated_at': row[9]
            }
            templates.append(template)
            
        return templates
    
    def set_role_default_template(self, role_id: str, template_id: str) -> bool:
        """设置角色的默认模板
        
        Args:
            role_id: 角色ID
            template_id: 模板ID
            
        Returns:
            是否成功设置
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            # 检查角色和模板是否存在
            cursor.execute("SELECT 1 FROM roles WHERE id = ?", (role_id,))
            if not cursor.fetchone():
                return False
                
            cursor.execute("SELECT 1 FROM prompt_templates WHERE id = ?", (template_id,))
            if not cursor.fetchone():
                return False
            
            # 检查是否已存在关联
            cursor.execute(
                "SELECT 1 FROM role_default_templates WHERE role_id = ? AND template_id = ?", 
                (role_id, template_id)
            )
            if cursor.fetchone():
                # 已经存在关联，视为成功
                return True
                
            # 添加关联
            cursor.execute("""
                INSERT INTO role_default_templates (role_id, template_id)
                VALUES (?, ?)
            """, (role_id, template_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error setting role default template: {e}")
            raise
    
    def remove_role_default_template(self, role_id: str, template_id: str) -> bool:
        """移除角色的默认模板
        
        Args:
            role_id: 角色ID
            template_id: 模板ID
            
        Returns:
            是否成功移除
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM role_default_templates 
                WHERE role_id = ? AND template_id = ?
            """, (role_id, template_id))
            
            if cursor.rowcount == 0:
                # 没有找到要删除的关联
                return False
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error removing role default template: {e}")
            raise
    
    def get_role_default_templates(self, role_id: str) -> List[Dict[str, Any]]:
        """获取角色的默认模板列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            模板列表
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pt.id, pt.name, pt.description, pt.format, pt.role_types, 
                   pt.template_content, pt.variables, pt.is_default, pt.created_at, pt.updated_at
            FROM prompt_templates pt
            JOIN role_default_templates rdt ON pt.id = rdt.template_id
            WHERE rdt.role_id = ?
            ORDER BY pt.name
        """, (role_id,))
        
        templates = []
        for row in cursor.fetchall():
            # 安全解析JSON，确保空值或无效值时返回默认值
            def safe_json_loads(json_str, default=None):
                if not json_str:
                    return default
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return default
            
            # 处理角色类型，如果是逗号分隔的字符串，转换为列表
            role_types = row[4]
            if role_types and isinstance(role_types, str) and ',' in role_types:
                role_types = [rt.strip() for rt in role_types.split(',')]
            else:
                role_types = safe_json_loads(role_types, [])
            
            template = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'format': row[3] or 'openai',  # 默认格式
                'role_types': role_types,
                'template_content': row[5],
                'variables': safe_json_loads(row[6], []),
                'is_default': bool(row[7]),
                'created_at': row[8],
                'updated_at': row[9]
            }
            templates.append(template)
            
        return templates 