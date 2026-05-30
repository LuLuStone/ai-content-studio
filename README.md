<div align="center">

# 🎙️ AI 文音画创作平台

**一句话，万物生。**

输入一段文字，AI 自动创作播客、有声书、视频、图片。

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## ✨ 产品特性

<table>
<tr>
<td width="50%">

### 🎙️ 播客生成
输入话题，AI 自动生成多人对话播客脚本，支持 2-4 人对话，自动分配角色与音色，支持轻松闲聊、深度访谈、新闻播报、故事讲述等风格。

</td>
<td width="50%">

### 📖 有声书生成
支持单角色 / 多角色朗读模式，多角色模式自动为每个角色设计独特音色，支持自然、有感情、播音腔等风格，每句可指定不同情绪。

</td>
</tr>
<tr>
<td>

### 🎤 音色管理
内置 8 种精品音色（冰糖、茉莉、苏打、白桦等），支持上传音频样本，基于 **MiMo VoiceClone** 技术复刻任意音色。

</td>
<td>

### 📊 任务追踪
Celery 异步任务队列，支持并发生成。实时进度弹窗，逐句展示音频合成状态，支持播放预览。

</td>
</tr>
</table>

> 🚧 **视频**和**图片**模块开发中，敬请期待。

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                  │
│         Vite · Element Plus · TypeScript             │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────┐
│                 Backend (FastAPI)                    │
│           API Routes · SQLAlchemy ORM                │
├─────────────┬──────────────┬────────────────────────┤
│  MiMo LLM  │  MiMo TTS    │   Celery Workers       │
│  (脚本生成)  │  (语音合成)    │   (异步任务处理)        │
└──────┬──────┴──────┬───────┴────────┬───────────────┘
       │             │                │
  ┌────▼────┐  ┌─────▼─────┐  ┌──────▼──────┐
  │  MySQL  │  │   Redis   │  │   Storage   │
  │  数据存储  │  │  消息队列   │  │  文件存储    │
  └─────────┘  └───────────┘  └─────────────┘
```

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus | SPA，组件化 |
| 后端 | Python + FastAPI | 异步高性能，自动生成 API 文档 |
| 数据库 | MySQL 8 | 主数据存储 |
| 缓存/队列 | Redis + Celery | AI 生成任务异步处理 |
| LLM | 小米 MiMo API | 文本生成（脚本创作） |
| TTS | 小米 MiMo TTS | 语音合成（预置/设计/复刻三种模式） |
| 设计语言 | ElevenLabs DESIGN.md | 编辑杂志风格 UI |

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| MySQL | 8.0+ |
| Redis | 7.0+ |

### 1. 克隆仓库

```bash
git clone git@github.com:LuLuStone/ai-content-studio.git
cd ai-content-studio
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key：

```env
# 小米 MiMo API
MIMO_API_KEY=your_api_key
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_LLM_MODEL=mimo-v2.5-pro
MIMO_TTS_MODEL=mimo-v2.5-tts

# MySQL
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/ai_agent?charset=utf8mb4

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 3. 创建数据库

```sql
CREATE DATABASE ai_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

> 后端运行在 `http://localhost:8000`，API 文档：`http://localhost:8000/docs`

### 5. 启动 Celery Worker

```bash
# 新终端
cd backend && source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
```

### 6. 启动前端

```bash
# 新终端
cd frontend
npm install
npm run dev
```

> 前端运行在 `http://localhost:5173`

### 7. 启动 Redis

```bash
# macOS
brew install redis && redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 🐳 Docker 一键部署

```bash
docker-compose up -d
```

> 启动 Redis + 后端 + Celery Worker + 前端四个容器。MySQL 需单独安装。

---

## 📡 API 概览

<details>
<summary><strong>🎙️ 播客 / 有声书</strong></summary>

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/create` | POST | 统一创作入口 |
| `/api/podcasts` | GET | 播客列表 |
| `/api/podcasts/{id}` | GET | 播客详情 |
| `/api/podcasts/{id}/audio` | GET | 播客音频 |
| `/api/audiobooks` | GET | 有声书列表 |
| `/api/audiobooks/{id}` | GET | 有声书详情 |
| `/api/audiobooks/{id}/audio` | GET | 有声书音频 |

</details>

<details>
<summary><strong>🎤 音色管理</strong></summary>

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/voices/presets` | GET | 预置音色列表 |
| `/api/voices/presets/{id}/preview` | POST | 试听预置音色（带缓存） |
| `/api/voices` | GET / POST | 自定义音色列表 / 上传创建 |
| `/api/voices/{id}` | PATCH / DELETE | 重命名 / 删除 |
| `/api/voices/{id}/preview` | POST | 试听自定义音色（VoiceClone） |

</details>

<details>
<summary><strong>📊 任务管理</strong></summary>

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/tasks/active` | GET | 进行中的任务 |
| `/api/tasks/{id}` | GET | 任务状态 + step_data |

</details>

完整交互式 API 文档：`http://localhost:8000/docs`

---

## 🎨 设计规范

项目采用 [ElevenLabs DESIGN.md](https://github.com/VoltAgent/awesome-design-md) 设计语言：

| 元素 | 规范 |
|------|------|
| 画布 | `#f5f5f5` 米白底色 |
| 墨色 | `#0c0a09` 暖近黑 |
| 标题字体 | EB Garamond（衬线，weight 300） |
| 正文字体 | Inter（+0.15px letter-spacing） |
| 按钮 | 胶囊形 `border-radius: 9999px` |
| 卡片 | 16px 圆角，1px hairline 边框 |
| 装饰 | 渐变光球（mint / peach / lavender / sky / rose） |

---

## 🔧 TTS 三种模式

| 模型 | 用途 | 说明 |
|------|------|------|
| `mimo-v2.5-tts` | 预置音色 | 内置 8 种精品音色，开箱即用 |
| `mimo-v2.5-tts-voicedesign` | 音色设计 | 文本描述自动生成音色，无需音频样本 |
| `mimo-v2.5-tts-voiceclone` | 音色复刻 | 上传音频样本，精准复刻任意音色 |

自定义音色使用 `custom:uuid` 前缀标识，任务自动路由到对应 TTS 模型。

---

## 📁 项目结构

```
ai-content-studio/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/                 # API 调用封装
│   │   ├── components/          # 通用组件
│   │   │   └── TaskProgressDialog.vue
│   │   ├── views/               # 页面视图
│   │   ├── router/              # 路由配置
│   │   └── stores/              # Pinia 状态管理
│   └── vite.config.ts
│
├── backend/                     # Python FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   ├── schemas/             # Pydantic 校验 Schema
│   │   ├── services/            # LLM / TTS 服务封装
│   │   ├── tasks/               # Celery 异步任务
│   │   ├── prompts/             # Prompt 模板
│   │   └── utils/               # 工具函数
│   └── requirements.txt
│
├── storage/                     # 文件存储
│   ├── audio/                   # 生成的音频
│   └── voices/                  # 自定义音色样本
│
├── DESIGN.md                    # UI 设计规范
├── docker-compose.yml           # Docker 部署配置
├── .env.example                 # 环境变量模板
└── README.md
```

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">

**Built with ❤️ using Vue 3 · FastAPI · Celery · Redis · 小米 MiMo**

</div>
