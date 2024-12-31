from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from models import Workload

class WorkersAddDTO(BaseModel):  # POST
    username: str

class WorkersDTO(WorkersAddDTO): # GET
    id: int              # значення що задаються на рівні бд

class ResumesAddDTO(BaseModel):  # POST
    title: str
    compensation: Optional[int]
    workload: Workload
    worker_id: int

class ResumesDTO(ResumesAddDTO): # GET
    id: int              # значення що задаються на рівні бд
    created_at: datetime # значення що задаються на рівні бд
    updated_at: datetime # значення що задаються на рівні бд

class ResumesRelDTO(ResumesDTO):
    worker: "WorkersDTO"

class WorkersRelDTO(WorkersDTO):
    resumes: list["ResumesDTO"]