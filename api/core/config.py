from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Настройки приложения.
    
    Attributes:
        POSTGRES_DB: Название базы данных PostgreSQL
        POSTGRES_USER: Имя пользователя PostgreSQL
        POSTGRES_PASSWORD: Пароль пользователя PostgreSQL
        POSTGRES_HOST: Хост базы данных
        POSTGRES_PORT: Порт базы данных
    """
    
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    @property
    def database_url(self) -> str:
        """Формирует URL для подключения к базе данных.
        
        Returns:
            str: DSN строка для подключения к PostgreSQL
        """
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = ConfigDict(env_file='.env', case_sensitive=False)


settings = Settings()