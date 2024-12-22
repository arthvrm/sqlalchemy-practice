from sqlalchemy import text, insert
from database import sync_engine, async_engine, session_factory, async_session_factory
from models import metadata_obj, WorkersOrm



def create_tables() -> None:
    sync_engine.echo = False             # виключення виведення логів у консоль
    metadata_obj.drop_all(sync_engine)   # видаляє всі таблиці з бд на основі підключення до бд
    metadata_obj.create_all(sync_engine) # створює все що знаходиться в об'єкті метадати, на основі двигуна що з'єднується з бд
    sync_engine.echo = True              # включення виведення логів у консоль


def insert_data() -> None:
    with session_factory() as session:
        worker_beaver = WorkersOrm(username="Beaver")
        worker_wolf = WorkersOrm(username="Wolf")
        session.add_all([worker_beaver, worker_wolf])
        session.commit()


async def insert_data() -> None:
    async with async_session_factory() as session:
        worker_beaver = WorkersOrm(username="Beaver")
        worker_wolf = WorkersOrm(username="Wolf")
        session.add_all([worker_beaver, worker_wolf])
        await session.commit()