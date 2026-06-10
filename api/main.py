from fastapi import FastAPI
from sqlalchemy.orm import Session

from database.db import Base, engine, SessionLocal
from models.job import Job
from worker.redis_client import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Distributed Job Scheduler Running"}


@app.post("/jobs")
def create_job(
    task_name: str,
    priority: str = "MEDIUM"
):

    db: Session = SessionLocal()

    job = Job(
        task_name=task_name,
        status="PENDING",
        priority=priority.upper()
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    queue_name = f"{priority.lower()}_priority_queue"

    redis_client.lpush(
        queue_name,
        job.id
    )

    return {
        "job_id": job.id,
        "task_name": job.task_name,
        "status": job.status,
        "priority": job.priority
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: int):

    db: Session = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job.id,
        "task_name": job.task_name,
        "status": job.status,
        "retries": job.retries,
        "priority": job.priority
    }