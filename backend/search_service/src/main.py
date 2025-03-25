from fastapi import FastAPI
from src.api.endpoints.search import router as search_router

app = FastAPI(title="Search Service")
app.include_router(search_router)

@app.get("/")
def health():
    return {"status": "Search service operational"}
