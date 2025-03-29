#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class DatabaseBackend(ABC):
    """数据库后端抽象基类"""
    
    @abstractmethod
    def connect(self) -> None:
        """建立数据库连接"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    def create_role(self, role_data: Dict[str, Any]) -> str:
        """创建角色"""
        pass
    
    @abstractmethod
    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """获取角色"""
        pass
    
    @abstractmethod
    def update_role(self, role_id: str, role_data: Dict[str, Any]) -> bool:
        """更新角色"""
        pass
    
    @abstractmethod
    def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        pass
    
    @abstractmethod
    def list_roles(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """列出角色"""
        pass
    
    @abstractmethod
    def search_roles(self, query: str) -> List[Dict[str, Any]]:
        """搜索角色"""
        pass
    
    # 会话相关方法
    @abstractmethod
    def create_session(self, role_id: str, user_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建会话"""
        pass
    
    @abstractmethod
    def add_message(self, session_id: str, sender: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """添加消息"""
        pass
    
    @abstractmethod
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话消息"""
        pass 