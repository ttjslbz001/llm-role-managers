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
from src.llm_roles.api.role_api import RoleAPI

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