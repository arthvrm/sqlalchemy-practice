from sqlalchemy import Integer, and_, text, insert, select, func, cast
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager
from database import sync_engine, async_engine, session_factory, async_session_factory
from models import WorkersOrm, Base, ResumesOrm, Workload


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
            workers = result.scalars().all() # scalars() позпаковує кортеж в моделі
            print(f"{workers=}")

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        with session_factory() as session:
            worker_beaver = session.get(WorkersOrm, worker_id)
            worker_beaver.username = new_username
            # session.expire_all()         # скасовує всі зміни наприклад - worker_beaver.username = new_username до стану заданого worker_beaver = session.get(WorkersOrm, worker_id)
            # session.refresh(worker_beaver) # рефрешить вибраний запис на той що знаходиться в даний момент в бд
            session.commit()

    @staticmethod
    def insert_resumes() -> None:
        with session_factory() as session:
            resume_beaver_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=Workload.fulltime, worker_id=1)
            resume_beaver_2 = ResumesOrm(
                title="Python Developer", compensation=150000, workload=Workload.fulltime, worker_id=1)
            resume_squirrel_1 = ResumesOrm(
                title="Python Data Engineer", compensation=250000, workload=Workload.parttime, worker_id=2)
            resume_squirrel_2 = ResumesOrm(
                title="Data Scientist", compensation=300000, workload=Workload.fulltime, worker_id=2)
            session.add_all([resume_beaver_1, resume_beaver_2, resume_squirrel_1, resume_squirrel_2])
            session.commit()

    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python") -> None:
        with session_factory() as session:
            """
            select workload, avg(compensation)::int as avg_compensation
            from resumes
            where title like '%Python%' and compensation > 40000
            group by workload
            having avg(compensation) > 70000
            """
            query = (
                select(
                    ResumesOrm.workload,
                    # 1 варіант застосування cast
                    # cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                    # 2 варіант застосування cast (рекомендується)
                    func.avg(ResumesOrm.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                # .where() | .filter() | .filter_by() <- потребує конкретні дані: id=1, workload="" ... на відміну від where/filter
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.compensation > 40000,
                ))
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(result)
            print(result[0].avg_compensation)
    
    @staticmethod
    def insert_additional_resumes() -> None:
        with session_factory() as session:
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
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()
    
    @staticmethod
    def join_cte_subquery_window_func() -> None:
        with session_factory() as session:
            """
            with helper2 as (
                select *, compensation-avg_workload_compensation as compensation_diff
                from
                (select
                    w.id,
                    w.username,
                    r.compensation,
                    r.workload,
                    avg(r.compensation) over (partition by workload)::int as avg_workload_compensation
                from resumes r
                join workers w on r.worker_id = w.id) helper1
            )
            select * from helper2
            order by compensation_diff desc
            """
            r = aliased(ResumesOrm) # aliased() щось по типу скорочень, сприйняття
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation"),
                    #                               partition_by= в ролі поділу за чимось, типо avg для кожної окремої групи значень workload
                )
                # .select_from(r) # краще не юзати, sql-алхімія сама краще підставить) (don't touch)
                .join(r, r.worker_id == w.id).subquery("helper1") # subquery() в ролі назв (idk нашо)
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
            # print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all() # res.all() виступає в ролі зчитувача результату aka компіляції вихідного результату
            #                    по цій причині ЗАВЖДИ спочатку результат зберігаємо(result) а далі оперуєм ним як завгодно
            print(f"{result=}")
    
    @staticmethod
    def select_workers_with_lazy_relationship() -> None:
        with session_factory() as session:
            query = (
                select(WorkersOrm) # завантажуємо всі записи з таблиці workers, але оскільки в нашій моделі прописаний relationship
                # з таблицею resumes, ми можемо звертатись до резюме записів as well(вони будуть підвантажуватись окремо оскільки
                # не при кожному запиті вони наб будуть необхідні)
            )
            res = session.execute(query) # тут виконується сама query(логічний один запит по типу select * from workers..)
            result = res.scalars().all()
            
            worker_1_resumes = result[0].resumes # а вже на цьому місці де ми звертаємось до резюме, буде відбуватись підгрузка
            print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes # на цьому теж

            # висновок такий що в нас крім основного запиту буде додаватись N запитів пов'язаних з remumes. тобто "проблема N+1" !!!
            # щоб уникнути такого переробляєм даний метод в екземпляр нижче
            
            print(worker_2_resumes)
    
    @staticmethod
    def select_workers_with_joined_relationship() -> None:
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(joinedload(WorkersOrm.resumes)) # в опціях прописуєм зробити join з relationship-ом resume(прописаний в models)
                #                                          завдяки цьому буде робитись один великий запит без подальших підгрузок
                
                #                                          з joinedload є проблема оскільки він підходиться для join-ів
                #                                          m2o, o2o  ішими словами просто "TO ONE" а нам потрібен m2o, реалізація в методі нижче
            )
            res = session.execute(query)
            result = res.unique().scalars().all() # unique() запит на рівні пайтона та алхімії(запит нікуди не відправляється),
            #                                       потрібен для відсіювання тільки унікальних pk значень
            worker_1_resumes = result[0].resumes  # вже тут не буде ніяких доп підгрузок
            print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes  # і тут теж
            print(worker_2_resumes)
    
    @staticmethod
    def select_workers_with_selectin_relationship() -> None:
        with session_factory() as session:
            query = (
                select(WorkersOrm)                         # відбувається 1 великий запит, перевага в тому що ми не будемо ганяти великий трафік)
                .options(selectinload(WorkersOrm.resumes)) # selectinload - відповідає за join-и m2m, o2m  ішими словами просто "TO MANY"
            )
            res = session.execute(query)
            result = res.scalars().all()
            
            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)
    
    @staticmethod
    def select_workers_with_condition_relationship() -> None:
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes_parttime))
                # .options(selectinload(WorkersOrm.resumes)) # <- для підгрузки кількох relationships
            )
            res = session.execute(query)
            result = res.scalars().all()
            
            print(result)
    
    @staticmethod
    def select_workers_with_condition_relationship_contains_eager() -> None:
        with session_factory() as session:
            query = (
                select(WorkersOrm)
                .join(WorkersOrm.resumes)
                .options(contains_eager(WorkersOrm.resumes)) # просимо contains_eager підтянути звідти(WorkersOrm.resumes) таблицю ResumesOrm
                # щоб в результаті отримати не табличну структуру, а вкладену(вложеная) структуру
                .filter(ResumesOrm.workload == 'parttime')
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            
            print(result)
    
    @staticmethod
    def select_workers_with_condition_relationship_contains_eager_with_limit() -> None:
        with session_factory() as session:
            subq = (
                select(ResumesOrm.id.label("parttime_resume_id"))
                .filter(ResumesOrm.worker_id == WorkersOrm.id)
                .order_by(WorkersOrm.id.desc())
                .limit(1) # встановлення ліміту по отриманню запитів column-у зі стовбця (aka тільки ПЕРШИЙ результат)
                .scalar_subquery() # оскільки в нас 1 об'єкт(?) Перетворює цей запит у підзапит, який повертає єдине значення
                .correlate(WorkersOrm) # Оголошуємо, що цей підзапит пов’язаний із зовнішньою таблицею WorkersOrm.
                # Це дозволяє SQLAlchemy правильно побудувати запит, вказуючи, що підзапит залежить від зовнішньої таблиці.
            )
            
            query = (
                select(WorkersOrm)
                .join(ResumesOrm, ResumesOrm.id.in_(subq))
                # Ми з'єднуємо таблиці WorkersOrm і ResumesOrm, використовуючи підзапит subq.
                # Логіка така:

                # У підзапиті ми отримали id резюме, яке відповідає певному працівнику.
                # Тепер фільтруємо таблицю ResumesOrm, залишаючи лише ті записи, чиї id співпадають із результатами підзапиту.
                
                .options(contains_eager(WorkersOrm.resumes))
                # Вказуємо SQLAlchemy, що потрібно завантажити зв’язану інформацію (resumes) разом із працівниками.
                # Це оптимізує виконання запиту, щоб уникнути додаткових запитів для отримання резюме.
            )
            
            res = session.execute(query)
            result = res.unique().scalars().all()
            
            print(result)
    



class AsyncORM:
    @staticmethod
    async def create_tables() -> None:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def insert_workers() -> None:
        async with async_session_factory() as session:
            worker_beaver = WorkersOrm(username="Beaver")
            worker_wolf = WorkersOrm(username="Wolf")
            session.add_all([worker_beaver, worker_wolf])
            await session.flush()
            await session.commit()
    
    @staticmethod
    async def select_workers() -> None:
        async with async_session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Squirrel") -> None:
        async with async_session_factory() as session:
            worker_beaver = await session.get(WorkersOrm, worker_id)
            worker_beaver.username = new_username
            # await session.refresh(worker_beaver)
            await session.commit()
    
    @staticmethod
    async def insert_resumes() -> None:
        async with async_session_factory() as session:
            resume_beaver_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=Workload.fulltime, worker_id=1)
            resume_beaver_2 = ResumesOrm(
                title="Python Developer", compensation=150000, workload=Workload.fulltime, worker_id=1)
            resume_squirrel_1 = ResumesOrm(
                title="Python Data Engineer", compensation=250000, workload=Workload.parttime, worker_id=2)
            resume_squirrel_2 = ResumesOrm(
                title="Data Scientist", compensation=300000, workload=Workload.fulltime, worker_id=2)
            session.add_all([resume_beaver_1, resume_beaver_2, resume_squirrel_1, resume_squirrel_2])
            await session.commit()
    
    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = "Python") -> None:
        async with async_session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    func.avg(ResumesOrm.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.compensation > 40000,
                ))
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(result)
            print(result[0].avg_compensation)
    
    @staticmethod
    async def insert_additional_resumes() -> None:
        async with async_session_factory() as session:
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
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            await session.execute(insert_workers)
            await session.execute(insert_resumes)
            await session.commit()
    
    @staticmethod
    async def join_cte_subquery_window_func() -> None:
        async with async_session_factory() as session:
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation"),
                )
                .join(r, r.worker_id == w.id).subquery("helper1")
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
            res = await session.execute(query)
            result = res.all()
            print(f"{result=}")

    @staticmethod
    async def select_workers_with_lazy_relationship() -> None:
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
            )
            res = await session.execute(query)
            result = res.scalars().all()
            
            # worker_1_resumes = result[0].resumes  # -> Приведе до помилки
            # Не можна використовувати ліниву підгрузку в асинхронному варіанті!

            # Помилка: sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. 
            # Was IO attempted in an unexpected place? (Background on this error at: https://sqlalche.me/e/20/xd2s)
    
    @staticmethod
    async def select_workers_with_joined_relationship() -> None:
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(joinedload(WorkersOrm.resumes))
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            
            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)
    
    @staticmethod
    async def select_workers_with_selectin_relationship() -> None:
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes))
            )
            res = await session.execute(query)
            result = res.scalars().all()
            
            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)
    
    @staticmethod
    async def select_workers_with_condition_relationship() -> None:
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes_parttime))
            )
            res = await session.execute(query)
            result = res.scalars().all()
            
            print(result)
    
    @staticmethod
    async def select_workers_with_condition_relationship_contains_eager() -> None:
        async with async_session_factory() as session:
            # Горячо рекомендую ознакомиться: https://stackoverflow.com/a/72298903/22259413 
            query = (
                select(WorkersOrm)
                .join(WorkersOrm.resumes)
                .options(contains_eager(WorkersOrm.resumes))
                .filter(ResumesOrm.workload == 'parttime')
            )
            res = await session.execute(query)
            result = res.unique().scalars().all()
            
            print(result)
    
    @staticmethod
    async def select_workers_with_condition_relationship_contains_eager_with_limit() -> None:
        async with async_session_factory() as session:
            subq = (
                select(ResumesOrm.id.label("parttime_resume_id"))
                .filter(ResumesOrm.worker_id == WorkersOrm.id)
                .order_by(WorkersOrm.id.desc())
                .limit(1)
                .scalar_subquery()
                .correlate(WorkersOrm)
            )
            
            query = (
                select(WorkersOrm)
                .join(ResumesOrm, ResumesOrm.id.in_(subq))
                .options(contains_eager(WorkersOrm.resumes))
            )
            
            res = await session.execute(query)
            result = res.unique().scalars().all()
            
            print(result)