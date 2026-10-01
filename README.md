# Financial Risk Agent

一个基于 **FastAPI + LangGraph + RAG + 大模型** 的金融交易风险分析系统。项目通过 SQL 查询交易流水，结合规则引擎识别异常交易，再使用 FAISS 知识库检索风控规则，最后由模型生成中文风险分析报告。

## 项目功能

- 交易流水查询：按用户 ID 查询最近交易记录
- 规则风险识别：根据金额、时间、地点、设备等因素计算风险分数
- 风险报告生成：输出结构化风控分析结果
- LLM 智能报告：调用大模型生成专业中文风控报告
- RAG 知识库检索：基于 FAISS 检索本地风控规则文档
- LangGraph 工作流：串联 SQL、风险识别、RAG、报告生成节点
- 多 Agent 分析：SQL Agent、Risk Agent、RAG Agent、Report Agent 协作完成分析
- 会话记忆：按 session_id 保存和读取历史分析结果
- 前端页面：提供一个简单的 Web 控制台用于发起风险分析和查看报告

## 技术栈

- 后端框架：FastAPI
- ASGI 服务：Uvicorn
- 数据库：MySQL
- ORM/SQL：SQLAlchemy + PyMySQL
- 大模型框架：LangChain / LangChain OpenAI
- 多 Agent 编排：LangGraph
- 向量数据库：FAISS
- Embedding 模型：sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- 配置管理：pydantic-settings + python-dotenv
- 前端：HTML + CSS + JavaScript

## 目录结构

```text
financial-risk-agent/
├── app/
│   ├── agents/                 # LangGraph 工作流与多 Agent 编排
│   ├── api/                    # FastAPI 路由
│   ├── core/                   # 配置与大模型初始化
│   ├── db/                     # 数据库连接
│   ├── memory/                 # 会话记忆
│   ├── rag/                    # 向量知识库构建脚本
│   └── skills/                 # SQL 查询、风险分析、报告、RAG 等能力模块
├── data/
│   └── faiss_index/            # FAISS 向量索引
├── docs/
│   └── risk_rules.txt          # 风控规则知识库原始文档
├── frontend/
│   └── index.html              # 前端页面
├── tests/                      # 测试目录
├── requirements.txt
└── README.md
```

## 环境要求

- Python 3.10+
- MySQL 8.0+
- 可访问 DeepSeek/OpenAI 兼容接口的 API Key

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zjq-yl/multi-agent-risk-analysis
cd multi-agent-risk-analysis
```

### 2. 创建虚拟环境

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
APP_NAME=Financial Risk Agent
APP_VERSION=0.1.0

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=deepseek-chat

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=financial_risk_agent

FAISS_INDEX_PATH=./data/faiss_index
KNOWLEDGE_DOCS_PATH=./docs
```

> 注意：当前代码在 `app/core/llm.py` 中使用的是 OpenAI 兼容调用方式，并将 `base_url` 设置为 `https://api.deepseek.com/v1`。如果你使用其他兼容服务，请同步修改该地址。

### 5. 准备 MySQL 数据表

项目默认查询 `transactions` 表，可以使用下面的 SQL 创建示例表：

```sql
CREATE DATABASE IF NOT EXISTS financial_risk_agent
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE financial_risk_agent;

CREATE TABLE IF NOT EXISTS transactions (
  transaction_id VARCHAR(64) PRIMARY KEY,
  account_id VARCHAR(64),
  user_id VARCHAR(64) NOT NULL,
  amount DECIMAL(18, 2) NOT NULL,
  transaction_type VARCHAR(32),
  direction VARCHAR(32),
  location VARCHAR(64),
  device_id VARCHAR(64),
  ip_address VARCHAR(64),
  transaction_time DATETIME NOT NULL,
  status VARCHAR(32),
  INDEX idx_user_time (user_id, transaction_time)
);
```

示例数据：

```sql
INSERT INTO transactions (
  transaction_id, account_id, user_id, amount, transaction_type,
  direction, location, device_id, ip_address, transaction_time, status
) VALUES
('T10001', 'A1001', 'U1001', 80000.00, 'transfer', 'out', '上海', 'D8001', '192.168.1.10', '2026-06-01 23:30:00', 'success'),
('T10002', 'A1001', 'U1001', 1200.00, 'payment', 'out', '北京', 'D1001', '192.168.1.11', '2026-06-02 10:20:00', 'success'),
('T10003', 'A1001', 'U1001', 56000.00, 'withdraw', 'out', '深圳', 'D8002', '192.168.1.12', '2026-06-03 02:10:00', 'success');
```

### 6. 构建 RAG 向量知识库

如果 `data/faiss_index` 不存在或需要更新知识库，请执行：

```bash
python -m app.rag.build_vector_store
```

该脚本会读取 `docs/risk_rules.txt`，切分文本并生成 FAISS 本地索引。

### 7. 启动后端服务

前端页面默认请求 `http://127.0.0.1:8001`，因此推荐使用 8001 端口启动：

```bash
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8001
```

启动后访问：

- 后端根路径：http://127.0.0.1:8001
- 健康检查：http://127.0.0.1:8001/health
- Swagger 文档：http://127.0.0.1:8001/docs
- ReDoc 文档：http://127.0.0.1:8001/redoc

### 8. 打开前端页面

直接用浏览器打开：

```text
frontend/index.html
```

输入用户 ID 和会话 ID 后，点击开始分析即可调用多 Agent 风控流程。

## API 接口

### 基础接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 服务状态 |
| GET | `/health` | 健康检查 |

### 交易与风险分析

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/transactions/{user_id}` | 查询用户交易流水 |
| GET | `/risk/analyze/{user_id}` | 执行规则风险分析 |
| GET | `/report/{user_id}` | 生成规则版风险报告 |
| GET | `/llm-report/{user_id}` | 生成大模型风险报告 |

### RAG 与工作流

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/rag/search?query=大额交易风险` | 检索风控知识库 |
| GET | `/workflow/risk/{user_id}` | 执行 LangGraph 风险分析工作流 |

### 多 Agent 与记忆

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/agent/risk/{user_id}?session_id=demo-session` | 执行多 Agent 风控分析 |
| GET | `/agent/memory/{session_id}` | 查询指定会话的全部历史记录 |
| GET | `/agent/memory/{session_id}/latest` | 查询指定会话最近一次分析 |
| DELETE | `/agent/memory/{session_id}` | 清空指定会话历史记录 |

## 风险规则说明

当前规则引擎主要根据以下条件计算交易风险：

| 规则 | 条件 | 分数 |
| --- | --- | --- |
| 大额交易 | 单笔金额大于等于 50000 | +40 |
| 夜间交易 | 交易时间早于 06:00 或晚于等于 23:00 | +20 |
| 异常设备 | 设备 ID 以 `D8` 开头 | +20 |
| 异地交易 | 交易地点为上海、深圳、广州等重点城市 | +20 |

风险等级：

| 分数 | 等级 |
| --- | --- |
| >= 70 | HIGH |
| >= 40 且 < 70 | MEDIUM |
| < 40 | LOW |

## 多 Agent 流程

```text
SQL Agent
  -> 查询用户交易流水

Risk Agent
  -> 识别大额、夜间、异常设备、异地等风险

RAG Agent
  -> 根据风险原因检索风控规则知识库

Report Agent
  -> 调用大模型生成最终中文风险报告
```

## 常见问题

### 1. 启动时报 MySQL 连接失败

请检查 `.env` 中的数据库配置是否正确，并确认 MySQL 服务已启动：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=financial_risk_agent
```

### 2. RAG 检索时报 FAISS 索引不存在

执行下面命令重新构建索引：

```bash
python -m app.rag.build_vector_store
```

### 3. 大模型调用失败

请检查：

- `OPENAI_API_KEY` 是否正确
- `OPENAI_MODEL` 是否是当前服务支持的模型
- `app/core/llm.py` 中的 `base_url` 是否匹配你的模型服务

### 4. 前端请求失败

前端默认请求：

```text
http://127.0.0.1:8001
```

请确认后端服务使用 8001 端口启动。如果你改用了其他端口，需要同步修改 `frontend/index.html` 中的请求地址。




