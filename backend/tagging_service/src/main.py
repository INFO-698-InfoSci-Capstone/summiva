from fastapi import FastAPI
from src.api.endpoints.tagging import router as tagging_router

app = FastAPI(title="Tagging Service")

@app.get("/")
def health_check():
    return {"status": "Tagging Service is healthy"}

app.include_router(tagging_router)
