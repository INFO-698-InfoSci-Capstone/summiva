from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import torch
from pathlib import Path
import logging

from config.base import BaseConfig
from utils.paths import path_manager
from core.config.settings import settings

config = BaseConfig()
app = FastAPI(title="Model Server")
logger = logging.getLogger(__name__)

# Model registry
MODEL_REGISTRY: Dict[str, Any] = {}

class ModelServer:
    def __init__(self):
        self.model_dir = settings.MODEL_DOWNLOAD_DIR
        self._ensure_model_directories()
    
    def _ensure_model_directories(self):
        """Ensure all required model directories exist."""
        # Ensure model download directory exists
        path_manager.ensure_dir(self.model_dir)
        
        # Create subdirectories for different model types
        self.summarization_dir = path_manager.ensure_dir(self.model_dir / 'summarization')
        self.tagging_dir = path_manager.ensure_dir(self.model_dir / 'tagging')
        self.clustering_dir = path_manager.ensure_dir(self.model_dir / 'clustering')
    
    def get_model_path(self, model_type: str, model_name: str) -> Path:
        """
        Get the path for a specific model.
        
        Args:
            model_type: Type of model (summarization, tagging, clustering)
            model_name: Name of the model
            
        Returns:
            Path: Path to the model directory
        """
        model_type_dir = getattr(self, f"{model_type}_dir")
        return path_manager.ensure_dir(model_type_dir / model_name)
    
    def get_faiss_paths(self) -> tuple[Path, Path]:
        """Get paths for FAISS index and document mapping."""
        return settings.FAISS_INDEX_PATH, settings.FAISS_DOC_MAP_PATH

# Global model server instance
model_server = ModelServer()

def load_model(model_type: str, model_path: str) -> Any:
    """Load a model from the specified path."""
    try:
        if model_type == "summarization":
            # Load summarization model
            model = torch.load(model_path)
        elif model_type == "tagging":
            # Load tagging model
            model = torch.load(model_path)
        elif model_type == "grouping":
            # Load grouping model
            model = torch.load(model_path)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    try:
        # Load models from config
        model_dir = Path(config.MODEL_DOWNLOAD_DIR)
        if not model_dir.exists():
            model_dir.mkdir(parents=True)
        
        # Load each model type
        for model_type in ["summarization", "tagging", "grouping"]:
            model_path = model_dir / f"{model_type}_model.pt"
            if model_path.exists():
                MODEL_REGISTRY[model_type] = load_model(model_type, str(model_path))
                logger.info(f"Loaded {model_type} model")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "models_loaded": list(MODEL_REGISTRY.keys())}

@app.get("/models/{model_type}")
async def get_model(model_type: str):
    """Get information about a specific model."""
    if model_type not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="Model not found")
    return {
        "model_type": model_type,
        "status": "loaded",
        "device": str(next(MODEL_REGISTRY[model_type].parameters()).device)
    } 
