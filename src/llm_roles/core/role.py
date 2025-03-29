#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

class Role:
    """LLM角色定义类"""
    
    def __init__(self, 
                name: str, 
                description: str = "",
                role_type: str = "",
                role_id: Optional[str] = None,
                **attributes):
        """初始化角色
        
        Args:
            name: 角色名称
            description: 角色描述
            role_type: 角色类型
            role_id: 角色ID，如果不提供则自动生成
            **attributes: 角色其他属性
        """
        self.id = role_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.role_type = role_type
        self.attributes = attributes
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        
    def to_dict(self) -> Dict[str, Any]:
        """将角色转换为字典
        
        Returns:
            角色字典表示
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'role_type': self.role_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        # 添加其他属性
        result.update(self.attributes)
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """从字典创建角色
        
        Args:
            data: 角色数据字典
            
        Returns:
            创建的角色对象
        """
        # 提取基本属性
        role_id = data.get('id')
        name = data.get('name', '')
        description = data.get('description', '')
        role_type = data.get('role_type', '')
        
        # 提取其他属性
        attributes = {k: v for k, v in data.items() 
                     if k not in ('id', 'name', 'description', 'role_type', 'created_at', 'updated_at')}
        
        # 创建角色
        role = cls(name=name, description=description, role_type=role_type, 
                  role_id=role_id, **attributes)
        
        # 设置时间戳（如果有）
        if 'created_at' in data:
            try:
                role.created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
                
        if 'updated_at' in data:
            try:
                role.updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                pass
                
        return role
    
    def update(self, **kwargs) -> None:
        """更新角色属性
        
        Args:
            **kwargs: 要更新的属性
        """
        for key, value in kwargs.items():
            if key == 'name':
                self.name = value
            elif key == 'description':
                self.description = value
            elif key == 'role_type':
                self.role_type = value
            else:
                self.attributes[key] = value
                
        self.updated_at = datetime.now()
        
    def __str__(self) -> str:
        """角色字符串表示"""
        return f"Role({self.name}: {self.description})"
    
    def __repr__(self) -> str:
        """角色表示"""
        return f"Role(id={self.id}, name={self.name}, type={self.role_type})" 