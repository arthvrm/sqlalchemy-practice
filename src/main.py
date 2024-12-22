import asyncio
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], ".."))
# from queries.core import create_tables, insert_data, get_123_sync
from queries.orm import create_tables, insert_data

"""це основний файл з якого будем запускати аплікуху"""
create_tables()
# insert_data()
# asyncio.run(insert_data())
