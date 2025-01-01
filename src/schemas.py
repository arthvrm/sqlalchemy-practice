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

class ResumesRelWorkersDTO(ResumesDTO):
    worker: "WorkersDTO"

class WorkersRelResumesDTO(WorkersDTO):
    resumes: list["ResumesDTO"]

class VacanciesAddDTO(BaseModel):    # GET
    title: str
    compensation: Optional[int]

class VacanciesDTO(VacanciesAddDTO): # POST
    id: int

class VacanciesWithoutCompensationDTO(BaseModel):         # GET
    id: int
    title: str

class ResumesRelWorkerAndVacanciesRepliedDTO(ResumesDTO):
    worker: "WorkersDTO"
    vacancies_replied: list["VacanciesDTO"]

class ResumesRelVacanciesRepliedWithoutVacancyCompensationDTO(ResumesDTO):
    worker: "WorkersDTO"
    vacancies_replied: list["VacanciesWithoutCompensationDTO"]