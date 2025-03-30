#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Any, Optional
from http import HTTPStatus

from ..services.prompt_service import PromptService
from ..core.prompt_template import PromptTemplate


class PromptAPI:
    """提示词管理API"""
    
    def __init__(self, prompt_service: PromptService):
        """初始化提示词API
        
        Args:
            prompt_service: 提示词服务
        """
        self.service = prompt_service
        
    def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建提示词模板API
        
        Args:
            template_data: 模板数据，必须包含name和template_content字段
            
        Returns:
            Dict[str, Any]: 包含创建结果的响应
        """
        # 验证必要字段
        if 'name' not in template_data or 'template_content' not in template_data:
            return {
                'status': HTTPStatus.BAD_REQUEST,
                'message': '缺少必要字段: name, template_content',
                'success': False
            }
            
        try:
            # 创建模板
            template = self.service.create_template(template_data)
            
            # 返回创建结果
            return {
                'status': HTTPStatus.CREATED,
                'message': '提示词模板创建成功',
                'success': True,
                'data': template.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'提示词模板创建失败: {str(e)}',
                'success': False
            }
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """获取提示词模板API
        
        Args:
            template_id: 模板ID
            
        Returns:
            Dict[str, Any]: 包含模板数据的响应
        """
        try:
            template = self.service.get_template(template_id)
            
            if not template:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'提示词模板不存在: {template_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '获取提示词模板成功',
                'success': True,
                'data': template.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'获取提示词模板失败: {str(e)}',
                'success': False
            }
    
    def update_template(self, template_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新提示词模板API
        
        Args:
            template_id: 模板ID
            updates: 要更新的字段
            
        Returns:
            Dict[str, Any]: 包含更新结果的响应
        """
        try:
            updated_template = self.service.update_template(template_id, **updates)
            
            if not updated_template:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'提示词模板不存在或不可修改: {template_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '提示词模板更新成功',
                'success': True,
                'data': updated_template.to_dict()
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'提示词模板更新失败: {str(e)}',
                'success': False
            }
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """删除提示词模板API
        
        Args:
            template_id: 模板ID
            
        Returns:
            Dict[str, Any]: 包含删除结果的响应
        """
        try:
            success = self.service.delete_template(template_id)
            
            if not success:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'提示词模板不存在、不可删除或删除失败: {template_id}',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '提示词模板删除成功',
                'success': True
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'提示词模板删除失败: {str(e)}',
                'success': False
            }
    
    def list_templates(self, include_defaults: bool = True, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """列出提示词模板API
        
        Args:
            include_defaults: 是否包含默认模板
            limit: 返回的最大模板数量
            offset: 分页偏移量
            
        Returns:
            Dict[str, Any]: 包含模板列表的响应
        """
        try:
            templates = self.service.list_templates(
                include_defaults=include_defaults,
                limit=limit,
                offset=offset
            )
            
            return {
                'status': HTTPStatus.OK,
                'message': '获取提示词模板列表成功',
                'success': True,
                'data': {
                    'templates': [template.to_dict() for template in templates],
                    'count': len(templates),
                    'limit': limit,
                    'offset': offset
                }
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'获取提示词模板列表失败: {str(e)}',
                'success': False
            }
    
    def generate_prompt(self, role_id: str, format: str = "openai", 
                        prompt_type: str = "complete", template_id: Optional[str] = None,
                        custom_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成角色提示词API
        
        Args:
            role_id: 角色ID
            format: 提示词格式
            prompt_type: 提示词类型
            template_id: 模板ID
            custom_vars: 自定义变量
            
        Returns:
            Dict[str, Any]: 包含生成的提示词的响应
        """
        try:
            result = self.service.generate_prompt(
                role_id=role_id,
                format=format,
                prompt_type=prompt_type,
                template_id=template_id,
                custom_vars=custom_vars
            )
            
            return {
                'status': HTTPStatus.OK,
                'message': '提示词生成成功',
                'success': True,
                'data': result
            }
        except ValueError as e:
            return {
                'status': HTTPStatus.NOT_FOUND,
                'message': str(e),
                'success': False
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'提示词生成失败: {str(e)}',
                'success': False
            }
    
    def preview_prompt(self, role_id: str, template_id: str, format: str = "openai",
                      prompt_type: str = "complete", custom_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """预览角色使用特定模板的提示词API
        
        Args:
            role_id: 角色ID
            template_id: 模板ID
            format: 提示词格式
            prompt_type: 提示词类型
            custom_vars: 自定义变量
            
        Returns:
            Dict[str, Any]: 包含预览的提示词的响应
        """
        try:
            result = self.service.preview_prompt(
                role_id=role_id,
                template_id=template_id,
                format=format,
                prompt_type=prompt_type,
                custom_vars=custom_vars
            )
            
            return {
                'status': HTTPStatus.OK,
                'message': '提示词预览成功',
                'success': True,
                'data': result
            }
        except ValueError as e:
            return {
                'status': HTTPStatus.NOT_FOUND,
                'message': str(e),
                'success': False
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'提示词预览失败: {str(e)}',
                'success': False
            }
    
    def set_role_default_template(self, role_id: str, template_id: str) -> Dict[str, Any]:
        """设置角色默认模板API
        
        Args:
            role_id: 角色ID
            template_id: 模板ID
            
        Returns:
            Dict[str, Any]: 包含设置结果的响应
        """
        try:
            success = self.service.set_role_default_template(role_id, template_id)
            
            if not success:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'角色或模板不存在，或设置失败',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '设置角色默认模板成功',
                'success': True
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'设置角色默认模板失败: {str(e)}',
                'success': False
            }
    
    def remove_role_default_template(self, role_id: str, template_id: str) -> Dict[str, Any]:
        """移除角色默认模板API
        
        Args:
            role_id: 角色ID
            template_id: 模板ID
            
        Returns:
            Dict[str, Any]: 包含移除结果的响应
        """
        try:
            success = self.service.remove_role_default_template(role_id, template_id)
            
            if not success:
                return {
                    'status': HTTPStatus.NOT_FOUND,
                    'message': f'角色默认模板不存在或移除失败',
                    'success': False
                }
                
            return {
                'status': HTTPStatus.OK,
                'message': '移除角色默认模板成功',
                'success': True
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'移除角色默认模板失败: {str(e)}',
                'success': False
            }
    
    def get_role_default_templates(self, role_id: str) -> Dict[str, Any]:
        """获取角色默认模板列表API
        
        Args:
            role_id: 角色ID
            
        Returns:
            Dict[str, Any]: 包含模板列表的响应
        """
        try:
            templates = self.service.get_role_default_templates(role_id)
            
            return {
                'status': HTTPStatus.OK,
                'message': '获取角色默认模板列表成功',
                'success': True,
                'data': {
                    'templates': [template.to_dict() for template in templates],
                    'count': len(templates),
                    'role_id': role_id
                }
            }
        except Exception as e:
            return {
                'status': HTTPStatus.INTERNAL_SERVER_ERROR,
                'message': f'获取角色默认模板列表失败: {str(e)}',
                'success': False
            } 