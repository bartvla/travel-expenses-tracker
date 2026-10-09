# travel-expenses-tracker

## Backend
Uruchomienie:

```sh
cd backend
uv run fastapi dev main.py
```

Backend korzysta z biblioteki fastapi do tworzenia API. Środowisko jest zarządzane za pomocą narzędzia uv.

Serwuje endpoint `GET /api/message` na http://127.0.0.1:8000.

## Frontend
Uruchomienie:

```sh
cd frontend
npm install   # wymagane przy pierwszym uruchomieniu
npm run dev
```

Frontend wykorzystuje typescript + React. Aktualnie wyświetla wiadomość pobraną z backendu.

Uruchamia się pod adresem: http://localhost:5173/


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
