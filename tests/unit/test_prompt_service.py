#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock, patch
from src.llm_roles.services.prompt_service import PromptService
from src.llm_roles.core.prompt_template import PromptTemplate


class TestPromptService(unittest.TestCase):
    """提示词服务单元测试"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建一个Mock数据库后端
        self.mock_db = MagicMock()
        self.service = PromptService(self.mock_db)
        
        # 备份原始的默认模板加载方法
        self.original_load_default_templates = self.service._load_default_templates
        # 替换为返回测试模板的版本
        self.service._load_default_templates = self._mock_load_default_templates
        self.service._default_templates = self._mock_load_default_templates()
    
    def tearDown(self):
        """测试后的清理"""
        # 恢复原始方法
        self.service._load_default_templates = self.original_load_default_templates
    
    def _mock_load_default_templates(self):
        """返回测试用的默认模板字典"""
        templates = {}
        
        # 测试默认模板
        test_template = PromptTemplate(
            template_id="default-template-id",
            name="默认测试模板",
            description="测试用默认模板",
            template_content="你好，{role.name}",
            variables=[{"name": "role.name", "source": "name"}]
        )
        templates[test_template.id] = test_template
        
        # 带角色类型的测试模板
        typed_template = PromptTemplate(
            template_id="typed-template-id",
            name="有类型的测试模板",
            description="测试用类型模板",
            role_types=["test_type"],
            template_content="你好，{role.name}，你是{role.type}",
            variables=[
                {"name": "role.name", "source": "name"},
                {"name": "role.type", "source": "role_type"}
            ]
        )
        templates[typed_template.id] = typed_template
        
        return templates
    
    def test_create_template(self):
        """测试创建模板"""
        # 准备
        template_data = {
            "name": "测试模板",
            "template_content": "测试内容",
            "description": "测试描述"
        }
        self.mock_db.create_template.return_value = "test-id"
        
        # 执行
        template = self.service.create_template(template_data)
        
        # 验证
        self.mock_db.create_template.assert_called_once()
        self.assertEqual(template.name, "测试模板")
        self.assertEqual(template.template_content, "测试内容")
        self.assertEqual(template.description, "测试描述")
        self.assertEqual(template.id, "test-id")
    
    def test_get_template_default(self):
        """测试获取默认模板"""
        # 执行
        template = self.service.get_template("default-template-id")
        
        # 验证
        self.assertEqual(template.id, "default-template-id")
        self.assertEqual(template.name, "默认测试模板")
        # 验证没有调用数据库
        self.mock_db.get_template.assert_not_called()
    
    def test_get_template_custom(self):
        """测试获取自定义模板"""
        # 准备
        self.mock_db.get_template.return_value = {
            "id": "custom-id",
            "name": "自定义模板",
            "description": "自定义描述",
            "format": "openai",
            "role_types": [],
            "template_content": "自定义内容",
            "variables": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        # 执行
        template = self.service.get_template("custom-id")
        
        # 验证
        self.mock_db.get_template.assert_called_once_with("custom-id")
        self.assertEqual(template.id, "custom-id")
        self.assertEqual(template.name, "自定义模板")
        self.assertEqual(template.template_content, "自定义内容")
    
    def test_get_template_not_found(self):
        """测试获取不存在的模板"""
        # 准备
        self.mock_db.get_template.return_value = None
        
        # 执行
        template = self.service.get_template("non-existent-id")
        
        # 验证
        self.mock_db.get_template.assert_called_once_with("non-existent-id")
        self.assertIsNone(template)
    
    def test_update_template(self):
        """测试更新模板"""
        # 准备
        template_id = "custom-id"
        self.mock_db.get_template.return_value = {
            "id": template_id,
            "name": "原名称",
            "description": "原描述",
            "format": "openai",
            "role_types": [],
            "template_content": "原内容",
            "variables": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        self.mock_db.update_template.return_value = True
        
        # 执行
        updated_template = self.service.update_template(
            template_id,
            name="新名称",
            description="新描述",
            template_content="新内容"
        )
        
        # 验证
        self.mock_db.get_template.assert_called_once_with(template_id)
        self.mock_db.update_template.assert_called_once()
        self.assertEqual(updated_template.name, "新名称")
        self.assertEqual(updated_template.description, "新描述")
        self.assertEqual(updated_template.template_content, "新内容")
    
    def test_update_template_not_found(self):
        """测试更新不存在的模板"""
        # 准备
        self.mock_db.get_template.return_value = None
        
        # 执行
        result = self.service.update_template("non-existent-id", name="新名称")
        
        # 验证
        self.mock_db.get_template.assert_called_once_with("non-existent-id")
        self.mock_db.update_template.assert_not_called()
        self.assertIsNone(result)
    
    def test_update_default_template(self):
        """测试更新默认模板"""
        # 执行
        result = self.service.update_template("default-template-id", name="新名称")
        
        # 验证
        self.mock_db.get_template.assert_not_called()
        self.mock_db.update_template.assert_not_called()
        self.assertIsNone(result)
    
    def test_delete_template(self):
        """测试删除模板"""
        # 准备
        self.mock_db.delete_template.return_value = True
        
        # 执行
        result = self.service.delete_template("custom-id")
        
        # 验证
        self.mock_db.delete_template.assert_called_once_with("custom-id")
        self.assertTrue(result)
    
    def test_delete_default_template(self):
        """测试删除默认模板"""
        # 执行
        result = self.service.delete_template("default-template-id")
        
        # 验证
        self.mock_db.delete_template.assert_not_called()
        self.assertFalse(result)
    
    def test_list_templates(self):
        """测试列出模板"""
        # 准备
        self.mock_db.list_templates.return_value = [
            {
                "id": "custom-id-1",
                "name": "自定义模板1",
                "description": "描述1",
                "format": "openai",
                "role_types": [],
                "template_content": "内容1",
                "variables": [],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            },
            {
                "id": "custom-id-2",
                "name": "自定义模板2",
                "description": "描述2",
                "format": "openai",
                "role_types": [],
                "template_content": "内容2",
                "variables": [],
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        ]
        
        # 执行
        templates = self.service.list_templates(include_defaults=True)
        
        # 验证
        self.mock_db.list_templates.assert_called_once_with(limit=100, offset=0)
        # 默认模板 + 自定义模板
        self.assertEqual(len(templates), 4)
        
        # 不包括默认模板的情况
        templates = self.service.list_templates(include_defaults=False)
        self.assertEqual(len(templates), 2)
    
    def test_generate_prompt_with_template_id(self):
        """测试使用指定模板ID生成提示词"""
        # 准备
        role_id = "role-id"
        template_id = "default-template-id"
        role_data = {
            "id": role_id,
            "name": "测试角色",
            "role_type": "test_type"
        }
        self.mock_db.get_role.return_value = role_data
        
        # 执行
        result = self.service.generate_prompt(
            role_id=role_id,
            template_id=template_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_db.get_role.assert_called_once_with(role_id)
        self.assertEqual(result["role_id"], role_id)
        self.assertEqual(result["role_name"], "测试角色")
        self.assertEqual(result["template_id"], template_id)
        self.assertEqual(result["format"], "openai")
        self.assertEqual(result["type"], "system")
        self.assertEqual(result["prompt"], "你好，测试角色")
    
    def test_generate_prompt_with_default_templates(self):
        """测试使用角色默认模板生成提示词"""
        # 准备
        role_id = "role-id"
        role_data = {
            "id": role_id,
            "name": "测试角色",
            "role_type": "test_type"
        }
        self.mock_db.get_role.return_value = role_data
        self.mock_db.get_role_default_templates.return_value = [{
            "id": "default-template-id",
            "name": "默认测试模板",
            "description": "测试用默认模板",
            "format": "openai",
            "role_types": [],
            "template_content": "你好，{role.name}",
            "variables": [{"name": "role.name", "source": "name"}],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }]
        
        # 执行
        result = self.service.generate_prompt(
            role_id=role_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_db.get_role.assert_called_once_with(role_id)
        self.mock_db.get_role_default_templates.assert_called_once_with(role_id)
        self.assertEqual(result["role_id"], role_id)
        self.assertEqual(result["role_name"], "测试角色")
        self.assertEqual(result["template_id"], "default-template-id")
        self.assertEqual(result["format"], "openai")
        self.assertEqual(result["type"], "system")
        self.assertEqual(result["prompt"], "你好，测试角色")
    
    def test_generate_prompt_with_role_type(self):
        """测试根据角色类型选择模板生成提示词"""
        # 准备
        role_id = "role-id"
        role_data = {
            "id": role_id,
            "name": "测试角色",
            "role_type": "test_type"
        }
        self.mock_db.get_role.return_value = role_data
        self.mock_db.get_role_default_templates.return_value = []
        
        # 执行
        result = self.service.generate_prompt(
            role_id=role_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_db.get_role.assert_called_once_with(role_id)
        self.mock_db.get_role_default_templates.assert_called_once_with(role_id)
        self.assertEqual(result["role_id"], role_id)
        self.assertEqual(result["role_name"], "测试角色")
        self.assertEqual(result["template_id"], "typed-template-id")
        self.assertEqual(result["format"], "openai")
        self.assertEqual(result["type"], "system")
        self.assertEqual(result["prompt"], "你好，测试角色，你是test_type")
    
    def test_preview_prompt(self):
        """测试预览提示词"""
        # 准备
        role_id = "role-id"
        template_id = "default-template-id"
        role_data = {
            "id": role_id,
            "name": "测试角色",
            "role_type": "test_type"
        }
        self.mock_db.get_role.return_value = role_data
        
        # 执行
        result = self.service.preview_prompt(
            role_id=role_id,
            template_id=template_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_db.get_role.assert_called_once_with(role_id)
        self.assertEqual(result["role_id"], role_id)
        self.assertEqual(result["role_name"], "测试角色")
        self.assertEqual(result["template_id"], template_id)
        self.assertEqual(result["format"], "openai")
        self.assertEqual(result["type"], "system")
        self.assertEqual(result["prompt"], "你好，测试角色")
    
    def test_format_prompt_openai(self):
        """测试OpenAI格式的提示词格式化"""
        content = "这是测试内容"
        
        # 系统提示词
        result = self.service._format_prompt(content, "openai", "system")
        self.assertEqual(result, content)
        
        # 用户提示词
        result = self.service._format_prompt(content, "openai", "user")
        self.assertEqual(result, content)
        
        # 助手提示词
        result = self.service._format_prompt(content, "openai", "assistant")
        self.assertEqual(result, content)
        
        # 完整提示词
        result = self.service._format_prompt(content, "openai", "complete")
        self.assertEqual(result, {"role": "system", "content": content})
    
    def test_format_prompt_anthropic(self):
        """测试Anthropic格式的提示词格式化"""
        content = "这是测试内容"
        
        # 系统提示词
        result = self.service._format_prompt(content, "anthropic", "system")
        self.assertEqual(result, f"<admin>\n{content}\n</admin>")
        
        # 用户提示词
        result = self.service._format_prompt(content, "anthropic", "user")
        self.assertEqual(result, f"Human: {content}")
        
        # 助手提示词
        result = self.service._format_prompt(content, "anthropic", "assistant")
        self.assertEqual(result, f"Assistant: {content}")
        
        # 完整提示词
        result = self.service._format_prompt(content, "anthropic", "complete")
        self.assertEqual(result, f"<admin>\n{content}\n</admin>")
    
    def test_set_role_default_template(self):
        """测试设置角色默认模板"""
        # 准备
        role_id = "role-id"
        template_id = "default-template-id"
        self.mock_db.set_role_default_template.return_value = True
        
        # 执行
        result = self.service.set_role_default_template(role_id, template_id)
        
        # 验证
        self.mock_db.set_role_default_template.assert_called_once_with(role_id, template_id)
        self.assertTrue(result)
    
    def test_remove_role_default_template(self):
        """测试移除角色默认模板"""
        # 准备
        role_id = "role-id"
        template_id = "template-id"
        self.mock_db.remove_role_default_template.return_value = True
        
        # 执行
        result = self.service.remove_role_default_template(role_id, template_id)
        
        # 验证
        self.mock_db.remove_role_default_template.assert_called_once_with(role_id, template_id)
        self.assertTrue(result)
    
    def test_get_role_default_templates(self):
        """测试获取角色默认模板"""
        # 准备
        role_id = "role-id"
        self.mock_db.get_role_default_templates.return_value = [{
            "id": "template-id",
            "name": "模板名称",
            "description": "模板描述",
            "format": "openai",
            "role_types": [],
            "template_content": "模板内容",
            "variables": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }]
        
        # 执行
        templates = self.service.get_role_default_templates(role_id)
        
        # 验证
        self.mock_db.get_role_default_templates.assert_called_once_with(role_id)
        self.assertEqual(len(templates), 1)
        self.assertEqual(templates[0].id, "template-id")
        self.assertEqual(templates[0].name, "模板名称")


if __name__ == "__main__":
    unittest.main() 