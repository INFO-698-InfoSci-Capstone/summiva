"""
Document Grouping Module
======================
Implements document grouping and clustering using FAISS and KMeans
for efficient vector similarity search and clustering.
"""
import os
import numpy as np
import pickle
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

# Vector embedding
from sentence_transformers import SentenceTransformer

# FAISS for efficient similarity search
import faiss

# Scikit-learn for KMeans clustering
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# Constants
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2
DEFAULT_NUM_CLUSTERS = 10
SIMILARITY_THRESHOLD = 0.75
INDEX_PATH = os.path.join(os.path.dirname(__file__), "../models/faiss_index")
KMEANS_PATH = os.path.join(os.path.dirname(__file__), "../models/kmeans_model.pkl")

# Configure logging
logger = logging.getLogger("grouping.core")

class DocumentGrouper:
    """
    Production-level document grouping system using FAISS and KMeans
    for efficient similarity search and clustering.
    """
    
    def __init__(
        self,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        embedding_dim: int = DEFAULT_EMBEDDING_DIM,
        num_clusters: int = DEFAULT_NUM_CLUSTERS,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        index_path: str = INDEX_PATH,
        kmeans_path: str = KMEANS_PATH
    ):
        """
        Initialize the DocumentGrouper with configurable parameters
        
        Args:
            embedding_model: Name of the SentenceTransformer model to use
            embedding_dim: Dimension of embeddings
            num_clusters: Number of clusters to use for KMeans
            similarity_threshold: Threshold for considering documents similar
            index_path: Path to save/load FAISS index
            kmeans_path: Path to save/load KMeans model
        """
        self.embedding_model_name = embedding_model
        self.embedding_dim = embedding_dim
        self.num_clusters = num_clusters
        self.similarity_threshold = similarity_threshold
        self.index_path = index_path
        self.kmeans_path = kmeans_path
        
        # Initialize components to None - will be loaded on demand
        self.embedding_model = None
        self.index = None
        self.kmeans = None
        self.id_to_data_map = {}  # Maps FAISS IDs to original document data
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        logger.info(f"Initialized DocumentGrouper with model: {embedding_model}")
        
    def _load_embedding_model(self):
        """Load the sentence transformer embedding model on first use"""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            start_time = time.time()
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Embedding model loaded in {time.time() - start_time:.2f} seconds")
    
    def get_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text using SentenceTransformers
        
        Args:
            text: Text or list of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        self._load_embedding_model()
        
        # Handle empty input
        if not text:
            if isinstance(text, list):
                return np.zeros((0, self.embedding_dim))
            return np.zeros(self.embedding_dim)
        
        try:
            start_time = time.time()
            embeddings = self.embedding_model.encode(
                text, 
                convert_to_numpy=True, 
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            logger.debug(f"Generated {embeddings.shape[0]} embeddings in {time.time() - start_time:.2f}s")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            if isinstance(text, list):
                return np.zeros((len(text), self.embedding_dim))
            return np.zeros(self.embedding_dim)
    
    def _init_faiss_index(self) -> faiss.Index:
        """
        Initialize a new FAISS index for similarity search
        
        Returns:
            FAISS index
        """
        # Use L2 distance (squared euclidean) for normalized vectors
        index = faiss.IndexFlatL2(self.embedding_dim)
        
        # For larger datasets, consider using approximate nearest neighbors
        # with IndexIVFFlat for better scaling
        # quantizer = faiss.IndexFlatL2(self.embedding_dim)
        # index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
        # index.train(sample_vectors)
        
        return index
    
    def load_or_create_index(self) -> faiss.Index:
        """
        Load existing FAISS index or create a new one
        
        Returns:
            FAISS index
        """
        if self.index is not None:
            return self.index
            
        try:
            if os.path.exists(self.index_path):
                logger.info(f"Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
                
                # Load document mapping if available
                mapping_path = self.index_path + ".mapping"
                if os.path.exists(mapping_path):
                    with open(mapping_path, 'rb') as f:
                        self.id_to_data_map = pickle.load(f)
                        
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                logger.info("Creating new FAISS index")
                self.index = self._init_faiss_index()
                
            return self.index
            
        except Exception as e:
            logger.error(f"Error loading/creating FAISS index: {str(e)}")
            logger.info("Creating new FAISS index after failure")
            self.index = self._init_faiss_index()
            return self.index
    
    def load_or_train_kmeans(self, embeddings: Optional[np.ndarray] = None) -> KMeans:
        """
        Load existing KMeans model or train a new one
        
        Args:
            embeddings: Optional sample embeddings to train on
            
        Returns:
            KMeans model
        """
        if self.kmeans is not None:
            return self.kmeans
            
        try:
            if os.path.exists(self.kmeans_path):
                logger.info(f"Loading KMeans model from {self.kmeans_path}")
                with open(self.kmeans_path, 'rb') as f:
                    self.kmeans = pickle.load(f)
            elif embeddings is not None and embeddings.shape[0] >= self.num_clusters:
                # Train new model
                logger.info(f"Training new KMeans model with {self.num_clusters} clusters")
                start_time = time.time()
                
                # Cap the number of clusters to the number of samples
                n_clusters = min(self.num_clusters, embeddings.shape[0])
                
                self.kmeans = KMeans(
                    n_clusters=n_clusters,
                    init='k-means++',
                    n_init=10,
                    random_state=42
                )
                self.kmeans.fit(embeddings)
                
                # Save the model
                with open(self.kmeans_path, 'wb') as f:
                    pickle.dump(self.kmeans, f)
                    
                logger.info(f"KMeans model trained in {time.time() - start_time:.2f} seconds")
            else:
                # Create dummy model that will be trained later
                self.kmeans = KMeans(
                    n_clusters=self.num_clusters,
                    init='k-means++',
                    n_init=10,
                    random_state=42
                )
                
            return self.kmeans
            
        except Exception as e:
            logger.error(f"Error loading/training KMeans model: {str(e)}")
            # Create fallback model
            self.kmeans = KMeans(
                n_clusters=self.num_clusters,
                init='k-means++',
                n_init=10,
                random_state=42
            )
            return self.kmeans
    
    def add_documents(self, docs: List[Dict[str, Any]], texts_key: str = "text", ids_key: str = "id") -> bool:
        """
        Add documents to the index
        
        Args:
            docs: List of document dictionaries
            texts_key: Key for extracting text from documents
            ids_key: Key for document IDs
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not docs:
                logger.warning("No documents provided to add_documents")
                return True
                
            # Extract texts and IDs
            texts = [doc.get(texts_key, "") for doc in docs]
            ids = [doc.get(ids_key, i) for i, doc in enumerate(docs)]
            
            # Generate embeddings
            embeddings = self.get_embedding(texts)
            
            # Ensure the embeddings are float32 (required by FAISS)
            embeddings = embeddings.astype(np.float32)
            
            # Load or create index
            index = self.load_or_create_index()
            
            # Generate sequential IDs for FAISS
            start_id = len(self.id_to_data_map)
            faiss_ids = np.arange(start_id, start_id + len(docs), dtype=np.int64)
            
            # Add vectors to index
            index.add_with_ids(embeddings, faiss_ids)
            
            # Update the mapping
            for i, doc_id in enumerate(ids):
                faiss_id = start_id + i
                self.id_to_data_map[int(faiss_id)] = {
                    "id": doc_id,
                    "text": texts[i],
                    "doc": docs[i]
                }
            
            # Save the updated index and mapping
            self._save_index()
            
            logger.info(f"Added {len(docs)} documents to FAISS index, total now: {index.ntotal}")
            
            # Retrain KMeans if we have enough documents
            if index.ntotal >= self.num_clusters:
                self._retrain_kmeans()
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {str(e)}")
            return False
    
    def find_similar_documents(
        self, 
        query_text: str, 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to the query text
        
        Args:
            query_text: Query text
            k: Number of similar documents to return
            
        Returns:
            List of similar document dicts with similarity scores
        """
        try:
            # Generate query embedding
            query_emb = self.get_embedding(query_text)
            query_emb = query_emb.astype(np.float32).reshape(1, -1)  # Reshape for single query
            
            # Load index
            index = self.load_or_create_index()
            
            # Handle empty index case
            if index.ntotal == 0:
                logger.warning("No documents in index to search")
                return []
                
            # Limit k to the number of documents in the index
            k = min(k, index.ntotal)
            
            # Search for similar vectors
            distances, indices = index.search(query_emb, k)
            
            # Process results
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                distance = distances[0][i]
                
                # Convert L2 distance to similarity score (approximation)
                # For normalized vectors, similarity ~ 1 - distance/2
                similarity = max(0.0, 1.0 - distance / 2)
                
                # Skip low similarity results
                if similarity < self.similarity_threshold:
                    continue
                    
                # Get document data
                doc_data = self.id_to_data_map.get(int(idx), {})
                if not doc_data:
                    continue
                    
                results.append({
                    "id": doc_data.get("id"),
                    "text": doc_data.get("text"),
                    "similarity": float(similarity),
                    "document": doc_data.get("doc", {})
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []
    
    def cluster_documents(self) -> List[Dict[str, Any]]:
        """
        Cluster all documents in the index using KMeans
        
        Returns:
            List of cluster information with centroids and document counts
        """
        try:
            # Load index
            index = self.load_or_create_index()
            
            # Handle empty index case
            if index.ntotal == 0:
                logger.warning("No documents in index to cluster")
                return []
                
            # Extract all vectors from FAISS
            vectors = np.zeros((index.ntotal, self.embedding_dim), dtype=np.float32)
            all_ids = np.arange(index.ntotal, dtype=np.int64)
            index.reconstruct_batch(all_ids, vectors)
            
            # Load or train KMeans
            kmeans = self.load_or_train_kmeans(vectors)
            
            # Predict clusters
            clusters = kmeans.predict(vectors)
            
            # Group documents by cluster
            cluster_groups = {}
            for i, cluster_id in enumerate(clusters):
                faiss_id = int(all_ids[i])
                doc_data = self.id_to_data_map.get(faiss_id, {})
                
                if cluster_id not in cluster_groups:
                    cluster_groups[cluster_id] = []
                    
                cluster_groups[cluster_id].append({
                    "id": doc_data.get("id"),
                    "text": doc_data.get("text"),
                    "document": doc_data.get("doc", {})
                })
            
            # Create cluster info with centroids and documents
            clusters_info = []
            for cluster_id, docs in cluster_groups.items():
                # Get cluster centroid
                centroid = kmeans.cluster_centers_[cluster_id]
                
                # Find document closest to centroid for representative
                representative = None
                min_distance = float('inf')
                for i, doc in enumerate(docs):
                    faiss_id = next(
                        (k for k, v in self.id_to_data_map.items() 
                         if v.get("id") == doc["id"]), 
                        None
                    )
                    if faiss_id is not None:
                        doc_vector = vectors[all_ids == faiss_id][0]
                        dist = np.linalg.norm(doc_vector - centroid)
                        if dist < min_distance:
                            min_distance = dist
                            representative = doc
                
                clusters_info.append({
                    "cluster_id": int(cluster_id),
                    "centroid": centroid.tolist(),
                    "size": len(docs),
                    "documents": docs,
                    "representative": representative
                })
            
            return clusters_info
            
        except Exception as e:
            logger.error(f"Error clustering documents: {str(e)}")
            return []
    
    def assign_to_cluster(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Assign a text to the best matching cluster
        
        Args:
            text: Text to assign
            
        Returns:
            Cluster information or None if no suitable cluster
        """
        try:
            # Generate embedding
            embedding = self.get_embedding(text)
            
            # Load index and KMeans
            _ = self.load_or_create_index()  # Make sure index is loaded
            kmeans = self.load_or_train_kmeans()
            
            # Predict cluster
            cluster_id = kmeans.predict([embedding])[0]
            
            # Get cluster centroid
            centroid = kmeans.cluster_centers_[cluster_id]
            
            # Calculate similarity to centroid
            similarity = cosine_similarity([embedding], [centroid])[0][0]
            
            # Only assign if similarity is high enough
            if similarity < self.similarity_threshold:
                return None
                
            # Get cluster info
            cluster_info = self.cluster_documents()[cluster_id]
            
            return {
                "cluster_id": int(cluster_id),
                "similarity": float(similarity),
                "cluster_info": cluster_info
            }
            
        except Exception as e:
            logger.error(f"Error assigning to cluster: {str(e)}")
            return None
    
    def find_best_cluster(
        self, 
        embedding: np.ndarray,
        existing_clusters: List[Dict[str, Any]],
        threshold: float = SIMILARITY_THRESHOLD
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best matching cluster for an embedding
        
        Args:
            embedding: Document embedding
            existing_clusters: List of existing clusters with centroids
            threshold: Minimum similarity threshold
            
        Returns:
            Best matching cluster or None
        """
        best_score = 0.0
        best_cluster = None
        
        for cluster in existing_clusters:
            if "centroid" not in cluster:
                continue
                
            centroid = np.array(cluster["centroid"])
            sim = cosine_similarity([embedding], [centroid])[0][0]
            
            if sim > best_score and sim >= threshold:
                best_score = sim
                best_cluster = cluster
                
        return best_cluster
    
    def _retrain_kmeans(self) -> bool:
        """
        Retrain KMeans with all current embeddings
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract all vectors from FAISS
            index = self.load_or_create_index()
            vectors = np.zeros((index.ntotal, self.embedding_dim), dtype=np.float32)
            all_ids = np.arange(index.ntotal, dtype=np.int64)
            index.reconstruct_batch(all_ids, vectors)
            
            # Train new KMeans model
            logger.info(f"Retraining KMeans model with {index.ntotal} vectors")
            start_time = time.time()
            
            # Cap the number of clusters to the number of vectors
            n_clusters = min(self.num_clusters, vectors.shape[0])
            
            self.kmeans = KMeans(
                n_clusters=n_clusters,
                init='k-means++',
                n_init=10,
                random_state=42
            )
            self.kmeans.fit(vectors)
            
            # Save the model
            with open(self.kmeans_path, 'wb') as f:
                pickle.dump(self.kmeans, f)
                
            logger.info(f"KMeans model retrained in {time.time() - start_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error retraining KMeans model: {str(e)}")
            return False
    
    def _save_index(self) -> bool:
        """
        Save FAISS index and document mapping
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.index is not None:
                # Save FAISS index
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                faiss.write_index(self.index, self.index_path)
                
                # Save document mapping
                mapping_path = self.index_path + ".mapping"
                with open(mapping_path, 'wb') as f:
                    pickle.dump(self.id_to_data_map, f)
                    
                logger.info(f"Saved FAISS index with {self.index.ntotal} vectors")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            return False
    
    def cleanup(self):
        """Release resources"""
        self.embedding_model = None
        self.index = None
        self.kmeans = None
        
        # Force garbage collection
        import gc
        gc.collect()
        
        logger.info("DocumentGrouper resources cleaned up")

# Legacy function for backward compatibility
def get_embedding(text: str) -> np.ndarray:
    """Legacy function for backward compatibility"""
    grouper = DocumentGrouper()
    return grouper.get_embedding(text)

def find_best_cluster(embedding: np.ndarray, existing: list[dict], threshold: float = 0.75):
    """Legacy function for backward compatibility"""
    grouper = DocumentGrouper()
    return grouper.find_best_cluster(embedding, existing, threshold)
