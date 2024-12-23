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

SyncORM.create_tables()
# SyncCore.create_tables()

SyncORM.insert_workers()
# SyncCore.insert_workers()

SyncORM.update_worker()
# SyncCore.update_worker()

SyncORM.select_workers()
# SyncCore.select_workers()



# async def main():
#     await AsyncORM.create_tables()
#     # await AsyncCore.create_tables()
    
#     # await AsyncORM.insert_workers()
#     await AsyncCore.insert_workers()
    
#     # await AsyncORM.update_worker()
#     await AsyncCore.update_worker()

#     # await AsyncORM.select_workers()
#     await AsyncCore.select_workers()

# # Execute the main function
# asyncio.run(main())