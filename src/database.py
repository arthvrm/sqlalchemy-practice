import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import URL, create_engine, text
from config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,                         # вивід логів у консоль
    # pool_size=5,                     # макс к-сть доступних підключень
    # max_overflow=10,                 # якщо всі підключення будуть зайняті тоді буде додано ще N вільних підключень
)


async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
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