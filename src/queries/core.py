from sqlalchemy import text, insert, values
from database import sync_engine, async_engine
from models import metadata_obj, workers_table


def get_123_sync() -> None:
    with sync_engine.connect() as conn:
        res = conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.all()[0]=}")


async def get_123_async() -> None:
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.all()[0]=}")


def create_tables() -> None:
    sync_engine.echo = False             # виключення виведення логів у консоль
    metadata_obj.drop_all(sync_engine)   # видаляє все з бд на основі підключення до бд
    metadata_obj.create_all(sync_engine) # створює все що знаходиться в об'єкті метадати, на основі двигуна що з'єднується з бд
    sync_engine.echo = True              # включення виведення логів у консоль


def insert_data() -> None:
    with sync_engine.connect() as conn:
        # text(stmt = """INSERT INTO workers (username) VALUES # швидший за часом спосіб виконанню sql-script'а хоча пишеться вручну
        #     ('Beaver'), 
        #     ('Wolf');""")
        stmt = insert(workers_table).values(                   # instrument: "query builder", довший за часом спосіб виконання sql-script'а зате пишеться синтаксисом пайтона
            [
                {"username": "Beaver"},
                {"username": "Wolf"},
            ]
        )
        conn.execute(stmt)
        conn.commit()                                          # оскільки .connect() -> return ROLLBACK, треба вручну робити COMMIT щоб дані записувались в таблицю