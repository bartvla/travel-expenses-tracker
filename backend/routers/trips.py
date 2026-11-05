from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/trips", tags=["trips"])

DbSession = Annotated[Session, Depends(get_db)]


def get_trip_or_404(trip_id: int, db: Session) -> models.Trips:
    """Wspolny lookup dla endpointow operujacych na jednej podrozy."""
    trip = db.get(models.Trips, trip_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Podroz nie istnieje")
    return trip


@router.get("", response_model=list[schemas.TripRead])
def list_trips(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[models.Trips]:
    """GET lista zasobow, z paginacja."""
    stmt = (
        select(models.Trips)
        .order_by(models.Trips.start_date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


@router.get("/{trip_id}", response_model=schemas.TripRead)
def get_trip(trip_id: int, db: DbSession) -> models.Trips:
    """GET pojedynczy zasob. Nieistniejace id -> 404."""
    return get_trip_or_404(trip_id, db)


@router.post("", response_model=schemas.TripRead, status_code=status.HTTP_201_CREATED)
def create_trip(payload: schemas.TripCreate, db: DbSession) -> models.Trips:
    """POST nowy zasob."""
    trip = models.Trips(**payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)  # dociaga id i created_at nadane przez baze
    return trip


@router.put("/{trip_id}", response_model=schemas.TripRead)
def replace_trip(
    trip_id: int, payload: schemas.TripCreate, db: DbSession
) -> models.Trips:
    """PUT nadpisuje caly zasob."""
    trip = get_trip_or_404(trip_id, db)
    for field, value in payload.model_dump().items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: DbSession) -> None:
    """DELETE zasob. Wydatki znikaja kaskadowo (ondelete=CASCADE)."""
    trip = get_trip_or_404(trip_id, db)
    db.delete(trip)
    db.commit()
