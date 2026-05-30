"""任务状态 API"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskStatus

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/active", response_model=List[TaskStatus])
def get_active_tasks(db: Session = Depends(get_db)):
    """获取所有进行中的任务（pending / processing），自动过滤超过 10 分钟的旧任务"""
    cutoff = datetime.now() - timedelta(minutes=10)
    # 先把超时的旧任务标记为失败
    db.query(Task).filter(
        Task.status.in_(["pending", "processing"]),
        Task.created_at < cutoff
    ).update({"status": "failed", "error_message": "任务超时，已自动清理"})
    db.commit()
    # 再查询真正活跃的任务
    tasks = db.query(Task).filter(
        Task.status.in_(["pending", "processing"])
    ).order_by(Task.created_at.desc()).all()
    return [
        TaskStatus(
            task_id=t.id,
            type=t.type,
            status=t.status,
            progress=t.progress,
            result_id=t.result_id,
            error_message=t.error_message,
            step_data=t.step_data,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tasks
    ]


@router.get("/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """查询任务状态"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskStatus(
        task_id=task.id,
        type=task.type,
        status=task.status,
        progress=task.progress,
        result_id=task.result_id,
        error_message=task.error_message,
        step_data=task.step_data,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
