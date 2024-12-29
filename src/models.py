import datetime
from typing import Optional, Annotated
from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
    func
)
from database import Base, str_255
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

"""annotations below"""
intpk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow
    )]


class Workload(enum.Enum):
    parttime = "parttime"
    fulltime = "fulltime"


"""імперативний стиль"""
metadata_obj = MetaData() # об'єкт що передається у всі теблиці/моделі створені на стороні програми щоб мати доступ для взаємодії з ними(таблицями/моделями)


workers_table = Table(                       # створення таблиці
    "workers",                               # назва таблиці
    metadata_obj,                            # оголошення метадати в таблиці/моделі щоб мати доступ до неї з об'єкту metadata_obj
    Column("id", Integer, primary_key=True), # створення стовпця name, type, pk
    Column("username", String),
)


resumes_table = Table(
    "resumes",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("title", String(255)),
    Column("compensation", Integer, nullable=True),
    Column("workload", Enum(Workload)),
    Column("worker_id", ForeignKey("workers.id", ondelete="CASCADE")), # CASCADE: when a parent row is deleted, the children(current) are also deleted
    Column("created_at", TIMESTAMP, server_default=text("TIMEZONE('utc', now())")),
    Column("updated_at", TIMESTAMP, server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow),
)


"""декларативний стиль"""
class WorkersOrm(Base):
    __tablename__ = "workers"
    
    id: Mapped[intpk]# = mapped_column(primary_key=True)
    username: Mapped[str]# = mapped_column()
    
    resumes: Mapped[list["ResumesOrm"]] = relationship( # зв'язка таблиць
        back_populates="worker", # посилається на relationship в моделі ResumesOrm з назвою worker
        # backref="worker",      # буде СТВОРЮВАТИ relationship в моделі ResumesOrm(якщо його там нема) з визначеною назвою(worker)
        # backref НЕ РЕКОМЕНДУЄТЬСЯ ДО ЗАСТОСУВАННЯ, ВКАЗУЙТЕ RELATIONSHIPS ЯВНО ЧЕРЕЗ back_populates
    )
    
    resumes_parttime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'parttime')",
        order_by="ResumesOrm.id.desc()",
        # lazy="" # <- тут можна вибрати типи підгрузки(default: select) # краще визначати тип підгрузки в запиті
    )



class ResumesOrm(Base):
    __tablename__ = "resumes"
    
    id: Mapped[intpk]# = mapped_column(primary_key=True)
    title: Mapped[str_255]# = mapped_column(String(200))
    compensation: Mapped[Optional[int]] # Mapped[int | None] # Mapped[int] = mapped_column(nullable=True)
    workload: Mapped[Workload]
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE")) # ForeignKey(WorkersOrm.id) <- usualy not in usage
    created_at: Mapped[created_at]# = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[updated_at]# = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow)

    worker: Mapped["WorkersOrm"] = relationship( # зв'язка таблиць
        back_populates="resumes", 
    )
    # def __repr__(self): # для кожного класу моделі (логічно) можна прописувати свою логіку методу __repr__
    #     return f"Resume id={self.id}, ..."

    repr_cols_num = 4
    repr_cols = ("created_at", )
    
    __table_args__ = (                 # визначає пріколи таблиці таких як:
        PrimaryKeyConstraint("id"),    # задає первинний ключ для таблиці, визначаючи, що стовпець id буде унікальним і
                                       # не може містити значення NULL
        Index("title_index", "title"), # створює індекси що прискорюють виконання пошукових запитів для вибраних стовбців таблиці
        CheckConstraint("compensation > 0", name="check_compensation_positive"), # створює перевірку яка гарантує, що значення стовпців
    )                                                                            # будуть відповідати обмеженням або певній логіці