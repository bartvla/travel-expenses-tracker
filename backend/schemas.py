from datetime import date, datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TripCreate(BaseModel):
    """Dane przyjmowane w POST /api/trips oraz PUT /api/trips/{trip_id}."""

    name: str = Field(min_length=1, max_length=120)
    destination: str | None = Field(default=None, max_length=120)
    start_date: date
    end_date: date | None = None
    currency: str = Field(min_length=3, max_length=3)
    budget: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None

    @model_validator(mode="after")
    def check_date_order(self) -> Self:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date nie moze byc wczesniejsze niz start_date")
        return self


class TripRead(BaseModel):
    """Dane zwracane przez API. Wypelniane z obiektu ORM, nie z zadania."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination: str | None
    start_date: date
    end_date: date | None
    currency: str
    budget: Decimal | None
    notes: str | None
    created_at: datetime

class ExpenseCreate(BaseModel):
    """Dane przyjmowane w POST /api/trips/{trip_id}/expenses oraz PUT /api/expenses/{expense_id}."""

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    spent_on: date
    description: str | None = Field(default=None, max_length=255)

class ExpenseRead(BaseModel):
    """Dane wydatku zwracane przez API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    amount: Decimal
    spent_on: date
    description: str | None
    created_at: datetime