#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM角色管理API服务启动脚本

该脚本启动LLM角色管理API服务，支持Swagger UI进行API交互
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 检查yaml库是否已安装
try:
    import yaml
except ImportError:
    print("需要安装pyyaml库以支持OpenAPI文档加载")
    print("请运行: pip install pyyaml")
    sys.exit(1)

# 确保api_docs目录存在
api_docs_dir = project_root / "api_docs"
api_docs_dir.mkdir(parents=True, exist_ok=True)

# 确保api_docs.yml文件存在
api_docs_path = api_docs_dir / "api_docs.yml"
if not api_docs_path.exists():
    print(f"警告: API文档文件不存在: {api_docs_path}")
    print("API将使用FastAPI自动生成的OpenAPI模式")

# 确保数据库目录存在
db_dir = project_root / "resource" / "db"
db_dir.mkdir(parents=True, exist_ok=True)

# 检查数据库文件是否存在
db_path = db_dir / "llm_roles.db"
if not db_path.exists():
    print("数据库文件不存在，请先运行初始化脚本:")
    print("python src/llm_roles/database/scripts/init_db.py")
    sys.exit(1)

def main():
    """启动API服务器"""
    print("=" * 60)
    print("LLM角色管理API服务")
    print("=" * 60)
    print(f"* 访问Swagger UI文档: http://localhost:8000/docs")
    print(f"* 访问ReDoc文档: http://localhost:8000/redoc")
    print(f"* OpenAPI JSON: http://localhost:8000/openapi.json")
    print(f"* 健康检查: http://localhost:8000/health")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        "src.llm_roles.web.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main() 