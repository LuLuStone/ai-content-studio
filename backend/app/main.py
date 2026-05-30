"""FastAPI 应用入口"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import init_db

# 导入路由
from app.api.create import router as create_router
from app.api.task import router as task_router
from app.api.podcast import router as podcast_router
from app.api.audiobook import router as audiobook_router
from app.api.video import router as video_router
from app.api.image import router as image_router
from app.api.voices import router as voices_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="AI全能创作平台",
    description="统一入口，生成播客、有声书、视频、图片",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保存储目录存在
storage_path = os.path.abspath(settings.STORAGE_PATH)
for sub in ["audio", "video", "image"]:
    os.makedirs(os.path.join(storage_path, sub), exist_ok=True)

# 静态文件服务（本地存储的音频/视频/图片）
app.mount("/storage", StaticFiles(directory=storage_path), name="storage")

# 注册路由
app.include_router(create_router)
app.include_router(task_router)
app.include_router(podcast_router)
app.include_router(audiobook_router)
app.include_router(video_router)
app.include_router(image_router)
app.include_router(voices_router)


@app.on_event("startup")
def startup():
    """应用启动时初始化数据库"""
    init_db()
    logging.info("数据库表初始化完成")


@app.get("/")
def root():
    return {
        "name": "AI全能创作平台",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
