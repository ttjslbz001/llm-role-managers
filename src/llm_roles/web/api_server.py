#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

# Add project root to Python path if running directly
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.llm_roles.database.sqlite import SQLiteDatabase
from src.llm_roles.services.role_manager import RoleManager
from src.llm_roles.services.prompt_service import PromptService
from src.llm_roles.api.role_api import RoleAPI
from src.llm_roles.api.prompt_api import PromptAPI

# 创建FastAPI应用
app = FastAPI(
    title="LLM角色管理API",
    description="LLM角色管理系统的RESTful API接口",
    version="0.1.0",
    docs_url="/docs",    # Swagger UI 路径
    redoc_url="/redoc",  # ReDoc 路径
    openapi_url="/openapi.json"  # OpenAPI JSON 路径
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以设置为特定域名，例如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义OpenAPI模式
def custom_openapi():
    """自定义OpenAPI模式，允许使用预定义的API文档"""
    # 尝试从文件加载API文档
    api_docs_path = project_root / "api_docs" / "api_docs.yml"
    
    if app.openapi_schema:
        return app.openapi_schema
        
    # 如果文件存在且为YAML格式，则尝试加载
    if api_docs_path.exists() and api_docs_path.suffix in ['.yml', '.yaml']:
        try:
            import yaml
            with open(api_docs_path, 'r', encoding='utf-8') as f:
                openapi_schema = yaml.safe_load(f)
                app.openapi_schema = openapi_schema
                return app.openapi_schema
        except (ImportError, yaml.YAMLError, IOError) as e:
            print(f"警告: 无法加载API文档文件: {e}")
    
    # 如果上述方法失败，则使用FastAPI的默认方式
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 数据模型
class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    role_type: Optional[str] = ""
    language_style: Optional[str] = None
    knowledge_domains: Optional[List[str]] = None
    response_mode: Optional[str] = None
    allowed_topics: Optional[List[str]] = None
    forbidden_topics: Optional[List[str]] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    role_type: Optional[str] = None
    language_style: Optional[str] = None
    knowledge_domains: Optional[List[str]] = None
    response_mode: Optional[str] = None
    allowed_topics: Optional[List[str]] = None
    forbidden_topics: Optional[List[str]] = None

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    format: str = "openai"
    role_types: Optional[List[str]] = None
    template_content: str
    variables: Optional[List[Dict[str, Any]]] = None

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None
    role_types: Optional[List[str]] = None
    template_content: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None

class PromptGenerateRequest(BaseModel):
    format: Optional[str] = "openai"
    type: Optional[str] = "complete"
    template_id: Optional[str] = None
    custom_variables: Optional[Dict[str, Any]] = None

class PromptPreviewRequest(BaseModel):
    template_id: str
    format: Optional[str] = "openai"
    type: Optional[str] = "complete"
    custom_variables: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    status: int
    message: str
    success: bool
    data: Optional[Dict[str, Any]] = None

# 依赖项 - 获取API实例
def get_role_api():
    """获取角色API实例"""
    db_path = project_root / "resource" / "db" / "llm_roles.db"
    if not db_path.exists():
        raise HTTPException(
            status_code=500, 
            detail="数据库不存在，请先运行初始化脚本: src/llm_roles/database/scripts/init_db.py"
        )
    
    db = SQLiteDatabase(str(db_path))
    role_manager = RoleManager(db)
    return RoleAPI(role_manager)

def get_prompt_api():
    """获取提示词API实例"""
    db_path = project_root / "resource" / "db" / "llm_roles.db"
    if not db_path.exists():
        raise HTTPException(
            status_code=500, 
            detail="数据库不存在，请先运行初始化脚本: src/llm_roles/database/scripts/init_db.py"
        )
    
    db = SQLiteDatabase(str(db_path))
    prompt_service = PromptService(db)
    return PromptAPI(prompt_service)

# API路由
@app.post("/roles", response_model=ApiResponse, tags=["角色管理"])
def create_role(role: RoleCreate, api: RoleAPI = Depends(get_role_api)):
    """创建新角色"""
    result = api.create_role(role.model_dump(exclude_none=True))
    return result

@app.get("/roles/{role_id}", response_model=ApiResponse, tags=["角色管理"])
def get_role(role_id: str, api: RoleAPI = Depends(get_role_api)):
    """获取角色详情"""
    result = api.get_role(role_id)
    return result

@app.put("/roles/{role_id}", response_model=ApiResponse, tags=["角色管理"])
def update_role(role_id: str, role: RoleUpdate, api: RoleAPI = Depends(get_role_api)):
    """更新角色"""
    # 移除空值字段
    update_data = {k: v for k, v in role.model_dump().items() if v is not None}
    result = api.update_role(role_id, update_data)
    return result

@app.delete("/roles/{role_id}", response_model=ApiResponse, tags=["角色管理"])
def delete_role(role_id: str, api: RoleAPI = Depends(get_role_api)):
    """删除角色"""
    result = api.delete_role(role_id)
    return result

@app.get("/roles", response_model=ApiResponse, tags=["角色管理"])
def list_roles(
    limit: int = Query(100, description="返回的最大角色数量"),
    offset: int = Query(0, description="分页偏移量"),
    api: RoleAPI = Depends(get_role_api)
):
    """列出所有角色"""
    result = api.list_roles(limit=limit, offset=offset)
    return result

@app.get("/search-roles", response_model=ApiResponse, tags=["角色管理"])
def search_roles(
    query: str = Query(..., description="搜索关键词"),
    api: RoleAPI = Depends(get_role_api)
):
    """搜索角色"""
    result = api.search_roles(query)
    return result

# 提示词模板管理API
@app.post("/prompt-templates", response_model=ApiResponse, tags=["提示词管理"])
def create_template(
    template: TemplateCreate,
    api: PromptAPI = Depends(get_prompt_api)
):
    """创建提示词模板"""
    result = api.create_template(template.model_dump(exclude_none=True))
    return result

@app.get("/prompt-templates/{template_id}", response_model=ApiResponse, tags=["提示词管理"])
def get_template(
    template_id: str,
    api: PromptAPI = Depends(get_prompt_api)
):
    """获取提示词模板详情"""
    result = api.get_template(template_id)
    return result

@app.put("/prompt-templates/{template_id}", response_model=ApiResponse, tags=["提示词管理"])
def update_template(
    template_id: str,
    template: TemplateUpdate,
    api: PromptAPI = Depends(get_prompt_api)
):
    """更新提示词模板"""
    # 移除空值字段
    update_data = {k: v for k, v in template.model_dump().items() if v is not None}
    result = api.update_template(template_id, update_data)
    return result

@app.delete("/prompt-templates/{template_id}", response_model=ApiResponse, tags=["提示词管理"])
def delete_template(
    template_id: str,
    api: PromptAPI = Depends(get_prompt_api)
):
    """删除提示词模板"""
    result = api.delete_template(template_id)
    return result

@app.get("/prompt-templates", response_model=ApiResponse, tags=["提示词管理"])
def list_templates(
    include_defaults: bool = Query(True, description="是否包含默认模板"),
    limit: int = Query(100, description="返回的最大模板数量"),
    offset: int = Query(0, description="分页偏移量"),
    api: PromptAPI = Depends(get_prompt_api)
):
    """列出所有提示词模板"""
    result = api.list_templates(include_defaults=include_defaults, limit=limit, offset=offset)
    return result

# 角色提示词生成API
@app.get("/roles/{role_id}/prompt", response_model=ApiResponse, tags=["提示词生成"])
def get_role_prompt(
    role_id: str,
    format: str = Query("openai", description="提示词格式(openai, anthropic等)"),
    type: str = Query("complete", description="提示词类型(system, user, assistant, complete等)"),
    template_id: Optional[str] = Query(None, description="使用的模板ID"),
    api: PromptAPI = Depends(get_prompt_api)
):
    """获取角色提示词"""
    result = api.generate_prompt(
        role_id=role_id,
        format=format,
        prompt_type=type,
        template_id=template_id
    )
    return result

@app.post("/roles/{role_id}/prompt", response_model=ApiResponse, tags=["提示词生成"])
def generate_role_prompt(
    role_id: str,
    request: PromptGenerateRequest,
    api: PromptAPI = Depends(get_prompt_api)
):
    """生成角色提示词（带自定义参数）"""
    result = api.generate_prompt(
        role_id=role_id,
        format=request.format,
        prompt_type=request.type,
        template_id=request.template_id,
        custom_vars=request.custom_variables
    )
    return result

@app.post("/roles/{role_id}/preview-prompt", response_model=ApiResponse, tags=["提示词生成"])
def preview_role_prompt(
    role_id: str,
    request: PromptPreviewRequest,
    api: PromptAPI = Depends(get_prompt_api)
):
    """预览角色使用特定模板的提示词"""
    result = api.preview_prompt(
        role_id=role_id,
        template_id=request.template_id,
        format=request.format,
        prompt_type=request.type,
        custom_vars=request.custom_variables
    )
    return result

# 角色默认模板管理API
@app.post("/roles/{role_id}/default-templates/{template_id}", response_model=ApiResponse, tags=["提示词管理"])
def set_role_default_template(
    role_id: str,
    template_id: str,
    api: PromptAPI = Depends(get_prompt_api)
):
    """设置角色的默认模板"""
    result = api.set_role_default_template(role_id, template_id)
    return result

@app.delete("/roles/{role_id}/default-templates/{template_id}", response_model=ApiResponse, tags=["提示词管理"])
def remove_role_default_template(
    role_id: str,
    template_id: str,
    api: PromptAPI = Depends(get_prompt_api)
):
    """移除角色的默认模板"""
    result = api.remove_role_default_template(role_id, template_id)
    return result

@app.get("/roles/{role_id}/default-templates", response_model=ApiResponse, tags=["提示词管理"])
def get_role_default_templates(
    role_id: str,
    api: PromptAPI = Depends(get_prompt_api)
):
    """获取角色的默认模板列表"""
    result = api.get_role_default_templates(role_id)
    return result

# 健康检查
@app.get("/health", tags=["系统"])
def health_check():
    """系统健康检查"""
    return {"status": "healthy", "message": "API服务运行正常"}

# 主函数
def main():
    """启动FastAPI应用"""
    import uvicorn
    
    # 确保数据库目录存在
    db_dir = project_root / "resource" / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # 启动服务器
    uvicorn.run(
        "src.llm_roles.web.api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main() 