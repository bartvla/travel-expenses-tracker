# travel-expenses-tracker

Aplikacja do śledzenia wydatków z podróży: frontend (React) + backend (FastAPI) + baza danych w kontenerze.

## Wymagania

- Docker z wtyczką Compose
- [uv](https://docs.astral.sh/uv/) — zarządzanie środowiskiem backendu
- Node.js — frontend

## Konfiguracja

Przed pierwszym uruchomieniem utwórz plik `.env` na podstawie szablonu i ustaw w nim własne hasło:

```sh
cp .env.example .env
```

Plik `.env` leży w katalogu głównym repozytorium i jest wczytywany w dwóch miejscach:

- `compose.yaml` podstawia z niego zmienne `POSTGRES_*` do kontenera bazy,
- `backend/database.py` czyta z niego `DATABASE_URL` (przez `python-dotenv`).

Hasło występuje w `.env` dwa razy — osobno w `POSTGRES_PASSWORD` i wewnątrz `DATABASE_URL`. Obie wartości muszą być identyczne, inaczej backend nie uwierzytelni się w bazie.

`.env` jest w `.gitignore` i nie trafia do repozytorium. Do repozytorium trafia tylko `.env.example`.

## Baza danych

PostgreSQL 17 działa w kontenerze opisanym w `compose.yaml`. Uruchomienie z katalogu głównego repozytorium:

```sh
docker compose up -d
```

Sprawdzenie, czy kontener wstał:

```sh
docker compose ps
```

Połączenie z bazą z linii poleceń (apostrofy są konieczne — zmienne mają się podstawić w kontenerze, nie na hoście):

```sh
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Zatrzymanie:

```sh
docker compose down
```

Dane bazy przechowuje wolumen `data` i przeżywają `docker compose down`. Żeby skasować bazę razem z zawartością:

```sh
docker compose down -v
```

Zmienne `POSTGRES_*` są odczytywane wyłącznie przy pierwszej inicjalizacji wolumenu. Jeśli zmienisz użytkownika lub hasło w `.env` już po utworzeniu bazy, trzeba usunąć wolumen (`docker compose down -v`), a potem postawić kontener na nowo — w przeciwnym razie backend dostanie `password authentication failed`.

## Backend

Baza musi być uruchomiona przed startem backendu.

```sh
cd backend
uv run fastapi dev main.py
```

Backend korzysta z FastAPI, a dostęp do bazy realizuje przez SQLAlchemy ORM (sterownik `psycopg`). Środowisko jest zarządzane za pomocą narzędzia uv.

Serwuje na http://127.0.0.1:8000:

- `GET /api/message` — wiadomość testowa dla frontendu,
- `GET /api/health/db` — zwraca `{"db": "ok"}`, jeśli połączenie z bazą działa.

## Frontend

```sh
cd frontend
npm install   # wymagane przy pierwszym uruchomieniu
npm run dev
```

Frontend wykorzystuje TypeScript + React. Aktualnie wyświetla wiadomość pobraną z backendu. Żądania `/api/*` są przekierowywane przez proxy Vite na http://127.0.0.1:8000.

Uruchamia się pod adresem: http://localhost:5173/

## Model danych

#### `users` – użytkownicy

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | UUID | tak | Klucz główny |
| `email` | VARCHAR(255) | tak | Adres e-mail, unikalny |
| `password_hash` | VARCHAR(255) | tak | Skrót hasła (hasło nigdy nie jest zapisywane jawnie) |
| `display_name` | VARCHAR(80) | tak | Nazwa wyświetlana |
| `default_currency` | CHAR(3) | tak | Domyślna waluta użytkownika, kod ISO 4217 (np. `PLN`) |
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia konta |

#### `trips` – podróże

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | UUID | tak | Klucz główny |
| `user_id` | UUID | tak | Właściciel podróży, klucz obcy do `users.id` |
| `name` | VARCHAR(120) | tak | Nazwa podróży, np. „Lizbona 2026” |
| `destination` | VARCHAR(120) | nie | Kraj lub miasto |
| `start_date` | DATE | tak | Pierwszy dzień podróży |
| `end_date` | DATE | nie | Ostatni dzień podróży, nie wcześniejszy niż `start_date` |
| `base_currency` | CHAR(3) | tak | Waluta podsumowań, kod ISO 4217 |
| `budget` | DECIMAL(12,2) | nie | Planowany budżet w walucie podróży |
| `notes` | TEXT | nie | Notatki |
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia |
| `updated_at` | TIMESTAMP (UTC) | tak | Data ostatniej zmiany |

#### `expenses` – wydatki

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | UUID | tak | Klucz główny |
| `trip_id` | UUID | tak | Podróż, klucz obcy do `trips.id` (usuwanie kaskadowe) |
| `category_id` | UUID | tak | Kategoria, klucz obcy do `categories.id` |
| `amount` | DECIMAL(12,2) | tak | Kwota w walucie, w której zapłacono; większa od zera |
| `currency` | CHAR(3) | tak | Waluta płatności, kod ISO 4217 (np. `EUR`) |
| `exchange_rate` | DECIMAL(18,8) | tak | Kurs użyty do przeliczenia na walutę podróży |
| `amount_base` | DECIMAL(12,2) | tak | Kwota przeliczona na walutę podróży, zapisana na stałe |
| `spent_on` | DATE | tak | Dzień wydatku |
| `description` | VARCHAR(255) | nie | Opis, np. „Kolacja” |
| `payment_method` | ENUM | tak | `cash`, `card`, `transfer` lub `other`; domyślnie `card` |
| `merchant` | VARCHAR(120) | nie | Miejsce lub sprzedawca |
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia |
| `updated_at` | TIMESTAMP (UTC) | tak | Data ostatniej zmiany |

#### `categories` – kategorie wydatków

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | UUID | tak | Klucz główny |
| `user_id` | UUID | nie | Właściciel kategorii, klucz obcy do `users.id`; puste oznacza kategorię systemową |
| `name` | VARCHAR(60) | tak | Nazwa, unikalna w obrębie użytkownika |
| `icon` | VARCHAR(40) | nie | Nazwa ikony używanej przez frontend |
| `color` | CHAR(7) | nie | Kolor w formacie `#RRGGBB` |

Kategorie systemowe: transport, nocleg, jedzenie, atrakcje, zakupy, inne.

#### Relacje

- Użytkownik ma wiele podróży (`users.id` → `trips.user_id`).
- Użytkownik może mieć wiele własnych kategorii (`users.id` → `categories.user_id`).
- Podróż ma wiele wydatków (`trips.id` → `expenses.trip_id`).
- Każdy wydatek należy do jednej kategorii (`categories.id` → `expenses.category_id`).
