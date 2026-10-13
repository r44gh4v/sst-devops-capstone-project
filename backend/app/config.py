from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Expense Tracker API"
    database_url: str = "postgresql+psycopg://expenses:expenses@localhost:5432/expenses"


settings = Settings()
