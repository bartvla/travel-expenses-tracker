from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db, Base, engine
from metrics import setup_metrics
from routers import trips, expenses


app = FastAPI(title="travel-expenses-tracker")

DbSession = Annotated[Session, Depends(get_db)]

Base.metadata.create_all(engine)

setup_metrics(app)

app.include_router(trips.router)
app.include_router(expenses.router)

@app.get("/api/health")
def db_health(db: DbSession) -> dict[str,str]:
    """Show if databse is up and running"""
    db.execute(text("SELECT 1"))
    return {"db": "ok"}