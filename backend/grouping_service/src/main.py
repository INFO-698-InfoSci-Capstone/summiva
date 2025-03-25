from fastapi import FastAPI
from src.api.endpoints.grouping import router as grouping_router

app = FastAPI(title="Grouping Service")

@app.get("/")
def health_check():
    return {"status": "Grouping Service healthy"}

app.include_router(grouping_router)
