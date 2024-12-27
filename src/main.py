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
    SyncCore.insert_additional_resumes()


def sync_orm_main() -> None:
    SyncORM.create_tables()
    SyncORM.insert_workers()
    SyncORM.insert_resumes()
    SyncORM.update_worker()
    SyncORM.select_workers()
    SyncORM.select_resumes_avg_compensation()
    SyncORM.insert_additional_resumes()


async def async_core_main() -> None:
    await AsyncCore.create_tables()
    await AsyncCore.insert_workers()
    await AsyncCore.insert_resumes()
    await AsyncCore.update_worker()
    await AsyncCore.select_workers()
    await AsyncCore.select_resumes_avg_compensation()
    await AsyncCore.insert_additional_resumes()


async def async_orm_main() -> None:
    await AsyncORM.create_tables()
    await AsyncORM.insert_workers()
    await AsyncORM.insert_resumes()
    await AsyncORM.update_worker()
    await AsyncORM.select_workers()
    await AsyncORM.select_resumes_avg_compensation()
    await AsyncORM.insert_additional_resumes()


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
    

if __name__ == "__main__":
    asyncio.run(main())