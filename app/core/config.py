from dataclasses import dataclass
import os


@dataclass
class Settings:
    """Application configuration
    """

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://medivue:medivuepassword@localhost:5432/medivue_db",
    )


settings = Settings()
