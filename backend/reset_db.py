import models
from database import Base, SessionLocal, engine

SYSTEM_CATEGORIES = ["transport", "nocleg", "jedzenie", "atrakcje", "zakupy", "inne"]


def reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def seed_system_categories() -> None:
    with SessionLocal() as session:
        session.add_all(
            [models.Categories(user_id=None, name=name) for name in SYSTEM_CATEGORIES]
        )
        session.commit()


if __name__ == "__main__":
    reset_schema()
    seed_system_categories()
    print(f"Schemat odtworzony, wstawiono {len(SYSTEM_CATEGORIES)} kategorii systemowych.")
