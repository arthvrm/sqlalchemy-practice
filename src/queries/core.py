from sqlalchemy import Integer, and_, func, text, insert, select, update
from sqlalchemy.orm import aliased
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
                    resumes_table.c.workload,                                                       # .c. означає звернення по column оскільки
                    func.avg(resumes_table.c.compensation).cast(Integer).label("avg_compensation"), #   звернення до моделі не завдяки orm
                    #   cast() означає перетворення до типу даних, в нашому випадку з float до integer
                    #   label() відповідає за створення нового стовбця яке в нашому випадку відповідає за avg блаблаблаа
                )
                .select_from(resumes_table)
                .filter(and_(
                    resumes_table.c.title.contains(like_language), # типо містить... contains ж...
                    resumes_table.c.compensation > 40000,
                ))
                .group_by(resumes_table.c.workload)
                .having(func.avg(resumes_table.c.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True})) # compile() для підстановки значення в наш згенерований sqlalchemy-єю запит
            res = conn.execute(query)
            result = res.all()
            print(result[0].avg_compensation)
    
    @staticmethod
    def insert_additional_resumes() -> None:
        with sync_engine.connect() as conn:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Danny"},  # id 5
            ]
            resumes = [
                {"title": "Python developer", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(workers_table).values(workers)
            insert_resumes = insert(resumes_table).values(resumes)
            conn.execute(insert_workers)
            conn.execute(insert_resumes)
            conn.commit()
    
    @staticmethod
    def join_cte_subquery_window_func() -> None:
        with sync_engine.connect() as conn:
            r = aliased(resumes_table) # aliased() щось по типу скорочень, сприйняття
            w = aliased(workers_table)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.c.compensation).over(partition_by=r.c.workload).cast(Integer).label("avg_workload_compensation"), 
                    #                               partition_by= в ролі поділу за чимось, типо avg для кожної окремої групи значень workload
                )
                .join(r, r.c.worker_id == w.c.id).subquery("helper1") # subquery() в ролі назв (idk нашо)
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff"),
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )
            res = conn.execute(query)
            result = res.all() # res.all() виступає в ролі зчитувача результату aka компіляції вихідного результату
            #                    по цій причині ЗАВЖДИ спочатку результат зберігаємо(result) а далі оперуєм ним як завгодно
            print(f"{result=}")


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
    
    
    @staticmethod
    async def insert_additional_resumes() -> None:
        async with async_engine.connect() as conn:
            workers = [
                {"username": "Artem"},
                {"username": "Roman"},
                {"username": "Danny"},
            ]
            resumes = [
                {"title": "Python developer", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(workers_table).values(workers)
            insert_resumes = insert(resumes_table).values(resumes)
            await conn.execute(insert_workers)
            await conn.execute(insert_resumes)
            await conn.commit()
    
    @staticmethod
    async def join_cte_subquery_window_func() -> None:
        async with async_engine.connect() as conn:
            r = aliased(resumes_table)
            w = aliased(workers_table)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.c.compensation).over(partition_by=r.c.workload).cast(Integer).label("avg_workload_compensation"),
                )
                .join(r, r.c.worker_id == w.c.id).subquery("helper1")
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff"),
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )
            res = await conn.execute(query)
            result = res.all()
            print(f"{result=}")