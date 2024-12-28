import asyncio
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy import URL, String, create_engine, text
from config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,                         # вивід логів у консоль
    # pool_size=5,                     # макс к-сть доступних підключень
    # max_overflow=10,                 # якщо всі підключення будуть зайняті тоді буде додано ще N вільних підключень
)


async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
)

"""код нище був перенесений в core.py"""
# with sync_engine.connect() as conn:                                 # engine.begin -> return COMMIT, .connect -> return ROLLBACK
#     res = conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6")) # використовується функція text() для перетворення рядка в текст оскільки обробка SQL-запитів зазвичай - обробка простого тексту
#     print(f"{res.all()[0]=}")
#     # conn.commit()                                                 # той самий COMMIT краще робити вручну


# async def get_123() -> None:                                                  # async <- для створення асинхронної функції (корутини(по ідеї))
#     async with async_engine.connect() as conn:                                # with...as(контекстний менеджер) <- для правильного закриття любих з'єднань/файлів
#         res = await conn.execute(text("SELECT 1, 2, 3 union select 4, 5, 6")) # await <- оскільки отримання результату виконується асинхронно в асинхронній функції
#         print(f"{res.all()[0]=}")
#         # conn.commit()

# asyncio.run(get_123()) # запуск асинхронної функції(такто створюється event_loop(?) в який надходять async-функції для їхнього почергового(*) виконання)


session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)

str_255 = Annotated[str, 255]# [str, mapped_column(String(255))]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_255: String(255)
    }
    
    repr_cols_num = 3
    repr_cols = tuple()
    
    def __repr__(self):
        """Relationships не використовуються в repr() оскільки можуть призвести до неочікуваних підвантажень"""
        cols = []
        # [cols.append(col) for col in self.__table__.columns.keys()] # secret code here yehehehehee
        
        # for col in self.__table__.columns.keys():
        #     cols.append(f"{col}={getattr(self, col)}") # getattr() - дістає значання атрибуту
        
        """reworked code here""" #(its very cool tho!😎)
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        
        return f"<{self.__class__.__name__} {', '.join(cols)}>"