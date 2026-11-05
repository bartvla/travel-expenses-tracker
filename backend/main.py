from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from routers import trips


app = FastAPI(title="travel-expenses-tracker")

DbSession = Annotated[Session, Depends(get_db)]

app.include_router(trips.router)


@app.get("/api/health")
def db_health(db: DbSession) -> dict[str,str]:
    db.execute(text("SELECT 1"))
    return {"db": "ok"}