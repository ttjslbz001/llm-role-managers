#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock, patch
from http import HTTPStatus

from src.llm_roles.api.prompt_api import PromptAPI
from src.llm_roles.core.prompt_template import PromptTemplate


class TestPromptAPI(unittest.TestCase):
    """提示词API单元测试"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建一个Mock服务
        self.mock_service = MagicMock()
        self.api = PromptAPI(self.mock_service)
    
    def test_create_template_success(self):
        """测试成功创建模板"""
        # 准备
        template_data = {
            "name": "测试模板",
            "template_content": "测试内容",
            "description": "测试描述"
        }
        mock_template = MagicMock()
        mock_template.to_dict.return_value = {
            "id": "test-id",
            "name": "测试模板",
            "template_content": "测试内容",
            "description": "测试描述"
        }
        self.mock_service.create_template.return_value = mock_template
        
        # 执行
        result = self.api.create_template(template_data)
        
        # 验证
        self.mock_service.create_template.assert_called_once_with(template_data)
        self.assertEqual(result["status"], HTTPStatus.CREATED)
        self.assertEqual(result["message"], "提示词模板创建成功")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], "test-id")
    
    def test_create_template_missing_fields(self):
        """测试缺少必要字段创建模板"""
        # 准备
        template_data = {
            "description": "测试描述"
        }
        
        # 执行
        result = self.api.create_template(template_data)
        
        # 验证
        self.mock_service.create_template.assert_not_called()
        self.assertEqual(result["status"], HTTPStatus.BAD_REQUEST)
        self.assertEqual(result["message"], "缺少必要字段: name, template_content")
        self.assertFalse(result["success"])
    
    def test_create_template_error(self):
        """测试创建模板出错"""
        # 准备
        template_data = {
            "name": "测试模板",
            "template_content": "测试内容"
        }
        self.mock_service.create_template.side_effect = Exception("测试错误")
        
        # 执行
        result = self.api.create_template(template_data)
        
        # 验证
        self.mock_service.create_template.assert_called_once_with(template_data)
        self.assertEqual(result["status"], HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(result["message"], "提示词模板创建失败: 测试错误")
        self.assertFalse(result["success"])
    
    def test_get_template_success(self):
        """测试成功获取模板"""
        # 准备
        template_id = "test-id"
        mock_template = MagicMock()
        mock_template.to_dict.return_value = {
            "id": template_id,
            "name": "测试模板",
            "template_content": "测试内容"
        }
        self.mock_service.get_template.return_value = mock_template
        
        # 执行
        result = self.api.get_template(template_id)
        
        # 验证
        self.mock_service.get_template.assert_called_once_with(template_id)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "获取提示词模板成功")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], template_id)
    
    def test_get_template_not_found(self):
        """测试获取不存在的模板"""
        # 准备
        template_id = "non-existent-id"
        self.mock_service.get_template.return_value = None
        
        # 执行
        result = self.api.get_template(template_id)
        
        # 验证
        self.mock_service.get_template.assert_called_once_with(template_id)
        self.assertEqual(result["status"], HTTPStatus.NOT_FOUND)
        self.assertEqual(result["message"], f"提示词模板不存在: {template_id}")
        self.assertFalse(result["success"])
    
    def test_get_template_error(self):
        """测试获取模板出错"""
        # 准备
        template_id = "test-id"
        self.mock_service.get_template.side_effect = Exception("测试错误")
        
        # 执行
        result = self.api.get_template(template_id)
        
        # 验证
        self.mock_service.get_template.assert_called_once_with(template_id)
        self.assertEqual(result["status"], HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(result["message"], "获取提示词模板失败: 测试错误")
        self.assertFalse(result["success"])
    
    def test_update_template_success(self):
        """测试成功更新模板"""
        # 准备
        template_id = "test-id"
        updates = {
            "name": "新名称",
            "description": "新描述"
        }
        mock_template = MagicMock()
        mock_template.to_dict.return_value = {
            "id": template_id,
            "name": "新名称",
            "description": "新描述"
        }
        self.mock_service.update_template.return_value = mock_template
        
        # 执行
        result = self.api.update_template(template_id, updates)
        
        # 验证
        self.mock_service.update_template.assert_called_once_with(template_id, **updates)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "提示词模板更新成功")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["id"], template_id)
        self.assertEqual(result["data"]["name"], "新名称")
    
    def test_update_template_not_found(self):
        """测试更新不存在的模板"""
        # 准备
        template_id = "non-existent-id"
        updates = {"name": "新名称"}
        self.mock_service.update_template.return_value = None
        
        # 执行
        result = self.api.update_template(template_id, updates)
        
        # 验证
        self.mock_service.update_template.assert_called_once_with(template_id, **updates)
        self.assertEqual(result["status"], HTTPStatus.NOT_FOUND)
        self.assertEqual(result["message"], f"提示词模板不存在或不可修改: {template_id}")
        self.assertFalse(result["success"])
    
    def test_delete_template_success(self):
        """测试成功删除模板"""
        # 准备
        template_id = "test-id"
        self.mock_service.delete_template.return_value = True
        
        # 执行
        result = self.api.delete_template(template_id)
        
        # 验证
        self.mock_service.delete_template.assert_called_once_with(template_id)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "提示词模板删除成功")
        self.assertTrue(result["success"])
    
    def test_delete_template_not_found(self):
        """测试删除不存在的模板"""
        # 准备
        template_id = "non-existent-id"
        self.mock_service.delete_template.return_value = False
        
        # 执行
        result = self.api.delete_template(template_id)
        
        # 验证
        self.mock_service.delete_template.assert_called_once_with(template_id)
        self.assertEqual(result["status"], HTTPStatus.NOT_FOUND)
        self.assertEqual(
            result["message"], 
            f"提示词模板不存在、不可删除或删除失败: {template_id}"
        )
        self.assertFalse(result["success"])
    
    def test_list_templates_success(self):
        """测试成功列出模板"""
        # 准备
        mock_template1 = MagicMock()
        mock_template1.to_dict.return_value = {
            "id": "id1",
            "name": "模板1"
        }
        mock_template2 = MagicMock()
        mock_template2.to_dict.return_value = {
            "id": "id2",
            "name": "模板2"
        }
        self.mock_service.list_templates.return_value = [mock_template1, mock_template2]
        
        # 执行
        result = self.api.list_templates(include_defaults=True, limit=10, offset=0)
        
        # 验证
        self.mock_service.list_templates.assert_called_once_with(
            include_defaults=True, limit=10, offset=0
        )
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "获取提示词模板列表成功")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["templates"]), 2)
        self.assertEqual(result["data"]["count"], 2)
        self.assertEqual(result["data"]["limit"], 10)
        self.assertEqual(result["data"]["offset"], 0)
    
    def test_generate_prompt_success(self):
        """测试成功生成提示词"""
        # 准备
        role_id = "role-id"
        prompt_result = {
            "role_id": role_id,
            "role_name": "测试角色",
            "prompt": "测试提示词",
            "template_id": "template-id",
            "template_name": "模板名称",
            "format": "openai",
            "type": "system"
        }
        self.mock_service.generate_prompt.return_value = prompt_result
        
        # 执行
        result = self.api.generate_prompt(
            role_id=role_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_service.generate_prompt.assert_called_once_with(
            role_id=role_id,
            format="openai",
            prompt_type="system",
            template_id=None,
            custom_vars=None
        )
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "提示词生成成功")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], prompt_result)
    
    def test_generate_prompt_not_found(self):
        """测试生成提示词时角色不存在"""
        # 准备
        role_id = "non-existent-id"
        self.mock_service.generate_prompt.side_effect = ValueError(f"角色不存在: {role_id}")
        
        # 执行
        result = self.api.generate_prompt(role_id=role_id)
        
        # 验证
        self.mock_service.generate_prompt.assert_called_once()
        self.assertEqual(result["status"], HTTPStatus.NOT_FOUND)
        self.assertEqual(result["message"], f"角色不存在: {role_id}")
        self.assertFalse(result["success"])
    
    def test_preview_prompt_success(self):
        """测试成功预览提示词"""
        # 准备
        role_id = "role-id"
        template_id = "template-id"
        prompt_result = {
            "role_id": role_id,
            "role_name": "测试角色",
            "prompt": "测试提示词",
            "template_id": template_id,
            "template_name": "模板名称",
            "format": "openai",
            "type": "system"
        }
        self.mock_service.preview_prompt.return_value = prompt_result
        
        # 执行
        result = self.api.preview_prompt(
            role_id=role_id,
            template_id=template_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证
        self.mock_service.preview_prompt.assert_called_once_with(
            role_id=role_id,
            template_id=template_id,
            format="openai",
            prompt_type="system",
            custom_vars=None
        )
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "提示词预览成功")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"], prompt_result)
    
    def test_set_role_default_template_success(self):
        """测试成功设置角色默认模板"""
        # 准备
        role_id = "role-id"
        template_id = "template-id"
        self.mock_service.set_role_default_template.return_value = True
        
        # 执行
        result = self.api.set_role_default_template(role_id, template_id)
        
        # 验证
        self.mock_service.set_role_default_template.assert_called_once_with(role_id, template_id)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "设置角色默认模板成功")
        self.assertTrue(result["success"])
    
    def test_set_role_default_template_not_found(self):
        """测试设置不存在的角色默认模板"""
        # 准备
        role_id = "role-id"
        template_id = "template-id"
        self.mock_service.set_role_default_template.return_value = False
        
        # 执行
        result = self.api.set_role_default_template(role_id, template_id)
        
        # 验证
        self.mock_service.set_role_default_template.assert_called_once_with(role_id, template_id)
        self.assertEqual(result["status"], HTTPStatus.NOT_FOUND)
        self.assertEqual(result["message"], "角色或模板不存在，或设置失败")
        self.assertFalse(result["success"])
    
    def test_remove_role_default_template_success(self):
        """测试成功移除角色默认模板"""
        # 准备
        role_id = "role-id"
        template_id = "template-id"
        self.mock_service.remove_role_default_template.return_value = True
        
        # 执行
        result = self.api.remove_role_default_template(role_id, template_id)
        
        # 验证
        self.mock_service.remove_role_default_template.assert_called_once_with(role_id, template_id)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "移除角色默认模板成功")
        self.assertTrue(result["success"])
    
    def test_get_role_default_templates_success(self):
        """测试成功获取角色默认模板列表"""
        # 准备
        role_id = "role-id"
        mock_template1 = MagicMock()
        mock_template1.to_dict.return_value = {
            "id": "id1",
            "name": "模板1"
        }
        mock_template2 = MagicMock()
        mock_template2.to_dict.return_value = {
            "id": "id2",
            "name": "模板2"
        }
        self.mock_service.get_role_default_templates.return_value = [mock_template1, mock_template2]
        
        # 执行
        result = self.api.get_role_default_templates(role_id)
        
        # 验证
        self.mock_service.get_role_default_templates.assert_called_once_with(role_id)
        self.assertEqual(result["status"], HTTPStatus.OK)
        self.assertEqual(result["message"], "获取角色默认模板列表成功")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["templates"]), 2)
        self.assertEqual(result["data"]["count"], 2)
        self.assertEqual(result["data"]["role_id"], role_id)


if __name__ == "__main__":
    unittest.main() 