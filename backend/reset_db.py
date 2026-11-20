from datetime import date
from decimal import Decimal

import models
from database import Base, SessionLocal, engine


def reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def seed_data() -> None:
    """Dane startowe: piec podrozy, kazda z kilkoma wydatkami."""
    trips = [
        models.Trips(
            name="Lizbona 2026",
            destination="Portugalia",
            start_date=date(2026, 4, 12),
            end_date=date(2026, 4, 19),
            currency="EUR",
            budget=Decimal("2400.00"),
            notes="Nocleg w Alfamie, karta Viva Viagem na metro.",
            expenses=[
                models.Expenses(
                    amount=Decimal("680.00"),
                    spent_on=date(2026, 4, 12),
                    description="Loty w obie strony",
                ),
                models.Expenses(
                    amount=Decimal("54.50"),
                    spent_on=date(2026, 4, 13),
                    description="Kolacja w Bairro Alto",
                ),
                models.Expenses(
                    amount=Decimal("31.00"),
                    spent_on=date(2026, 4, 15),
                    description="Bilety do klasztoru Hieronimitow",
                ),
            ],
        ),
        models.Trips(
            name="Tatry zimowe",
            destination="Zakopane",
            start_date=date(2026, 1, 30),
            end_date=date(2026, 2, 2),
            currency="PLN",
            budget=Decimal("1500.00"),
            notes="Raki i czekan wypozyczone na miejscu.",
            expenses=[
                models.Expenses(
                    amount=Decimal("420.00"),
                    spent_on=date(2026, 1, 30),
                    description="Schronisko, trzy noce",
                ),
                models.Expenses(
                    amount=Decimal("160.00"),
                    spent_on=date(2026, 1, 31),
                    description="Wypozyczenie sprzetu",
                ),
            ],
        ),
        models.Trips(
            name="Berlin na weekend",
            destination="Niemcy",
            start_date=date(2025, 11, 7),
            end_date=date(2025, 11, 9),
            currency="EUR",
            budget=Decimal("600.00"),
            notes=None,
            expenses=[
                models.Expenses(
                    amount=Decimal("89.00"),
                    spent_on=date(2025, 11, 7),
                    description="Pociag Berlin Express",
                ),
                models.Expenses(
                    amount=Decimal("142.00"),
                    spent_on=date(2025, 11, 7),
                    description="Hostel, dwie noce",
                ),
                models.Expenses(
                    amount=Decimal("18.00"),
                    spent_on=date(2025, 11, 8),
                    description="Muzeum Pergamonskie",
                ),
            ],
        ),
        models.Trips(
            name="Objazd Islandii",
            destination="Islandia",
            start_date=date(2026, 7, 3),
            end_date=date(2026, 7, 17),
            currency="ISK",
            budget=Decimal("52000.00"),
            notes="Ring Road kampervanem, noclegi na kempingach.",
            expenses=[
                models.Expenses(
                    amount=Decimal("21000.00"),
                    spent_on=date(2026, 7, 3),
                    description="Wynajem kampervana",
                ),
                models.Expenses(
                    amount=Decimal("3450.00"),
                    spent_on=date(2026, 7, 5),
                    description="Paliwo, pierwszy tydzien",
                ),
            ],
        ),
        models.Trips(
            name="Praga sluzbowo",
            destination="Czechy",
            start_date=date(2026, 3, 2),
            end_date=None,
            currency="CZK",
            budget=None,
            notes="Konferencja, termin powrotu jeszcze nieustalony.",
            expenses=[
                models.Expenses(
                    amount=Decimal("4200.00"),
                    spent_on=date(2026, 3, 2),
                    description="Hotel przy centrum kongresowym",
                ),
            ],
        ),
    ]

    with SessionLocal() as session:
        session.add_all(trips)
        session.commit()


if __name__ == "__main__":
    reset_schema()
    seed_data()
    print("Schemat odtworzony, dane startowe wstawione.")
