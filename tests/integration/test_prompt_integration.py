#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
import tempfile
import json
from pathlib import Path

from src.llm_roles.core.prompt_template import PromptTemplate
from src.llm_roles.service.prompt_service import PromptService
from src.llm_roles.api.prompt_api import PromptAPI
from src.llm_roles.api.role_api import RoleAPI
from src.llm_roles.service.role_service import RoleService
from src.llm_roles.core.role import Role
from src.llm_roles.db.database import Database


class TestPromptIntegration(unittest.TestCase):
    """提示词模板集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类开始前的设置"""
        # 创建临时数据库文件
        cls.db_fd, cls.db_path = tempfile.mkstemp()
        cls.db = Database(cls.db_path)
        cls.db.init_db()
        
        # 创建服务和API实例
        cls.role_service = RoleService(cls.db)
        cls.prompt_service = PromptService(cls.db)
        cls.role_api = RoleAPI(cls.role_service)
        cls.prompt_api = PromptAPI(cls.prompt_service)
        
        # 添加测试数据：角色
        cls.test_role = Role(
            name="测试角色",
            description="用于测试的角色",
            type="assistant",
            metadata={"key": "value"}
        )
        created_role = cls.role_service.create_role(cls.test_role.to_dict())
        cls.role_id = created_role.id
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束后的清理"""
        os.close(cls.db_fd)
        os.unlink(cls.db_path)
    
    def test_1_create_template(self):
        """测试创建模板"""
        template_data = {
            "name": "测试模板",
            "template_content": "你是一个{{role_type}}，你的名字是{{name}}，你的职责是{{description}}",
            "description": "基础的角色模板",
            "is_default": False
        }
        
        # 通过API创建模板
        result = self.prompt_api.create_template(template_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词模板创建成功")
        
        # 保存模板ID用于后续测试
        self.template_id = result["data"]["id"]
    
    def test_2_get_template(self):
        """测试获取模板"""
        # 获取上一步创建的模板
        result = self.prompt_api.get_template(self.template_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "获取提示词模板成功")
        self.assertEqual(result["data"]["name"], "测试模板")
        self.assertEqual(
            result["data"]["template_content"], 
            "你是一个{{role_type}}，你的名字是{{name}}，你的职责是{{description}}"
        )
    
    def test_3_update_template(self):
        """测试更新模板"""
        updates = {
            "name": "更新后的模板",
            "description": "这是更新后的描述"
        }
        
        # 更新模板
        result = self.prompt_api.update_template(self.template_id, updates)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词模板更新成功")
        self.assertEqual(result["data"]["name"], "更新后的模板")
        self.assertEqual(result["data"]["description"], "这是更新后的描述")
        
        # 再次获取并确认更新成功
        result = self.prompt_api.get_template(self.template_id)
        self.assertEqual(result["data"]["name"], "更新后的模板")
    
    def test_4_set_role_default_template(self):
        """测试设置角色默认模板"""
        # 设置模板为角色的默认模板
        result = self.prompt_api.set_role_default_template(self.role_id, self.template_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "设置角色默认模板成功")
        
        # 获取角色的默认模板列表确认设置成功
        result = self.prompt_api.get_role_default_templates(self.role_id)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["templates"]), 1)
        self.assertEqual(result["data"]["templates"][0]["id"], self.template_id)
    
    def test_5_generate_prompt(self):
        """测试生成提示词"""
        # 生成提示词
        result = self.prompt_api.generate_prompt(
            role_id=self.role_id,
            format="openai",
            prompt_type="system"
        )
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词生成成功")
        self.assertEqual(result["data"]["role_id"], self.role_id)
        self.assertEqual(result["data"]["template_id"], self.template_id)
        
        # 检查提示词内容是否正确渲染
        expected_content = f"你是一个{self.test_role.type}，你的名字是{self.test_role.name}，你的职责是{self.test_role.description}"
        self.assertEqual(result["data"]["prompt"], expected_content)
    
    def test_6_preview_prompt(self):
        """测试预览提示词"""
        # 预览提示词
        result = self.prompt_api.preview_prompt(
            role_id=self.role_id,
            template_id=self.template_id,
            format="anthropic",
            prompt_type="user",
            custom_vars={"extra_field": "自定义值"}
        )
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词预览成功")
        self.assertEqual(result["data"]["role_id"], self.role_id)
        self.assertEqual(result["data"]["template_id"], self.template_id)
        self.assertEqual(result["data"]["format"], "anthropic")
        self.assertEqual(result["data"]["type"], "user")
        
        # 检查预览内容是否包含基本信息
        self.assertIn(self.test_role.name, result["data"]["prompt"])
        self.assertIn(self.test_role.type, result["data"]["prompt"])
        self.assertIn(self.test_role.description, result["data"]["prompt"])
    
    def test_7_create_default_template(self):
        """测试创建默认模板"""
        default_template_data = {
            "name": "全局默认模板",
            "template_content": "这是一个全局默认的{{role_type}}模板，为{{name}}设计",
            "description": "用于测试的全局默认模板",
            "is_default": True
        }
        
        # 创建默认模板
        result = self.prompt_api.create_template(default_template_data)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词模板创建成功")
        
        # 保存默认模板ID
        self.default_template_id = result["data"]["id"]
        
        # 验证是否在列表中出现
        result = self.prompt_api.list_templates(include_defaults=True)
        self.assertTrue(result["success"])
        
        # 查找默认模板
        found = False
        for template in result["data"]["templates"]:
            if template["id"] == self.default_template_id:
                found = True
                self.assertTrue(template["is_default"])
                break
        self.assertTrue(found, "未在列表中找到创建的默认模板")
    
    def test_8_remove_role_default_template(self):
        """测试移除角色默认模板"""
        # 移除角色的默认模板
        result = self.prompt_api.remove_role_default_template(self.role_id, self.template_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "移除角色默认模板成功")
        
        # 检查角色的默认模板列表是否为空
        result = self.prompt_api.get_role_default_templates(self.role_id)
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]["templates"]), 0)
    
    def test_9_delete_template(self):
        """测试删除模板"""
        # 删除测试模板
        result = self.prompt_api.delete_template(self.template_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "提示词模板删除成功")
        
        # 尝试获取被删除的模板，应该返回不存在
        result = self.prompt_api.get_template(self.template_id)
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], 404)


if __name__ == "__main__":
    unittest.main() 