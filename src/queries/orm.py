from sqlalchemy import text, insert, select
from database import sync_engine, async_engine, session_factory, async_session_factory
from models import WorkersOrm, Base


class SyncORM:
    @staticmethod
    def create_tables() -> None:
        sync_engine.echo = False              # виключення виведення логів у консоль
        Base.metadata.drop_all(sync_engine)   # видаляє всі таблиці з бд на основі підключення до бд
        Base.metadata.create_all(sync_engine) # створює все що знаходиться в об'єкті метадати, на основі двигуна що з'єднується з бд
        sync_engine.echo = True               # включення виведення логів у консоль

    @staticmethod
    def insert_workers() -> None:
        with session_factory() as session:
            worker_beaver = WorkersOrm(username="Beaver")
            worker_wolf = WorkersOrm(username="Wolf")
            session.add_all([worker_beaver, worker_wolf])
            session.flush()  # вносить прямі зміни(запис даних) в потік не закриваючи сесії, rollback() <- для відкату. Не комітить
            
                             # в нашому випадку для нагляднішого прикладу id в декларативному стилі написання через ORM, задається ПІСЛЯ
                             # виконання транзакції sql-алхімією, відповідно звертатись по id того ж самого worker_beaver ми зможемо тільки
                             # ПІСЛЯ виконання flush() (в теорії)
            
            session.commit() # commit ж в свою чергу відправляє данні(якщо не було flush()(в теорії)) та завершує сесію ставлячи точку.

    @staticmethod
    def select_workers() -> None:
        with session_factory() as session:
            # worker_id = 1
            # worker_beaver = session.get(WorkersOrm, worker_id) # {"id": worker_id} | (worker_id, 2) <- можна декілька id прокинути(в теорії)
            query = select(WorkersOrm)                         # SELECT * FROM workers
            result = session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        with session_factory() as session:
            worker_beaver = session.get(WorkersOrm, worker_id)
            worker_beaver.username = new_username
            # session.expire_all()         # скасовує всі зміни наприклад - worker_beaver.username = new_username до стану заданого worker_beaver = session.get(WorkersOrm, worker_id)
            session.refresh(worker_beaver) # рефрешить вибраний запис на той що знаходиться в даний момент в бд
            session.commit()


class AsyncORM:
    @staticmethod
    async def create_tables() -> None:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def insert_data() -> None:
        async with async_session_factory() as session:
            worker_beaver = WorkersOrm(username="Beaver")
            worker_wolf = WorkersOrm(username="Wolf")
            session.add_all([worker_beaver, worker_wolf])
            await session.flush()
            await session.commit()
    
    @staticmethod
    async def select_workers() -> None:
        async with session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        async with session_factory() as session:
            worker_beaver = await session.get(WorkersOrm, worker_id)
            worker_beaver.username = new_username
            await session.refresh(worker_beaver)
            await session.commit()