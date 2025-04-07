from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Summiva API",
    description="Enterprise-scale NLP system for summarization, tagging, and search",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and include routers
from summarization_service.routes import router as summarization_router
from tagging_service.routes import router as tagging_router
from search_service.routes import router as search_router
from grouping_service.routes import router as grouping_router
from auth_service.routes import router as auth_router

app.include_router(summarization_router, prefix="/api/v1/summarize", tags=["Summarization"])
app.include_router(tagging_router, prefix="/api/v1/tag", tags=["Tagging"])
app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(grouping_router, prefix="/api/v1/group", tags=["Grouping"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"]) 
