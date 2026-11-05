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

Serwuje na http://127.0.0.1:8000. Pełna lista endpointów w sekcji [API](#api), interaktywna dokumentacja pod http://127.0.0.1:8000/docs.

## Frontend

```sh
cd frontend
npm install   # wymagane przy pierwszym uruchomieniu
npm run dev
```

Frontend wykorzystuje TypeScript + React. Aktualnie wyświetla wiadomość pobraną z backendu. Żądania `/api/*` są przekierowywane przez proxy Vite na http://127.0.0.1:8000.

Uruchamia się pod adresem: http://localhost:5173/

## Model danych

Aplikacja jest jednoosobowa — nie ma kont użytkowników ani logowania. Kwoty w jednej walucie na podróż, bez przeliczania kursów.

#### `trips` – podróże

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | SERIAL | tak | Klucz główny, nadawany przez bazę |
| `name` | VARCHAR(120) | tak | Nazwa podróży, np. „Lizbona 2026” |
| `destination` | VARCHAR(120) | nie | Kraj lub miasto |
| `start_date` | DATE | tak | Pierwszy dzień podróży |
| `end_date` | DATE | nie | Ostatni dzień podróży, nie wcześniejszy niż `start_date` |
| `currency` | VARCHAR(3) | tak | Waluta podróży, kod ISO 4217 (np. `EUR`) |
| `budget` | DECIMAL(12,2) | nie | Planowany budżet |
| `notes` | TEXT | nie | Notatki |
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia |

#### `expenses` – wydatki

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `id` | SERIAL | tak | Klucz główny, nadawany przez bazę |
| `trip_id` | INTEGER | tak | Podróż, klucz obcy do `trips.id` (usuwanie kaskadowe) |
| `amount` | DECIMAL(12,2) | tak | Kwota w walucie podróży; większa od zera |
| `spent_on` | DATE | tak | Dzień wydatku |
| `description` | VARCHAR(255) | nie | Opis, np. „Kolacja” |
| `category` | VARCHAR(60) | nie | Kategoria jako zwykły tekst, np. „jedzenie” |
| `payment_method` | ENUM | tak | `cash`, `card`, `transfer` lub `other`; domyślnie `card` |
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia |

#### Relacje

- Podróż ma wiele wydatków (`trips.id` → `expenses.trip_id`). Usunięcie podróży usuwa jej wydatki.

Odtworzenie schematu od zera (kasuje wszystkie dane):

```sh
cd backend
uv run python reset_db.py
```

## wymagania dot. backendu (ujawniane KM1):

- min. 4 endpointy
    - GET: pojedynczy zasób
    - GET: lista zasobów
    - POST
    - PUT/PATCH lub DELETE
- format wymiany danych: JSON, udokumentowany w README
- podstawowa walidacja danych wejściowych, np. kod 400 przy błędnych danych
- kod 404 dla nieistniejącego zasobu
- endpoint /health
- healthcheck w compose korzystający z /health oraz depends_on: condition: service_healthy
- konfiguracja przez zmienne środowiskowe