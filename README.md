# LLM 角色管理框架

一个用于创建和管理LLM（大型语言模型）预定义角色的Python框架。

## 功能特点

- 角色定义和管理
- 会话历史记录
- 角色属性自定义
- 基于SQLite的数据存储
- 模块化设计，支持扩展

## 环境要求

- Python 3.11+
- SQLite 3.9+（支持JSON功能）

## 快速开始

### 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate

# 安装依赖
pip install -e .
```

### 初始化数据库

```bash
python src/llm_roles/database/scripts/init_db.py
```

### 运行API服务器

```bash
# 安装必要依赖
pip install pyyaml fastapi uvicorn

# 启动API服务器
python scripts/run_api_server.py
```

API服务器启动后，可以通过以下URL访问：
- Swagger UI 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- API健康检查: http://localhost:8000/health

### 运行示例

```bash
python examples/basic_usage.py
```

## 项目结构

```
llm-roles/
├── src/                      # 源代码
│   └── llm_roles/            # 主包
│       ├── core/             # 核心组件
│       ├── roles/            # 角色定义
│       ├── database/         # 数据库接口
│       ├── utils/            # 工具函数
│       ├── cli/              # 命令行界面
│       └── web/              # Web界面（可选）
├── examples/                 # 使用示例
├── tests/                    # 测试代码
├── resource/                 # 资源文件
│   └── db/                   # 数据库文件
└── data/                     # 数据文件
    └── roles/                # 角色定义文件
```

## 技术架构

- **Python**: 3.11+
- **数据库**: SQLite 3.9+ (支持JSON1扩展)
- **ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **Web框架**: FastAPI
- **API文档**: OpenAPI 3.0 (Swagger UI 和 ReDoc)
- **用户界面**(可选): Streamlit 或 Gradio

## 许可证

MIT
