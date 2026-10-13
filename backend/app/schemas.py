from datetime import date

from pydantic import BaseModel, ConfigDict, Field

CATEGORIES = ("Food", "Travel", "Bills", "Shopping", "Other")


class ExpenseIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    category: str = Field(pattern="^(Food|Travel|Bills|Shopping|Other)$")
    spent_on: date


class ExpenseOut(ExpenseIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Summary(BaseModel):
    total: float
    count: int
    by_category: dict[str, float]
