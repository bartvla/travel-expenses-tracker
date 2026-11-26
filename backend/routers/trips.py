import json
import os
from typing import Annotated

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/trips", tags=["trips"])

DbSession = Annotated[Session, Depends(get_db)]

cache = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379/0"),
    decode_responses=True,
)
CACHE_KEY = "trips:all"


def get_trip_or_404(trip_id: int, db: Session) -> models.Trips:
    """Wspolny lookup dla endpointow operujacych na jednej podrozy."""
    trip = db.get(models.Trips, trip_id)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Podroz nie istnieje")
    return trip


@router.get("", response_model=list[schemas.TripRead])
def list_trips(db: DbSession):
    """GET lista zasobow z cache'owaniem w Redisie."""
    cached = cache.get(CACHE_KEY)
    if cached:
        print("CACHE HIT (Redis)")
        return json.loads(cached)

    print("CACHE MISS (PostgreSQL)")
    stmt = select(models.Trips).order_by(models.Trips.start_date.desc())
    trips = list(db.scalars(stmt))

    data = jsonable_encoder(trips)
    cache.set(CACHE_KEY, json.dumps(data), ex=60)
    return data


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
    db.refresh(trip)
    cache.delete(CACHE_KEY)
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
    cache.delete(CACHE_KEY)
    return trip


@router.delete("/{trip_id}", status_code=200)
def delete_trip(trip_id: int, db: DbSession) -> dict[str, int]:
    """DELETE zasob. Wydatki znikaja kaskadowo (ondelete=CASCADE)."""
    trip = get_trip_or_404(trip_id, db)
    db.delete(trip)
    db.commit()
    cache.delete(CACHE_KEY)
    return {"Succesfully deleted ID": trip_id}