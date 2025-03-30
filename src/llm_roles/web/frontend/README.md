# LLM角色管理系统前端

这是LLM角色管理系统的前端应用，基于React和TypeScript开发。

## 功能

- 角色管理：创建、编辑、查看和删除LLM角色
- 提示词模板管理：创建、编辑、查看和删除提示词模板
- 角色提示词预览：查看角色在不同模板下生成的提示词

## 技术栈

- React 18
- TypeScript
- React Router v6
- Material UI
- React Query
- Axios

## 开发

### 安装依赖

```bash
cd src/llm_roles/web/frontend
npm install
```

### 启动开发服务器

```bash
npm start
```

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
  ├── api/          # API服务
  ├── components/   # 可复用组件
  ├── contexts/     # React上下文
  ├── hooks/        # 自定义钩子
  ├── pages/        # 页面组件
  ├── types/        # TypeScript类型定义
  └── utils/        # 通用工具函数
```

## 与后端集成

前端通过`package.json`中的`proxy`字段与后端API进行集成。在开发环境中，对`/api`的请求会被代理到`http://localhost:8000`。 