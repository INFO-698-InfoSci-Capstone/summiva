from fastapi import FastAPI
from api.endpoints.auth import router

app = FastAPI(title="Authentication Service")
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "Auth Service is running!"}
