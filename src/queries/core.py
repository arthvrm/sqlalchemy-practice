from sqlalchemy import Integer, and_, func, text, insert, select, update
from database import sync_engine, async_engine
from models import metadata_obj, workers_table, resumes_table, Workload


def get_123_sync() -> None:
    with sync_engine.connect() as conn:
        res = conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.all()[0]=}")


async def get_123_async() -> None:
    async with async_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6"))
        print(f"{res.all()[0]=}")


class SyncCore:
    @staticmethod                            # декоратор що перетворює функцію в статичний метод -> означає що для виклику методу не треба створювати екземпляр на основі класу
    def create_tables() -> None:
        sync_engine.echo = False             # виключення виведення логів у консоль
        metadata_obj.drop_all(sync_engine)   # видаляє всі таблиці з бд на основі підключення до бд
        metadata_obj.create_all(sync_engine) # створює все що знаходиться в об'єкті метадати, на основі двигуна що з'єднується з бд
        sync_engine.echo = True              # включення виведення логів у консоль

    @staticmethod
    def insert_workers() -> None:
        with sync_engine.connect() as conn:
            # text(stmt = """INSERT INTO workers (username) VALUES # швидший за часом спосіб виконання sql-script'а хоча пишеться вручну
            #     ('Beaver'), 
            #     ('Wolf');""")
            stmt = insert(workers_table).values(                   # instrument: "query builder", довший за часом спосіб виконання sql-script'а зате пишеться синтаксисом пайтона
                [
                    {"username": "Beaver"},
                    {"username": "Wolf"},
                ]
            )
            conn.execute(stmt)
            conn.commit()                                          # оскільки .connect() -> return ROLLBACK, треба вручну робити COMMIT(щоб дані записались в таблицю)

    @staticmethod
    def select_workers() -> None:
        with sync_engine.connect() as conn:
            query = select(workers_table) # SELECT * FROM workers
            result = conn.execute(query)
            workers = result.all()
            print(f"{workers=}")

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        with sync_engine.connect() as conn:
            # stmt = text("UPDATE workers SET username=:username WHERE id=:id") # для захисту від SQL-ін'єкцій використовуємо НЕ f-strings/format()
            # stmt = stmt.bindparams(username=new_username, id=worker_id)       # а вбудовану в підкапот(psycopg2||3) функцію bindparams()
            stmt = (
                update(workers_table)
                .values(username=new_username)
                # .where(workers_table.c.id==worker_id) # нижче .filter_by наслідується від .where тому сильної різнці між цими двома нема,
                .filter_by(id=worker_id)                # хіба що різниться синтаксис запису аргументів
            )
            conn.execute(stmt)
            conn.commit()
    
    @staticmethod
    def insert_resumes() -> None:
        with sync_engine.connect() as conn:
            resumes = [
                {"title": "Python Junior Developer", "compensation": 50000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Developer", "compensation": 150000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Data Engineer", "compensation": 250000, "workload": Workload.parttime, "worker_id": 2},
                {"title": "Data Scientist", "compensation": 300000, "workload": Workload.fulltime, "worker_id": 2},
            ]
            stmt = insert(resumes_table).values(resumes)
            conn.execute(stmt)
            conn.commit()
    
    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python") -> None:
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """
        with sync_engine.connect() as conn:
            query = (
                select(
                    resumes_table.c.workload,
                    func.avg(resumes_table.c.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(resumes_table)
                .filter(and_(
                    resumes_table.c.title.contains(like_language),
                    resumes_table.c.compensation > 40000,
                ))
                .group_by(resumes_table.c.workload)
                .having(func.avg(resumes_table.c.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = conn.execute(query)
            result = res.all()
            print(result[0].avg_compensation)


class AsyncCore:
    @staticmethod
    async def create_tables() -> None:
        async with async_engine.begin() as conn:
            await conn.run_sync(metadata_obj.drop_all)
            await conn.run_sync(metadata_obj.create_all)

    @staticmethod
    async def insert_workers() -> None:
        async with async_engine.connect() as conn:
            stmt = insert(workers_table).values(
                [
                    {"username": "Beaver"},
                    {"username": "Wolf"},
                ]
            )
            await conn.execute(stmt)
            await conn.commit()
    
    @staticmethod
    async def select_workers() -> None:
        async with async_engine.connect() as conn:
            query = select(workers_table)
            result = await conn.execute(query)
            workers = result.all()
            print(f"{workers=}")
    
    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        async with async_engine.connect() as conn:
            stmt = (
                update(workers_table)
                .values(username=new_username)
                .filter_by(id=worker_id)
            )
            await conn.execute(stmt)
            await conn.commit()
    
    @staticmethod
    async def insert_resumes() -> None:
        async with async_engine.connect() as conn:
            resumes = [
                {"title": "Python Junior Developer", "compensation": 50000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Developer", "compensation": 150000, "workload": Workload.fulltime, "worker_id": 1},
                {"title": "Python Data Engineer", "compensation": 250000, "workload": Workload.parttime, "worker_id": 2},
                {"title": "Data Scientist", "compensation": 300000, "workload": Workload.fulltime, "worker_id": 2},
            ]
            stmt = insert(resumes_table).values(resumes)
            await conn.execute(stmt)
            await conn.commit()
    
    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = "Python") -> None:
        async with async_engine.connect() as conn:
            query = (
                select(
                    resumes_table.c.workload,
                    func.avg(resumes_table.c.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(resumes_table)
                .filter(and_(
                    resumes_table.c.title.contains(like_language),
                    resumes_table.c.compensation > 40000,
                ))
                .group_by(resumes_table.c.workload)
                .having(func.avg(resumes_table.c.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await conn.execute(query)
            result = res.all()
            print(result[0].avg_compensation)
            