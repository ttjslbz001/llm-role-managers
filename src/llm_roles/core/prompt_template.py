#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Set
import re

class PromptTemplate:
    """提示词模板类，用于存储和管理提示词模板"""
    
    def __init__(self, 
                name: str, 
                template_content: str,
                format: str = "openai",
                description: str = "",
                role_types: Optional[List[str]] = None,
                variables: Optional[List[Dict[str, Any]]] = None,
                template_id: Optional[str] = None):
        """初始化提示词模板
        
        Args:
            name: 模板名称
            template_content: 模板内容，包含变量占位符
            format: 提示词格式，默认为openai
            description: 模板描述
            role_types: 适用的角色类型列表
            variables: 模板变量列表，每个变量为一个字典
            template_id: 模板ID，如果不提供则自动生成
        """
        self.id = template_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.format = format
        self.role_types = role_types or []
        self.template_content = template_content
        self.variables = variables or []
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """将模板转换为字典
        
        Returns:
            模板字典表示
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'format': self.format,
            'role_types': self.role_types,
            'template_content': self.template_content,
            'variables': self.variables,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """从字典创建模板
        
        Args:
            data: 模板数据字典
            
        Returns:
            创建的模板对象
        """
        # 提取基本属性
        template_id = data.get('id')
        name = data.get('name', '')
        description = data.get('description', '')
        format = data.get('format', 'openai')
        role_types = data.get('role_types', [])
        template_content = data.get('template_content', '')
        variables = data.get('variables', [])
        
        # 创建模板
        template = cls(
            name=name,
            template_content=template_content,
            format=format,
            description=description,
            role_types=role_types,
            variables=variables,
            template_id=template_id
        )
        
        # 设置时间戳（如果有）
        if 'created_at' in data:
            try:
                template.created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                pass
                
        if 'updated_at' in data:
            try:
                template.updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                pass
                
        return template
    
    def update(self, **kwargs) -> None:
        """更新模板属性
        
        Args:
            **kwargs: 要更新的属性
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
                
        self.updated_at = datetime.now()
    
    def get_variable_names(self) -> Set[str]:
        """获取模板中的所有变量名
        
        Returns:
            变量名集合
        """
        return {var['name'] for var in self.variables if 'name' in var}
    
    def render(self, role_data: Dict[str, Any], custom_vars: Optional[Dict[str, Any]] = None) -> str:
        """根据角色数据渲染提示词
        
        Args:
            role_data: 角色数据
            custom_vars: 自定义变量值
            
        Returns:
            渲染后的提示词
        """
        content = self.template_content
        merged_vars = {}
        
        # 从角色数据中提取变量值
        for var in self.variables:
            var_name = var.get('name')
            var_source = var.get('source', '')
            
            if not var_name:
                continue
                
            # 处理嵌套属性路径，如role.attributes.language_style
            if '.' in var_source:
                parts = var_source.split('.')
                value = role_data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
            else:
                value = role_data.get(var_source, None)
                
            if value is not None:
                merged_vars[var_name] = value
        
        # 合并自定义变量
        if custom_vars:
            merged_vars.update(custom_vars)
            
        # 应用变量替换 - 支持多种格式: {{{variable}}}, {{variable}} 和 {variable}
        for var_name, value in merged_vars.items():
            # 处理 {{{variable}}} 格式 (三重花括号)
            triple_mustache = f"{{{{{{{var_name}}}}}}}"
            # 处理 {{variable}} 格式 (双重花括号)
            double_mustache = f"{{{{{var_name}}}}}"
            # 处理 {variable} 格式 (单个花括号)
            standard_placeholder = f"{{{var_name}}}"
            
            # 列表特殊处理，转换为逗号分隔的字符串
            str_value = str(value)
            if isinstance(value, list):
                str_value = ", ".join(str(item) for item in value)
                
            # 替换所有格式的占位符
            content = content.replace(triple_mustache, str_value)
            content = content.replace(double_mustache, str_value)
            content = content.replace(standard_placeholder, str_value)
            
        # 支持Mustache的列表迭代 {{#list_var}} ... {{/list_var}}
        for var_name, value in merged_vars.items():
            if isinstance(value, list):
                # 查找模式 {{#var_name}}...{{/var_name}}
                pattern = f"{{{{#{var_name}}}}}(.*?){{{{/{var_name}}}}}"
                matches = re.finditer(pattern, content, re.DOTALL)
                
                for match in matches:
                    full_match = match.group(0)
                    template_part = match.group(1)
                    
                    # 为列表中的每个项目渲染模板部分
                    rendered_items = []
                    for item in value:
                        # 替换 {{{.}}} 为当前项
                        item_content = template_part.replace("{{{.}}}", str(item))
                        # 也处理 {{.}} 格式
                        item_content = item_content.replace("{{.}}", str(item))
                        rendered_items.append(item_content)
                    
                    # 替换整个匹配部分
                    content = content.replace(full_match, "".join(rendered_items))
            
        return content
        
    def __str__(self) -> str:
        """模板字符串表示"""
        return f"PromptTemplate({self.name}: {self.description})"
    
    def __repr__(self) -> str:
        """模板表示"""
        return f"PromptTemplate(id={self.id}, name={self.name}, format={self.format})" 