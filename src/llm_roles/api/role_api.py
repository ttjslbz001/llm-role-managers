#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional
from http import HTTPStatus

from ..services.role_manager import RoleManager
from ..core.role import Role


class RoleAPI:
    """角色管理API"""
    
    def __init__(self, role_manager: RoleManager):
        """初始化角色API
        
        Args:
            role_manager: 角色管理服务
        """
        self.manager = role_manager
        
    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建角色API
        
        Args:
            role_data: 角色数据，必须包含name字段
            
        Returns:
            Dict[str, Any]: 包含创建结果的响应
            
        Raises:
            ValueError: 如果缺少必要字段
        """
        # 验证必要字段
        if 'name' not in role_data:
            return {
                'status': HTTPStatus.BAD_REQUEST,
                'message': '缺少必要字段: name',
                'success': False
            }
            
        # 提取主要字段
        name = role_data.pop('name')
        description = role_data.pop('description', '')
        role_type = role_data.pop('role_type', '')
        
        try:
            # 创建角色
            role = self.manager.create_role(
                name=name,
                description=description,
                role_type=role_type,
                **role_data
            )
            
            # 返回创建结果
            return {
                'status': HTTPStatus.CREATED,
                'message': '角色创建成功',
                'success': True,
                'data': role.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'角色创建失败: {str(e)}',
                'success': False
            }
        
    def get_role(self, role_id: str) -> Dict[str, Any]:
        """获取角色API
        
        Args:
            role_id: 角色ID
            
        Returns:
            Dict[str, Any]: 包含角色数据的响应
        """
        try:
            role = self.manager.get_role(role_id)
            
            if not role:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'角色不存在: {role_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '获取角色成功',
                'success': True,
                'data': role.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'获取角色失败: {str(e)}',
                'success': False
            }
        
    def update_role(self, role_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新角色API
        
        Args:
            role_id: 角色ID
            updates: 要更新的字段
            
        Returns:
            Dict[str, Any]: 包含更新结果的响应
        """
        try:
            updated_role = self.manager.update_role(role_id, **updates)
            
            if not updated_role:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'角色不存在: {role_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '角色更新成功',
                'success': True,
                'data': updated_role.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'角色更新失败: {str(e)}',
                'success': False
            }
        
    def delete_role(self, role_id: str) -> Dict[str, Any]:
        """删除角色API
        
        Args:
            role_id: 角色ID
            
        Returns:
            Dict[str, Any]: 包含删除结果的响应
        """
        try:
            success = self.manager.delete_role(role_id)
            
            if not success:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'角色不存在或删除失败: {role_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '角色删除成功',
                'success': True
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'角色删除失败: {str(e)}',
                'success': False
            }
        
    def list_roles(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """列出角色API
        
        Args:
            limit: 返回的最大角色数量
            offset: 分页偏移量
            
        Returns:
            Dict[str, Any]: 包含角色列表的响应
        """
        try:
            roles = self.manager.list_roles(limit=limit, offset=offset)
            
            return {
                'status': HTTPStatus.OK,
                'message': '获取角色列表成功',
                'success': True,
                'data': {
                    'roles': [role.to_dict() for role in roles],
                    'count': len(roles),
                    'limit': limit,
                    'offset': offset
                }
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'获取角色列表失败: {str(e)}',
                'success': False
            }
        
    def search_roles(self, query: str) -> Dict[str, Any]:
        """搜索角色API
        
        Args:
            query: 搜索关键词
            
        Returns:
            Dict[str, Any]: 包含搜索结果的响应
        """
        try:
            roles = self.manager.search_roles(query)
            
            return {
                'status': HTTPStatus.OK,
                'message': '搜索角色成功',
                'success': True,
                'data': {
                    'roles': [role.to_dict() for role in roles],
                    'count': len(roles),
                    'query': query
                }
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'搜索角色失败: {str(e)}',
                'success': False
            } 