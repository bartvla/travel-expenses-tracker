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
npm run dev
```

Frontend wykorzystuje typescript + React. Aktualnie wyświetla wiadomość pobraną z backendu.

Uruchamia się pod adresem: http://localhost:5173/
