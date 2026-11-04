import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class PaymentMethod(enum.Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"
    other = "other"

class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    default_currency: Mapped[str] = mapped_column(CHAR(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trips: Mapped[list["Trips"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    categories: Mapped[list["Categories"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Trips(Base):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_trips_date_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str | None] = mapped_column(String(120))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    base_currency: Mapped[str] = mapped_column(CHAR(3))
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["Users"] = relationship(back_populates="trips")
    expenses: Mapped[list["Expenses"]] = relationship(back_populates="trip", cascade="all, delete-orphan")

class Categories(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    icon: Mapped[str | None] = mapped_column(String(40))
    color: Mapped[str | None] = mapped_column(CHAR(7))

    user: Mapped["Users | None"] = relationship(back_populates="categories")
    expenses: Mapped[list["Expenses"]] = relationship(back_populates="category")

class Expenses(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(CHAR(3))
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    amount_base: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    spent_on: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(String(255))
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method"), server_default=PaymentMethod.card.name
    )
    merchant: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trip: Mapped["Trips"] = relationship(back_populates="expenses")
    category: Mapped["Categories"] = relationship(back_populates="expenses")
