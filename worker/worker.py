import os
import time

from database.db import SessionLocal
from models.job import Job
from worker.redis_client import redis_client

WORKER_ID = os.getpid()

print("Worker started...")

while True:

    job_data = (
        redis_client.rpop("high_priority_queue")
        or redis_client.rpop("medium_priority_queue")
        or redis_client.rpop("low_priority_queue")
    )

    if job_data:

        db = SessionLocal()

        job = db.query(Job).filter(
            Job.id == int(job_data)
        ).first()

        if job:

            try:

                print(
    f"Worker {WORKER_ID} "
    f"Processing Job {job.id} [{job.priority}]"
)

                job.status = "RUNNING"
                db.commit()

                # Simulate failure for even IDs
                if job.id % 2 == 0:
                    raise Exception("Simulated Failure")

                time.sleep(5)

                job.status = "COMPLETED"
                db.commit()

                print(
                    f"Completed Job {job.id}"
                )

            except Exception as e:

                job.retries += 1

                if job.retries < 3:

                    print(
                        f"Retrying Job {job.id} "
                        f"(Attempt {job.retries})"
                    )

                    job.status = "PENDING"

                    queue_name = (
                        f"{job.priority.lower()}_priority_queue"
                    )

                    redis_client.lpush(
                        queue_name,
                        job.id
                    )

                else:

                    print(
                        f"Job {job.id} "
                        f"Failed Permanently"
                    )

                    job.status = "FAILED"

                db.commit()

        db.close()

    time.sleep(1)