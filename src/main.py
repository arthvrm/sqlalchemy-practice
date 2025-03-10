import asyncio
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(1, os.path.join(sys.path[0], ".."))
# from queries.core import create_tables, insert_data, get_123_sync
from queries.orm import SyncORM, AsyncORM
from queries.core import SyncCore, AsyncCore

# create_tables()
# insert_data()
# asyncio.run(insert_data())


def sync_core_main() -> None:
    SyncCore.create_tables()
    SyncCore.insert_workers()
    SyncCore.insert_resumes()
    SyncCore.update_worker()
    SyncCore.select_workers()
    SyncCore.select_resumes_avg_compensation()
    SyncCore.insert_additional_resumes()
    SyncCore.join_cte_subquery_window_func()


def sync_orm_main() -> None:
    SyncORM.create_tables()
    SyncORM.insert_workers()
    SyncORM.insert_resumes()
    SyncORM.update_worker()
    SyncORM.select_workers()
    SyncORM.select_resumes_avg_compensation()
    SyncORM.insert_additional_resumes()
    SyncORM.join_cte_subquery_window_func()
    SyncORM.select_workers_with_lazy_relationship()
    SyncORM.select_workers_with_joined_relationship()
    SyncORM.select_workers_with_selectin_relationship()
    SyncORM.select_workers_with_condition_relationship()
    SyncORM.select_workers_with_condition_relationship_contains_eager()
    SyncORM.select_workers_with_condition_relationship_contains_eager_with_limit()
    SyncORM.add_vacancies_and_replies()
    SyncORM.select_resumes_with_all_relationships()


async def async_core_main() -> None:
    await AsyncCore.create_tables()
    await AsyncCore.insert_workers()
    await AsyncCore.insert_resumes()
    await AsyncCore.update_worker()
    await AsyncCore.select_workers()
    await AsyncCore.select_resumes_avg_compensation()
    await AsyncCore.insert_additional_resumes()
    await AsyncCore.join_cte_subquery_window_func()


async def async_orm_main() -> None:
    await AsyncORM.create_tables()
    await AsyncORM.insert_workers()
    await AsyncORM.insert_resumes()
    await AsyncORM.update_worker()
    await AsyncORM.select_workers()
    await AsyncORM.select_resumes_avg_compensation()
    await AsyncORM.insert_additional_resumes()
    await AsyncORM.join_cte_subquery_window_func()
    await AsyncORM.select_workers_with_lazy_relationship()
    await AsyncORM.select_workers_with_joined_relationship()
    await AsyncORM.select_workers_with_selectin_relationship()
    await AsyncORM.select_workers_with_condition_relationship()
    await AsyncORM.select_workers_with_condition_relationship_contains_eager()
    await AsyncORM.select_workers_with_condition_relationship_contains_eager_with_limit()
    await AsyncORM.add_vacancies_and_replies()
    await AsyncORM.select_resumes_with_all_relationships()


# Executing
async def main():
    if "--core" in sys.argv and "--sync" in sys.argv:
        sync_core_main()
    
    elif "--orm" in sys.argv and "--sync" in sys.argv:
        sync_orm_main()
    
    elif "--core" in sys.argv and "--async" in sys.argv:
        await async_core_main()
    
    elif "--orm" in sys.argv and "--async" in sys.argv:
        await async_orm_main()


def create_fastapi_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,      # це шар між клієнтом і сервером, який перехоплює запити та відповіді для виконання певних дій 
        allow_origins=["*"], # Дозволяє запити з будь-якого домену 
    )

    @app.get("/workers")
    async def get_workers():
        workers = await AsyncORM.convert_workers_to_dto()
        return workers

    @app.get("/resumes")
    async def get_resumes():
        resumes = SyncORM.select_resumes_with_all_relationships()
        return resumes

    return app


app = create_fastapi_app() # initialisation


if __name__ == "__main__":
    asyncio.run(main())
    if "--webserver" in sys.argv:
        uvicorn.run(
            app="src.main:app",
            reload=True,
        )