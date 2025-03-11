from fastapi import FastAPI
from api.endpoints.summarize import router as summarize_router

app = FastAPI(title="Summarization Service (Celery, External Auth)")

@app.get("/")
def health_check():
    return {"status": "Summarization Service running with Celery + RabbitMQ, external Auth!"}

# Summarization endpoints
app.include_router(summarize_router)
