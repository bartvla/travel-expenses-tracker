import models  # noqa: F401 - sam import rejestruje tabele w Base.metadata
from database import Base, engine


def reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    reset_schema()
    print("Schemat odtworzony.")
