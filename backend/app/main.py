from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Expense
from .schemas import ExpenseIn, ExpenseOut, Summary

app = FastAPI(title=settings.app_name, version="1.0.0")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def find_expense(expense_id: int, db: Session) -> Expense:
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "READY"}


@app.get("/api/expenses", response_model=list[ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.scalars(select(Expense).order_by(Expense.spent_on.desc(), Expense.id.desc())).all()


@app.get("/api/expenses/summary", response_model=Summary)
def summary(db: Session = Depends(get_db)):
    rows = db.execute(select(Expense.category, func.sum(Expense.amount), func.count(Expense.id)).group_by(Expense.category)).all()
    by_category = {category: round(total, 2) for category, total, _ in rows}
    return Summary(total=round(sum(by_category.values()), 2), count=sum(count for *_, count in rows), by_category=by_category)


@app.get("/api/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return find_expense(expense_id, db)


@app.post("/api/expenses", response_model=ExpenseOut, status_code=201)
def create_expense(data: ExpenseIn, db: Session = Depends(get_db)):
    expense = Expense(**data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.put("/api/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, data: ExpenseIn, db: Session = Depends(get_db)):
    expense = find_expense(expense_id, db)
    for key, value in data.model_dump().items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db.delete(find_expense(expense_id, db))
    db.commit()
