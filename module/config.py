import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_SCHEMA: str

    @property
    def DATABASE_URL_psycopg2(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=ENV_PATH,
                                      extra='ignore')


# DSN для подключения к БД (переменные окружения)
try:
    settings = Settings()
except Exception as e:
    exit(f"error in module: {__name__}: {e}")

if __name__ == "__main__":
    import os

    settings = Settings()
    print(settings.DATABASE_URL_psycopg2)
