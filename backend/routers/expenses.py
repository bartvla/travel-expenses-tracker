from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from routers.trips import get_trip_or_404

router = APIRouter(prefix="/api", tags=["expenses"])

DbSession = Annotated[Session, Depends(get_db)]


def get_expense_or_404(expense_id: int, db: Session) -> models.Expenses:
    """Wspolny lookup dla endpointow operujacych na jednym wydatku."""
    expense = db.get(models.Expenses, expense_id)
    if expense is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Wydatek nie istnieje")
    return expense


@router.get("/trips/{trip_id}/expenses", response_model=list[schemas.ExpenseRead])
def list_expenses(trip_id: int, db: DbSession) -> list[models.Expenses]:
    """GET lista wydatkow przypisanych do danej podrozy."""
    get_trip_or_404(trip_id, db)
    stmt = (select(models.Expenses).where(models.Expenses.trip_id == trip_id).order_by(models.Expenses.spent_on.desc(), models.Expenses.id.desc()))
    return list(db.scalars(stmt))


@router.post("/trips/{trip_id}/expenses", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(trip_id: int, payload: schemas.ExpenseCreate, db: DbSession) -> models.Expenses:
    """POST nowy wydatek w ramach podrozy."""
    get_trip_or_404(trip_id, db)
    expense = models.Expenses(trip_id=trip_id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.put("/expenses/{expense_id}", response_model=schemas.ExpenseRead)
def replace_expense(expense_id: int, payload: schemas.ExpenseCreate, db: DbSession) -> models.Expenses:
    """PUT nadpisuje caly wydatek."""
    expense = get_expense_or_404(expense_id, db)
    for field, value in payload.model_dump().items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=200)
def delete_expense(expense_id: int, db: DbSession) -> dict[str, int]:
    """DELETE pojedynczy wydatek."""
    expense = get_expense_or_404(expense_id, db)
    db.delete(expense)
    db.commit()
    return {"Succesfully deleted ID": expense_id}