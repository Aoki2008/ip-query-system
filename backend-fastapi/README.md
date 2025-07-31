# FastAPI IP查询服务

高性能异步IP地理位置查询API服务，基于FastAPI构建。

## 特性

- 🚀 **高性能**: 基于FastAPI和异步编程，支持高并发
- 📊 **智能缓存**: Redis缓存支持，提升查询速度
- 🔍 **精准查询**: 基于MaxMind GeoLite2数据库
- 📝 **自动文档**: 自动生成OpenAPI文档
- 🛡️ **类型安全**: 使用Pydantic进行数据验证
- 📈 **监控统计**: 内置性能监控和统计功能

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

复制环境配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置相关参数。

### 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## API文档

启动服务后，可以访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## API端点

### 基础信息

- `GET /` - 服务信息
- `GET /api` - API信息
- `GET /health` - 健康检查

### IP查询

- `GET /api/query?ip={ip}` - 单个IP查询
- `POST /api/batch-query` - 批量IP查询

### 统计信息

- `GET /api/stats` - 服务统计
- `GET /api/cache/stats` - 缓存统计
- `POST /api/cache/clear` - 清空缓存

## 配置说明

主要配置项：

- `HOST`: 服务器地址 (默认: 0.0.0.0)
- `PORT`: 服务器端口 (默认: 8000)
- `REDIS_ENABLED`: 是否启用Redis缓存
- `GEOIP_DB_PATH`: GeoIP数据库路径
- `MAX_BATCH_SIZE`: 最大批量查询数量

## 性能优化

- 使用异步编程提升并发性能
- Redis缓存减少重复查询
- 线程池处理GeoIP查询
- 批量处理优化

## 开发

### 项目结构

```
backend-fastapi/
├── app/
│   ├── api/          # API路由
│   ├── core/         # 核心模块
│   ├── models/       # 数据模型
│   ├── services/     # 业务服务
│   └── main.py       # 主应用
├── data/             # 数据文件
├── requirements.txt  # 依赖列表
└── main.py          # 启动入口
```

### 运行测试

```bash
pytest
```

## 部署

### Docker部署

```bash
docker build -t ip-query-fastapi .
docker run -p 8000:8000 ip-query-fastapi
```

### 生产环境

建议使用Gunicorn + Uvicorn部署：

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
