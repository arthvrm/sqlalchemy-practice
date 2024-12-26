import asyncio
import os
import sys
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


def sync_orm_main() -> None:
    SyncORM.create_tables()

    SyncORM.insert_workers()

    SyncORM.insert_resumes()

    SyncORM.update_worker()

    SyncORM.select_workers()

    SyncORM.select_resumes_avg_compensation()



async def async_core_main() -> None:
    await AsyncCore.create_tables()

    await AsyncCore.insert_workers()

    await AsyncCore.insert_resumes()

    await AsyncCore.update_worker()

    await AsyncCore.select_workers()

    await AsyncCore.select_resumes_avg_compensation()


async def async_orm_main() -> None:
    await AsyncORM.create_tables()

    await AsyncORM.insert_workers()

    await AsyncORM.insert_resumes()

    await AsyncORM.update_worker()

    await AsyncORM.select_workers()

    await AsyncORM.select_resumes_avg_compensation()



# Executing
# sync_core_main()
sync_orm_main()

# asyncio.run(async_core_main())
# asyncio.run(async_orm_main())