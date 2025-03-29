#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any

from ..core.role import Role
from ..database.base import DatabaseBackend


class RoleManager:
    """角色管理服务，提供角色的CRUD操作"""
    
    def __init__(self, db_backend: DatabaseBackend):
        """初始化角色管理器
        
        Args:
            db_backend: 数据库后端接口
        """
        self.db = db_backend
        
    def create_role(self, name: str, description: str = "", role_type: str = "", **attributes) -> Role:
        """创建新角色
        
        Args:
            name: 角色名称
            description: 角色描述
            role_type: 角色类型
            **attributes: 其他角色属性
            
        Returns:
            Role: 创建的角色对象
        """
        # 创建Role对象
        role = Role(name=name, description=description, role_type=role_type, **attributes)
        
        # 持久化到数据库
        role_dict = role.to_dict()
        role_id = self.db.create_role(role_dict)
        
        # 确保ID一致
        role.id = role_id
        
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """获取角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            Optional[Role]: 如果找到则返回角色对象，否则返回None
        """
        role_data = self.db.get_role(role_id)
        if not role_data:
            return None
            
        # 提取主要属性
        role_id = role_data.pop('id')
        name = role_data.pop('name')
        description = role_data.pop('description', '')
        role_type = role_data.pop('role_type', '')
        
        # 移除created_at和updated_at，这些会在Role初始化时自动生成
        role_data.pop('created_at', None)
        role_data.pop('updated_at', None)
        
        # 构建Role对象
        return Role(
            role_id=role_id,
            name=name, 
            description=description,
            role_type=role_type,
            **role_data
        )
    
    def update_role(self, role_id: str, **updates) -> Optional[Role]:
        """更新角色
        
        Args:
            role_id: 角色ID
            **updates: 要更新的字段
            
        Returns:
            Optional[Role]: 更新后的角色对象，如果角色不存在则返回None
        """
        # 获取现有角色
        role = self.get_role(role_id)
        if not role:
            return None
            
        # 更新基本属性
        if 'name' in updates:
            role.name = updates.pop('name')
        if 'description' in updates:
            role.description = updates.pop('description')
        if 'role_type' in updates:
            role.role_type = updates.pop('role_type')
            
        # 更新其他属性
        for key, value in updates.items():
            role.attributes[key] = value
            
        # 持久化到数据库
        self.db.update_role(role_id, role.to_dict())
        
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """删除角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            bool: 删除是否成功
        """
        return self.db.delete_role(role_id)
        
    def list_roles(self, limit: int = 100, offset: int = 0) -> List[Role]:
        """列出角色
        
        Args:
            limit: 返回的最大角色数量
            offset: 分页偏移量
            
        Returns:
            List[Role]: 角色对象列表
        """
        roles_data = self.db.list_roles(limit=limit, offset=offset)
        return [self._dict_to_role(role_data) for role_data in roles_data]
    
    def search_roles(self, query: str) -> List[Role]:
        """搜索角色
        
        Args:
            query: 搜索关键词
            
        Returns:
            List[Role]: 匹配的角色对象列表
        """
        roles_data = self.db.search_roles(query)
        return [self._dict_to_role(role_data) for role_data in roles_data]
        
    def _dict_to_role(self, role_data: Dict[str, Any]) -> Role:
        """将字典转换为Role对象
        
        Args:
            role_data: 角色数据字典
            
        Returns:
            Role: 角色对象
        """
        # 提取主要属性
        role_id = role_data.pop('id')
        name = role_data.pop('name')
        description = role_data.pop('description', '')
        role_type = role_data.pop('role_type', '')
        
        # 移除created_at和updated_at，这些会在Role初始化时自动生成
        role_data.pop('created_at', None)
        role_data.pop('updated_at', None)
        
        # 创建并返回Role对象
        return Role(
            role_id=role_id,
            name=name, 
            description=description,
            role_type=role_type,
            **role_data
        ) 