"""
FAISS Vector Index Module
=========================
Production-level implementation of FAISS vector indexing and semantic search
for fast and efficient similarity queries at scale.
"""

import os
import faiss
import numpy as np
import pickle
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger("search.faiss")

# Constants for configuration
DEFAULT_MODEL = "all-MiniLM-L6-v2"
DEFAULT_INDEX_DIR = os.path.join(os.path.dirname(__file__), "../models/faiss")
DEFAULT_INDEX_PATH = os.path.join(DEFAULT_INDEX_DIR, "summiva.index")
DEFAULT_DOC_IDS_PATH = os.path.join(DEFAULT_INDEX_DIR, "doc_ids.npy")
DEFAULT_DOC_MAP_PATH = os.path.join(DEFAULT_INDEX_DIR, "doc_map.pkl")

class FAISSIndexManager:
    """
    Production-ready FAISS index manager for vector similarity search
    with proper resource management and error handling.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(FAISSIndexManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        index_path: str = DEFAULT_INDEX_PATH,
        doc_ids_path: str = DEFAULT_DOC_IDS_PATH,
        doc_map_path: str = DEFAULT_DOC_MAP_PATH
    ):
        """Initialize the FAISS index manager"""
        # Only initialize once (singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.model_name = model_name
        self.index_path = index_path
        self.doc_ids_path = doc_ids_path
        self.doc_map_path = doc_map_path
        
        # Components initialized on demand
        self._model = None
        self._index = None
        self._doc_ids = None
        self._doc_map = None
        
        # Create directory structure if needed
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        logger.info(f"Initialized FAISSIndexManager with model: {model_name}")
        self._initialized = True
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the embedding model"""
        if self._model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            start_time = time.time()
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded in {time.time() - start_time:.2f}s")
        return self._model
    
    @property
    def index(self) -> Optional[faiss.Index]:
        """Lazy-load the FAISS index"""
        if self._index is None:
            self.load_index()
        return self._index
    
    @property
    def doc_ids(self) -> Optional[np.ndarray]:
        """Lazy-load the document IDs"""
        if self._doc_ids is None and self._index is not None:
            self.load_doc_ids()
        return self._doc_ids
    
    @property
    def doc_map(self) -> Optional[Dict[int, Any]]:
        """Lazy-load the document mapping"""
        if self._doc_map is None and self._index is not None:
            self.load_doc_map()
        return self._doc_map
    
    def load_index(self) -> Optional[faiss.Index]:
        """Load FAISS index from disk"""
        try:
            if os.path.exists(self.index_path):
                logger.info(f"Loading FAISS index from {self.index_path}")
                start_time = time.time()
                self._index = faiss.read_index(self.index_path)
                logger.info(f"FAISS index loaded with {self._index.ntotal} vectors in {time.time() - start_time:.2f}s")
                return self._index
            else:
                logger.warning(f"FAISS index not found at {self.index_path}")
                self._index = None
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            self._index = None
        return None
    
    def load_doc_ids(self) -> Optional[np.ndarray]:
        """Load document IDs from disk"""
        try:
            if os.path.exists(self.doc_ids_path):
                logger.info(f"Loading document IDs from {self.doc_ids_path}")
                self._doc_ids = np.load(self.doc_ids_path)
                logger.info(f"Loaded {len(self._doc_ids)} document IDs")
                return self._doc_ids
            else:
                logger.warning(f"Document IDs not found at {self.doc_ids_path}")
                self._doc_ids = None
        except Exception as e:
            logger.error(f"Error loading document IDs: {str(e)}")
            self._doc_ids = None
        return None
    
    def load_doc_map(self) -> Optional[Dict[int, Any]]:
        """Load document mapping from disk"""
        try:
            if os.path.exists(self.doc_map_path):
                logger.info(f"Loading document mapping from {self.doc_map_path}")
                with open(self.doc_map_path, 'rb') as f:
                    self._doc_map = pickle.load(f)
                logger.info(f"Loaded mapping for {len(self._doc_map)} documents")
                return self._doc_map
            else:
                logger.info(f"No document mapping found at {self.doc_map_path}, using empty map")
                self._doc_map = {}
        except Exception as e:
            logger.error(f"Error loading document mapping: {str(e)}")
            self._doc_map = {}
        return self._doc_map
    
    def create_new_index(self, dimension: int = 384) -> faiss.Index:
        """Create a new FAISS index"""
        logger.info(f"Creating new FAISS index with dimension {dimension}")
        self._index = faiss.IndexFlatL2(dimension)
        self._doc_ids = np.array([], dtype=np.int64)
        self._doc_map = {}
        return self._index
    
    def get_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for input text"""
        try:
            start_time = time.time()
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            logger.debug(f"Generated embeddings in {time.time() - start_time:.2f}s")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return empty embedding with correct dimensions
            if isinstance(text, list):
                return np.zeros((len(text), self.model.get_sentence_embedding_dimension()))
            else:
                return np.zeros(self.model.get_sentence_embedding_dimension())
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        text_key: str = "text",
        id_key: str = "id",
        metadata_keys: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to the index
        
        Args:
            documents: List of document dictionaries
            text_key: Key for text content in documents
            id_key: Key for document IDs
            metadata_keys: Optional keys to store in document map
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not documents:
                logger.warning("No documents provided to add to index")
                return True
                
            # Extract text and IDs
            texts = [doc.get(text_key, "") for doc in documents]
            doc_ids = [doc.get(id_key, i) for i, doc in enumerate(documents)]
            
            # Generate embeddings
            embeddings = self.get_embedding(texts)
            embeddings = embeddings.astype(np.float32)  # FAISS requires float32
            
            # Create index if not existing
            if self._index is None:
                self.create_new_index(embeddings.shape[1])
                
            # Get next ID
            next_id = self._index.ntotal
            
            # Add to FAISS index
            self._index.add(embeddings)
            
            # Create or extend doc_ids array to map FAISS IDs to doc IDs
            if self._doc_ids is None or len(self._doc_ids) == 0:
                self._doc_ids = np.array(doc_ids)
            else:
                self._doc_ids = np.concatenate([self._doc_ids, doc_ids])
                
            # Add metadata to doc_map if requested
            if metadata_keys:
                if self._doc_map is None:
                    self._doc_map = {}
                    
                for i, doc in enumerate(documents):
                    faiss_id = next_id + i
                    doc_id = doc_ids[i]
                    
                    metadata = {"id": doc_id}
                    for key in metadata_keys:
                        if key in doc:
                            metadata[key] = doc[key]
                            
                    self._doc_map[faiss_id] = metadata
            
            # Save updated index and mappings
            self.save()
            
            logger.info(f"Added {len(documents)} documents to FAISS index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {str(e)}")
            return False
    
    def save(self) -> bool:
        """Save index and mappings to disk"""
        try:
            if self._index is not None:
                # Create directories if needed
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                
                # Save FAISS index
                faiss.write_index(self._index, self.index_path)
                logger.info(f"Saved FAISS index with {self._index.ntotal} vectors")
                
                # Save document IDs
                if self._doc_ids is not None:
                    np.save(self.doc_ids_path, self._doc_ids)
                    logger.info(f"Saved {len(self._doc_ids)} document IDs")
                    
                # Save document mapping
                if self._doc_map is not None:
                    with open(self.doc_map_path, 'wb') as f:
                        pickle.dump(self._doc_map, f)
                    logger.info(f"Saved mapping for {len(self._doc_map)} documents")
                    
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        k: int = 10,
        return_documents: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on the index
        
        Args:
            query: Search query text
            k: Number of results to return
            return_documents: Whether to include document metadata
            
        Returns:
            List of search results with scores
        """
        try:
            # Make sure index is loaded
            if self.index is None or self.doc_ids is None:
                logger.warning("FAISS index or document IDs not loaded")
                return []
                
            # Cap k to number of vectors in index
            k = min(k, self._index.ntotal) if self._index.ntotal > 0 else k
            
            # If index is empty, return empty results
            if self._index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return []
                
            # Generate query embedding
            embedding = self.get_embedding(query)
            embedding = embedding.astype(np.float32).reshape(1, -1)
            
            # Search the index
            start_time = time.time()
            distances, indices = self._index.search(embedding, k)
            search_time = time.time() - start_time
            
            # Process results
            results = []
            for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                # Convert L2 distance to cosine similarity (approximation)
                # For normalized vectors: similarity ≈ 1 - distance/2
                similarity = max(0.0, 1.0 - float(distance) / 2.0)
                
                # Get document ID
                if idx >= 0 and idx < len(self._doc_ids):
                    doc_id = self._doc_ids[idx]
                    
                    result = {
                        "id": doc_id,
                        "score": similarity,
                        "rank": i + 1
                    }
                    
                    # Add document metadata if requested
                    if return_documents and self._doc_map is not None:
                        doc_info = self._doc_map.get(int(idx), {})
                        if doc_info:
                            result["document"] = doc_info
                            
                    results.append(result)
            
            logger.debug(f"FAISS search completed in {search_time:.3f}s with {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {str(e)}")
            return []
    
    def semantic_search(
        self,
        text: str,
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Legacy method for backward compatibility"""
        return self.search(text, k)
    
    def cleanup(self):
        """Release resources used by the index manager"""
        self._model = None
        self._index = None
        self._doc_ids = None
        self._doc_map = None
        
        # Force garbage collection
        import gc
        gc.collect()
        
        logger.info("FAISS index manager resources cleaned up")

# Initialize singleton instance with default settings
faiss_manager = FAISSIndexManager()

# Legacy functions for backward compatibility
def load_index() -> Tuple[Optional[faiss.Index], Optional[np.ndarray]]:
    """Legacy function for backward compatibility"""
    index = faiss_manager.index
    doc_ids = faiss_manager.doc_ids
    return index, doc_ids

def semantic_search(text: str, k=10) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    return faiss_manager.search(text, k)

# Keep model reference for backward compatibility
model = faiss_manager.model
