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
        Index("title_index", "title"), # створює індекси що прискорюють виконання пошукових запитів для вибраних стовпців таблиці
        CheckConstraint("compensation > 0", name="check_compensation_positive"), # створює перевірку яка гарантує, що значення стовпців
    )                                                                            # будуть відповідати обмеженням або певній логіці
    
    vacancies_replied: Mapped[list["VacanciesOrm"]] = relationship( # бачиш тут є list, означає що це MANY, тепер шуруй до 134
        back_populates="resumes_replied",
        secondary="vacancies_replies", # Зв'язок через таблицю-посередник
                                       # Вказує, що зв'язок між ResumesOrm та VacanciesOrm встановлюється через таблицю vacancies_replies
    )

    # Детальніше про M2M зв'язки
    
    # Аргумент secondary в SQLAlchemy використовується для визначення таблиці-посередника в багато-до-багато зв'язках між двома таблицями

    # secondary вказує на ім'я таблиці або об'єкт таблиці (як правило, створеної за допомогою Table), яка використовується для реалізації
    # зв'язку "багато-до-багато".
    
    # У таких випадках жодна з таблиць (моделей) не зберігає пряму інформацію про іншу.
    # Замість цього є окрема таблиця, що зберігає ключі з обох таблиць.


class VacanciesOrm(Base):
    __tablename__ = "vacancies"
    
    id: Mapped[intpk]
    title: Mapped[str_255]
    compensation: Mapped[Optional[int]]
    
    resumes_replied: Mapped[list["ResumesOrm"]] = relationship( # тут теж list, означає що теж MANY, відповідно третя табл чисто для
                                                                #                                                функціоналу + посередник
        back_populates="vacancies_replied",
        secondary="vacancies_replies", # Зв'язок через таблицю-посередник
                                       # Вказує, що зв'язок між ResumesOrm та VacanciesOrm встановлюється через таблицю vacancies_replies
    )


# Таблиця-посередник                        (зазвичай це Table() aka те в чому ще прописується MetaData)

# Зберігає зв'язки між vacancies та resumes
# Використовується лише для багато-до-багато зв'язків (secondary в тому числі)

# Таблиця-посередник не має власної ORM-моделі(цей випадок більше як виключення =D )
class VacanciesRepliesOrm(Base):
    __tablename__ = "vacancies_replies"
    
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    cover_letter: Mapped[Optional[str]]