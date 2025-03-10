from pydantic_settings import BaseSettings, SettingsConfigDict

# нижче валідуються/підставляються змінні, потім визначаються посилання для з'єднань(сесій) з БД які будуть взаємодіяти з алхімією
class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    
    @property # property(set_value, get_value, delete_value) <- всередині все це функції які надають доступ до __змінної через інкапсуляцію
    def DATABASE_URL_asyncpg(self) -> str:
        # DSN - назва рядка нижче
        # postgresql+asyncpg://postgres:password13@localhost:5432/example_db
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_psycopg(self) -> str:
        # DSN
        # postgresql+psycopg://postgres:password13@localhost:5432/example_db
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
