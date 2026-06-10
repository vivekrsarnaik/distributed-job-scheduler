from sqlalchemy import Column, Integer, String
from database.db import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    retries = Column(Integer, default=0)
    priority = Column(String, default="MEDIUM")