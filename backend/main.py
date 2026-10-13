from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
app = FastAPI(title="travel-expenses-tracker")

DbSession = Annotated[Session, Depends(get_db)]

@app.get("/api/message")
def read_message() -> dict[str, str]:
    return {"message": "Hello from the backend!"}


@app.get("/api/health/db")
def db_health(db: DbSession) -> dict[str,str]:
    db.execute(text("SELECT 1"))
    return {"db": "ok"}