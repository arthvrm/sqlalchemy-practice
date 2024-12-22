import datetime
from typing import Optional, Annotated
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func, text
from database import Base, str_255
from sqlalchemy.orm import Mapped, mapped_column
import enum

"""annotations below"""
intpk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow
    )]



"""імперативний стиль"""
metadata_obj = MetaData() # об'єкт що передається у всі теблиці/моделі створені на стороні програми щоб мати доступ для взаємодії з ними(таблицями/моделями)


workers_table = Table(                       # створення таблиці
    "workers",                               # назва таблиці
    metadata_obj,                            # оголошення метадати в таблиці/моделі щоб мати доступ до неї з об'єкту metadata_obj
    Column("id", Integer, primary_key=True), # створення стовпця name, type, pk
    Column("username", String),
)


"""декларативний стиль"""
class WorkersOrm(Base):
    __tablename__ = "workers"
    
    id: Mapped[intpk]# = mapped_column(primary_key=True)
    username: Mapped[str]# = mapped_column()


class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"


class Resumes(Base):
    __tablename__ = "resumes"
    
    id: Mapped[intpk]# = mapped_column(primary_key=True)
    title: Mapped[str_255]# = mapped_column(String(200))
    compensation: Mapped[Optional[int]] # Mapped[int | None] # Mapped[int] = mapped_column(nullable=True)
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE")) # ForeignKey(WorkersOrm.id) <- usualy not in usage
    created_at: Mapped[created_at]# = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[updated_at]# = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow)
