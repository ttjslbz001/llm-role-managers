#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import json
from src.llm_roles.core.prompt_template import PromptTemplate


class TestPromptTemplate(unittest.TestCase):
    """提示词模板单元测试"""
    
    def test_init(self):
        """测试模板初始化"""
        template = PromptTemplate(
            name="测试模板",
            template_content="你好，{role.name}",
            format="openai",
            description="测试描述",
            role_types=["test"],
            variables=[{"name": "role.name", "source": "name"}]
        )
        
        self.assertEqual(template.name, "测试模板")
        self.assertEqual(template.template_content, "你好，{role.name}")
        self.assertEqual(template.format, "openai")
        self.assertEqual(template.description, "测试描述")
        self.assertEqual(template.role_types, ["test"])
        self.assertEqual(len(template.variables), 1)
        self.assertEqual(template.variables[0]["name"], "role.name")
        self.assertEqual(template.variables[0]["source"], "name")
        self.assertIsInstance(template.id, str)
        self.assertIsInstance(template.created_at, datetime)
        self.assertIsInstance(template.updated_at, datetime)
    
    def test_to_dict(self):
        """测试转换为字典"""
        template = PromptTemplate(
            name="测试模板",
            template_content="你好，{role.name}",
            template_id="test-id"
        )
        
        template_dict = template.to_dict()
        
        self.assertEqual(template_dict["id"], "test-id")
        self.assertEqual(template_dict["name"], "测试模板")
        self.assertEqual(template_dict["template_content"], "你好，{role.name}")
        self.assertEqual(template_dict["format"], "openai")
        self.assertIsInstance(template_dict["created_at"], str)
        self.assertIsInstance(template_dict["updated_at"], str)
    
    def test_from_dict(self):
        """测试从字典创建模板"""
        template_dict = {
            "id": "test-id",
            "name": "测试模板",
            "description": "测试描述",
            "format": "openai",
            "role_types": ["test"],
            "template_content": "你好，{role.name}",
            "variables": [{"name": "role.name", "source": "name"}],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        template = PromptTemplate.from_dict(template_dict)
        
        self.assertEqual(template.id, "test-id")
        self.assertEqual(template.name, "测试模板")
        self.assertEqual(template.description, "测试描述")
        self.assertEqual(template.format, "openai")
        self.assertEqual(template.role_types, ["test"])
        self.assertEqual(template.template_content, "你好，{role.name}")
        self.assertEqual(len(template.variables), 1)
        self.assertEqual(template.variables[0]["name"], "role.name")
    
    def test_update(self):
        """测试更新模板属性"""
        template = PromptTemplate(
            name="原名称",
            template_content="原内容",
            description="原描述"
        )
        
        template.update(
            name="新名称",
            description="新描述",
            template_content="新内容"
        )
        
        self.assertEqual(template.name, "新名称")
        self.assertEqual(template.description, "新描述")
        self.assertEqual(template.template_content, "新内容")
    
    def test_get_variable_names(self):
        """测试获取模板变量名集合"""
        template = PromptTemplate(
            name="测试模板",
            template_content="Hello, {name}! You are a {role}.",
            variables=[
                {"name": "name", "source": "role.name"},
                {"name": "role", "source": "role_type"}
            ]
        )
        
        variable_names = template.get_variable_names()
        
        self.assertEqual(len(variable_names), 2)
        self.assertIn("name", variable_names)
        self.assertIn("role", variable_names)
    
    def test_render_basic(self):
        """测试基本渲染功能"""
        template = PromptTemplate(
            name="测试模板",
            template_content="你好，{role.name}！你是{role.type}。",
            variables=[
                {"name": "role.name", "source": "name"},
                {"name": "role.type", "source": "role_type"}
            ]
        )
        
        role_data = {
            "name": "助手",
            "role_type": "聊天机器人"
        }
        
        rendered = template.render(role_data)
        
        self.assertEqual(rendered, "你好，助手！你是聊天机器人。")
    
    def test_render_with_custom_vars(self):
        """测试带自定义变量的渲染"""
        template = PromptTemplate(
            name="测试模板",
            template_content="你好，{role.name}！今天是{date}。",
            variables=[
                {"name": "role.name", "source": "name"}
            ]
        )
        
        role_data = {"name": "助手"}
        custom_vars = {"date": "2023-01-01"}
        
        rendered = template.render(role_data, custom_vars)
        
        self.assertEqual(rendered, "你好，助手！今天是2023-01-01。")
    
    def test_render_with_nested_source(self):
        """测试带嵌套源的渲染"""
        template = PromptTemplate(
            name="测试模板",
            template_content="风格: {style}",
            variables=[
                {"name": "style", "source": "attributes.language_style"}
            ]
        )
        
        role_data = {
            "name": "助手",
            "attributes": {
                "language_style": "专业"
            }
        }
        
        rendered = template.render(role_data)
        
        self.assertEqual(rendered, "风格: 专业")
    
    def test_render_with_list(self):
        """测试带列表的渲染"""
        template = PromptTemplate(
            name="测试模板",
            template_content="知识领域: {domains}",
            variables=[
                {"name": "domains", "source": "knowledge_domains"}
            ]
        )
        
        role_data = {
            "knowledge_domains": ["科学", "技术", "工程", "数学"]
        }
        
        rendered = template.render(role_data)
        
        self.assertEqual(rendered, "知识领域: 科学, 技术, 工程, 数学")
    
    def test_string_representation(self):
        """测试字符串表示"""
        template = PromptTemplate(
            name="测试模板",
            description="测试描述",
            template_id="test-id"
        )
        
        self.assertIn("测试模板", str(template))
        self.assertIn("测试描述", str(template))
        self.assertIn("test-id", repr(template))
        self.assertIn("测试模板", repr(template))


if __name__ == "__main__":
    unittest.main() 