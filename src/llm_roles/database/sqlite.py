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
            
            # 解析JSON属性并合并到角色对象
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