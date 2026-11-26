# travel-expenses-tracker

Aplikacja do śledzenia wydatków z podróży: frontend (React) + backend (FastAPI) + baza danych w kontenerze.

## Wymagania

- Docker z wtyczką Compose — wystarcza do uruchomienia całej aplikacji.

Tylko do pracy nad kodem poza kontenerami:

- [uv](https://docs.astral.sh/uv/) — zarządzanie środowiskiem backendu,
- Node.js — frontend.

## Konfiguracja

Przed pierwszym uruchomieniem utwórz plik `.env` na podstawie szablonu i ustaw w nim własne hasło:

```sh
cp .env.example .env
```

Plik `.env` leży w katalogu głównym repozytorium i jest wczytywany inaczej w zależności od trybu uruchomienia:

- **W kontenerach** `compose.yaml` podstawia z `.env` zmienne `POSTGRES_*` do kontenera bazy i buduje z nich `DATABASE_URL` dla backendu (host bazy to `db`). Sam plik `.env` nie trafia do obrazu — jest na liście `backend/.dockerignore`.
- **Lokalnie, poza Dockerem** `backend/database.py` czyta `DATABASE_URL` z `.env` przez `python-dotenv`.

Hasło występuje w `.env` dwa razy — osobno w `POSTGRES_PASSWORD` i wewnątrz `DATABASE_URL`. Obie wartości muszą być identyczne, inaczej backend uruchomiony lokalnie nie uwierzytelni się w bazie.

`.env` jest w `.gitignore` i nie trafia do repozytorium. Do repozytorium trafia tylko `.env.example`.

## Uruchomienie

Cała aplikacja — baza, backend i frontend — startuje jedną komendą z katalogu głównego repozytorium:

```sh
docker compose up -d
```

Sprawdzenie, czy wszystkie trzy kontenery wstały:

```sh
docker compose ps
```

Adresy po uruchomieniu:

| Usługa | Adres |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| Interaktywna dokumentacja API | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

Baza nie publikuje portu na hosta — jest dostępna wyłącznie dla backendu, przez wewnętrzną sieć compose `backend-net`.

Zatrzymanie:

```sh
docker compose down
```

Po zmianie kodu backendu lub frontendu obrazy trzeba przebudować:

```sh
docker compose up -d --build
```

## Baza danych

PostgreSQL 17 działa w kontenerze opisanym w `compose.yaml`.

Połączenie z bazą z linii poleceń (apostrofy są konieczne — zmienne mają się podstawić w kontenerze, nie na hoście):

```sh
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Dane bazy przechowuje nazwany wolumen `data` i przeżywają `docker compose down`. Żeby skasować bazę razem z zawartością:

```sh
docker compose down -v
```

Zmienne `POSTGRES_*` są odczytywane wyłącznie przy pierwszej inicjalizacji wolumenu. Jeśli zmienisz użytkownika lub hasło w `.env` już po utworzeniu bazy, trzeba usunąć wolumen (`docker compose down -v`), a potem postawić kontener na nowo — w przeciwnym razie backend dostanie `password authentication failed`.

## Backend

Backend korzysta z FastAPI, a dostęp do bazy realizuje przez SQLAlchemy ORM (sterownik `psycopg`). Środowisko jest zarządzane za pomocą narzędzia uv.

W kontenerze startuje automatycznie razem z resztą stacku (`docker compose up -d`) i czeka na bazę przez `depends_on: condition: service_healthy`.

Do pracy lokalnej, z przeładowywaniem kodu — baza musi być uruchomiona, a `DATABASE_URL` w `.env` musi wskazywać na adres osiągalny z hosta:

```sh
cd backend
uv run fastapi dev main.py
```

Pełna lista endpointów w sekcji [API](#api).

## Frontend

Frontend to React (JavaScript, pliki `.jsx`) budowany Vite. Ma dwa ekrany: listę podróży i szczegóły wybranej podróży z jej wydatkami. Dane pobiera wyłącznie z API backendu, przez funkcje w `src/api.js`.

Żądania `/api/*` przechodzą przez proxy Vite na `http://backend:8000` (`vite.config.js`). Nazwa `backend` rozwiązuje się tylko wewnątrz sieci compose, dlatego **frontend uruchamia się przez Dockera**, razem z resztą stacku:

```sh
docker compose up -d
```

Serwuje pod http://localhost:5173/.

Uruchomienie przez `npm run dev` na hoście postawi serwer deweloperski, ale każde żądanie do API padnie — proxy nie znajdzie hosta `backend`. Żeby pracować tak nad frontendem, trzeba najpierw zmienić `target` proxy w `vite.config.js` na `http://127.0.0.1:8000` i uruchomić backend lokalnie.

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
| `created_at` | TIMESTAMP (UTC) | tak | Data utworzenia |

#### Relacje

- Podróż ma wiele wydatków (`trips.id` → `expenses.trip_id`). Usunięcie podróży usuwa jej wydatki.

### Skrypt inicjalizujący

`backend/reset_db.py` odtwarza schemat od zera i wstawia dane startowe: pięć podróży wraz z ich wydatkami (11 rekordów w `expenses`). **Kasuje wszystkie dane** — tabele są najpierw usuwane, a potem tworzone na nowo.

Uruchomienie w kontenerze backendu (baza nie ma opublikowanego portu, więc z hosta jest nieosiągalna):

```sh
docker compose exec backend python reset_db.py
```

Uruchomienie lokalnie, poza Dockerem — wymaga bazy dostępnej pod adresem z `DATABASE_URL`:

```sh
cd backend
uv run python reset_db.py
```

## API

Formatem wymiany danych jest **JSON** — zarówno w ciele żądania, jak i w odpowiedzi. Żądania z ciałem wymagają nagłówka `Content-Type: application/json`. Interaktywna dokumentacja (OpenAPI) jest pod http://localhost:8000/docs.

Wszystkie ścieżki mają prefiks `/api`.

| Metoda | Ścieżka | Opis | Kod przy sukcesie |
|---|---|---|---|
| GET | `/api/health` | Stan aplikacji i połączenia z bazą | 200 |
| GET | `/api/trips` | Lista podróży, od najnowszej `start_date` | 200 |
| GET | `/api/trips/{trip_id}` | Jedna podróż | 200 |
| POST | `/api/trips` | Nowa podróż | 201 |
| PUT | `/api/trips/{trip_id}` | Nadpisanie całej podróży | 200 |
| DELETE | `/api/trips/{trip_id}` | Usunięcie podróży wraz z jej wydatkami | 200 |
| GET | `/api/trips/{trip_id}/expenses` | Wydatki danej podróży, od najnowszego `spent_on` | 200 |
| POST | `/api/trips/{trip_id}/expenses` | Nowy wydatek w podróży | 201 |
| PUT | `/api/expenses/{expense_id}` | Nadpisanie całego wydatku | 200 |
| DELETE | `/api/expenses/{expense_id}` | Usunięcie wydatku | 200 |

## Monitoring

Metryki zbiera **Prometheus**, a wykresy rysuje **Grafana**. Obie usługi startują razem z resztą stacku (`docker compose up -d`) i nie wymagają żadnej konfiguracji w UI.

### Zbierane metryki

| Metryka | Typ | Opis |
|---|---|---|
| `http_requests_total{handler,method,status}` | Counter | Łączna liczba żądań. Licznik tylko rośnie, więc sama wartość niewiele mówi — sens ma dopiero `rate()`, czyli liczba żądań na sekundę |
| `http_request_duration_seconds{handler,method}` | Histogram | Czas odpowiedzi w koszykach; z koszyków `histogram_quantile()` wylicza percentyle |
| `http_request_size_bytes`, `http_response_size_bytes` | Summary | Rozmiary żądań i odpowiedzi |

Etykieta `handler` zawiera **wzorzec ścieżki** (`/api/trips/{trip_id}`), a nie konkretne id. Gdyby trafiało tam `/api/trips/7`, każda podróż tworzyłaby osobną serię czasową i liczba serii rosłaby w nieskończoność.

Granice koszyków histogramu ustawia `LATENCY_BUCKETS` w `backend/metrics.py`. Domyślne koszyki biblioteki to `(0.1, 0.5, 1)` — przy lokalnym API wszystkie żądania wpadają do pierwszego z nich, więc p95 zawsze wychodzi 0,095 s i wykres jest płaską linią. Dlatego progi są zagęszczone poniżej 100 ms.

Podgląd surowych metryk:

```sh
curl -s localhost:8000/metrics | head -40
```

### Panele dashboardu

Dashboard **Travel Expenses – backend** jest dostępny w Grafanie od razu po starcie. Ma dwa panele:

| Panel | Zapytanie PromQL | Co pokazuje |
|---|---|---|
| Żądania na sekundę wg endpointu | `sum by (handler) (rate(http_requests_total{job="backend"}[1m]))` | Natężenie ruchu na każdym endpoincie, uśrednione z ostatniej minuty |
| Czas odpowiedzi p95 wg endpointu | `histogram_quantile(0.95, sum by (le, handler) (rate(http_request_duration_seconds_bucket{job="backend"}[5m])))` | 95. percentyl czasu odpowiedzi — 95% żądań jest obsłużonych szybciej niż pokazana wartość |

Świeżo uruchomiony dashboard jest pusty, bo `rate()` potrzebuje co najmniej dwóch odczytów w oknie czasowym. Żeby zobaczyć dane, trzeba wygenerować ruch i odczekać kilkanaście sekund:

```sh
for i in $(seq 1 200); do curl -s -o /dev/null localhost:8000/api/trips; sleep 0.3; done
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

## wymagania dot. bazy danych (ujawniane KM2):

- gotowy oficjalny obraz, np. : postgres, mysql, mongo
- dane trwałe na nazwanym wolumenie
- minimum dwie powiązane tabele lub kolekcje
- skrypt inicjalizujący: schemat i dane startowe
- brak opublikowanego portu; baza dostępna dla backend przez sieć compose

## wymagania dot. frontendu (ujawniane KM2):

- min. dwa ekrany / widoki
- komunikacja wyłącznie z API backendu
- własny Dockerfile (nie tylko bind mount)

## wymagania dot. monitoringu (ujawniane KM3):

- Prometheus + Grafana w compose
- endpoint `/metrics` na backendzie
- scrape metryk backendu przez Prometheusa
- dashboard w Grafanie z min. 2 panelami
