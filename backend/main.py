from fastapi import FastAPI

app = FastAPI(title="travel-expenses-tracker")


@app.get("/api/message")
def read_message() -> dict[str, str]:
    return {"message": "Hello from the backend!"}
