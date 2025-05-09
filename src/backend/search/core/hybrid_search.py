"""
Hybrid Search Module
=================
Production-level implementation of hybrid search combining Elasticsearch
for keyword-based search and FAISS for semantic vector search.

This hybrid approach delivers superior search results by combining:
1. High recall from keyword-based search (Elasticsearch)
2. High precision from semantic search (FAISS)
"""

import os
import time
import logging
import numpy as np
import json
from typing import List, Dict, Any, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor

# Elasticsearch imports
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout, NotFoundError
from elasticsearch.helpers import bulk

# Import FAISS manager from our implementation
from backend.search.core.faiss_index import faiss_manager

# Configure logging
logger = logging.getLogger("search.hybrid")

# Default configuration values
DEFAULT_ES_HOSTS = ["http://elasticsearch:9200"]
DEFAULT_ES_INDEX = "documents"
DEFAULT_ES_TIMEOUT = 20  # seconds
DEFAULT_ALPHA = 0.5  # Weight for blending scores (0.5 = equal weight)
DEFAULT_SEARCH_SIZE = 20
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1  # seconds

class HybridSearchEngine:
    """
    Production-level hybrid search engine combining Elasticsearch and FAISS
    for superior search results.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(HybridSearchEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        es_hosts: List[str] = DEFAULT_ES_HOSTS,
        es_index: str = DEFAULT_ES_INDEX,
        es_timeout: int = DEFAULT_ES_TIMEOUT,
        alpha: float = DEFAULT_ALPHA,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: int = DEFAULT_RETRY_DELAY
    ):
        """
        Initialize the hybrid search engine
        
        Args:
            es_hosts: List of Elasticsearch hostnames
            es_index: Elasticsearch index name
            es_timeout: Connection timeout in seconds
            alpha: Weight for blending scores (0.5 = equal weight)
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        # Only initialize once (singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Initialize configuration
        self.es_hosts = es_hosts
        self.es_index = es_index
        self.es_timeout = es_timeout
        self.alpha = alpha
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Components initialized on demand
        self._es_client = None
        
        logger.info(f"Initialized HybridSearchEngine with ES hosts: {es_hosts}")
        self._initialized = True
    
    @property
    def es_client(self) -> Optional[Elasticsearch]:
        """Lazy-load the Elasticsearch client"""
        if self._es_client is None:
            self._es_client = self._create_es_client()
        return self._es_client
    
    def _create_es_client(self) -> Optional[Elasticsearch]:
        """Create and configure Elasticsearch client"""
        try:
            # Create client with connection pooling and retry configuration
            client = Elasticsearch(
                self.es_hosts,
                request_timeout=self.es_timeout,
                retry_on_timeout=True,
                max_retries=self.max_retries
            )
            
            # Test connection
            start_time = time.time()
            is_connected = client.ping()
            ping_time = time.time() - start_time
            
            if not is_connected:
                logger.error("Could not connect to Elasticsearch")
                return None
            
            logger.info(f"Connected to Elasticsearch in {ping_time:.2f}s")
            return client
        except Exception as e:
            logger.error(f"Error connecting to Elasticsearch: {str(e)}")
            return None
    
    def ensure_index(self, mappings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Ensure the Elasticsearch index exists with proper mappings
        
        Args:
            mappings: Optional custom mappings for the index
            
        Returns:
            True if index exists or was created, False otherwise
        """
        if not self.es_client:
            logger.error("Elasticsearch client not available")
            return False
        
        try:
            # Check if index exists
            if self.es_client.indices.exists(index=self.es_index):
                logger.info(f"Elasticsearch index '{self.es_index}' already exists")
                return True
                
            # Create default mappings if not provided
            if not mappings:
                mappings = {
                    "mappings": {
                        "properties": {
                            "title": {
                                "type": "text",
                                "analyzer": "standard",
                                "fields": {
                                    "keyword": {"type": "keyword"}
                                }
                            },
                            "content": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "summary": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "tags": {
                                "type": "keyword"
                            },
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 384
                            },
                            "created_at": {
                                "type": "date"
                            },
                            "updated_at": {
                                "type": "date"
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "analysis": {
                            "analyzer": {
                                "standard": {
                                    "type": "standard"
                                }
                            }
                        }
                    }
                }
            
            # Create the index
            self.es_client.indices.create(
                index=self.es_index,
                body=mappings
            )
            
            logger.info(f"Created Elasticsearch index '{self.es_index}'")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring Elasticsearch index: {str(e)}")
            return False
    
    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        id_field: str = "id",
        text_field: str = "content",
        generate_embeddings: bool = True
    ) -> Tuple[int, int]:
        """
        Index documents in both Elasticsearch and FAISS
        
        Args:
            documents: List of documents to index
            id_field: Field to use as document ID
            text_field: Field to use as text content
            generate_embeddings: Whether to generate embeddings for FAISS
            
        Returns:
            Tuple of (es_success_count, faiss_success_count)
        """
        es_count = 0
        faiss_count = 0
        
        if not documents:
            logger.warning("No documents provided to index")
            return es_count, faiss_count
        
        try:
            # Index in Elasticsearch
            if self.es_client:
                # Prepare bulk indexing actions
                actions = []
                for doc in documents:
                    doc_id = doc.get(id_field, None)
                    if not doc_id:
                        continue
                        
                    action = {
                        "_op_type": "index",
                        "_index": self.es_index,
                        "_id": str(doc_id),
                        "_source": doc
                    }
                    actions.append(action)
                
                if actions:
                    # Ensure index exists
                    self.ensure_index()
                    
                    # Perform bulk indexing
                    start_time = time.time()
                    success, failed = bulk(
                        self.es_client,
                        actions,
                        refresh=True,
                        raise_on_error=False
                    )
                    
                    es_count = success
                    logger.info(f"Indexed {success} documents in Elasticsearch in {time.time() - start_time:.2f}s ({failed} failed)")
            
            # Index in FAISS if requested
            if generate_embeddings:
                # Extract relevant fields for FAISS indexing
                faiss_docs = []
                for doc in documents:
                    doc_id = doc.get(id_field, None)
                    text = doc.get(text_field, "")
                    
                    if doc_id and text:
                        faiss_docs.append({
                            "id": doc_id,
                            "text": text,
                            "doc": doc
                        })
                
                if faiss_docs:
                    # Add to FAISS index
                    start_time = time.time()
                    success = faiss_manager.add_documents(
                        faiss_docs,
                        text_key="text",
                        id_key="id",
                        metadata_keys=list(documents[0].keys()) if documents else None
                    )
                    
                    if success:
                        faiss_count = len(faiss_docs)
                        logger.info(f"Indexed {faiss_count} documents in FAISS in {time.time() - start_time:.2f}s")
            
            return es_count, faiss_count
            
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            return es_count, faiss_count
    
    def elasticsearch_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = DEFAULT_SEARCH_SIZE
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search using Elasticsearch
        
        Args:
            query: Search query text
            filters: Optional filters to apply to search
            size: Maximum number of results to return
            
        Returns:
            List of document matches with scores
        """
        if not self.es_client:
            logger.error("Elasticsearch client not available")
            return []
        
        try:
            # Build search query
            search_query = {
                "query": {
                    "bool": {
                        "must": [{
                            "multi_match": {
                                "query": query,
                                "fields": ["content^2", "title^3", "summary^4", "tags^2"],
                                "fuzziness": "AUTO",
                                "operator": "or"
                            }
                        }]
                    }
                },
                "size": size
            }
            
            # Add filters if provided
            if filters:
                filter_clauses = []
                for field, value in filters.items():
                    if isinstance(value, list):
                        filter_clauses.append({"terms": {field: value}})
                    else:
                        filter_clauses.append({"term": {field: value}})
                
                if filter_clauses:
                    search_query["query"]["bool"]["filter"] = filter_clauses
            
            # Execute search with retries
            for attempt in range(self.max_retries):
                try:
                    start_time = time.time()
                    response = self.es_client.search(
                        index=self.es_index,
                        body=search_query
                    )
                    search_time = time.time() - start_time
                    
                    # Process results
                    results = []
                    for hit in response["hits"]["hits"]:
                        results.append({
                            "id": hit["_id"],
                            "score": hit["_score"],
                            "source": hit["_source"],
                            "search_type": "elastic"
                        })
                        
                    logger.debug(f"Elasticsearch search completed in {search_time:.3f}s with {len(results)} results")
                    return results
                    
                except (ConnectionError, ConnectionTimeout) as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Elasticsearch search failed (attempt {attempt+1}): {str(e)}")
                        time.sleep(self.retry_delay)
                    else:
                        logger.error(f"Elasticsearch search failed after {self.max_retries} attempts: {str(e)}")
                        return []
                        
        except Exception as e:
            logger.error(f"Elasticsearch search error: {str(e)}")
            return []
    
    def faiss_search(
        self,
        query: str,
        size: int = DEFAULT_SEARCH_SIZE
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic vector search using FAISS
        
        Args:
            query: Search query text
            size: Number of results to return
            
        Returns:
            List of document matches with scores
        """
        try:
            # Use the FAISS manager to perform the search
            return faiss_manager.search(query, k=size, return_documents=True)
            
        except Exception as e:
            logger.error(f"FAISS search error: {str(e)}")
            return []
    
    def merge_search_results(
        self,
        elastic_results: List[Dict[str, Any]],
        faiss_results: List[Dict[str, Any]],
        alpha: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Merge and rerank results from Elasticsearch and FAISS
        
        Args:
            elastic_results: Results from Elasticsearch
            faiss_results: Results from FAISS
            alpha: Weight for blending scores (0.5 = equal weight)
            
        Returns:
            List of merged and reranked results
        """
        # Use instance alpha if not provided
        if alpha is None:
            alpha = self.alpha
        
        # Create lookup dictionaries for fast access
        elastic_dict = {item["id"]: item for item in elastic_results}
        faiss_dict = {item["id"]: item for item in faiss_results}
        
        # Normalize Elasticsearch scores if any results exist
        if elastic_results:
            max_elastic_score = max(item["score"] for item in elastic_results)
            min_elastic_score = min(item["score"] for item in elastic_results)
            score_range = max_elastic_score - min_elastic_score
            
            for item in elastic_results:
                if score_range > 0:
                    item["normalized_score"] = (item["score"] - min_elastic_score) / score_range
                else:
                    item["normalized_score"] = 1.0
        
        # Create merged results set
        merged_results = {}
        
        # Add all documents from both result sets
        all_doc_ids = set(elastic_dict.keys()) | set(faiss_dict.keys())
        
        for doc_id in all_doc_ids:
            elastic_item = elastic_dict.get(doc_id, {})
            faiss_item = faiss_dict.get(doc_id, {})
            
            merged_doc = {
                "id": doc_id,
                "search_type": "hybrid"
            }
            
            # Calculate combined score
            elastic_score = elastic_item.get("normalized_score", 0)
            faiss_score = faiss_item.get("score", 0)
            
            # Weighted combination of scores
            hybrid_score = (alpha * faiss_score) + ((1 - alpha) * elastic_score)
            merged_doc["score"] = hybrid_score
            
            # Record individual scores for debugging
            merged_doc["elastic_score"] = elastic_score
            merged_doc["semantic_score"] = faiss_score
            
            # Include source data if available
            if "source" in elastic_item:
                merged_doc["source"] = elastic_item["source"]
            elif "document" in faiss_item:
                merged_doc["source"] = faiss_item["document"]
                
            merged_results[doc_id] = merged_doc
        
        # Convert to list and sort by combined score
        result_list = list(merged_results.values())
        result_list.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank information
        for idx, item in enumerate(result_list):
            item["rank"] = idx + 1
            
        return result_list
    
    def hybrid_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = DEFAULT_SEARCH_SIZE,
        alpha: Optional[float] = None,
        search_type: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining Elasticsearch and FAISS
        
        Args:
            query: Search query text
            filters: Optional filters to apply to search
            size: Maximum number of results to return
            alpha: Weight for blending scores (0.5 = equal weight)
            search_type: Type of search to perform ('hybrid', 'elastic', or 'faiss')
            
        Returns:
            List of document matches with scores
        """
        # Set default alpha if not provided
        if alpha is None:
            alpha = self.alpha
            
        # Use ThreadPoolExecutor to run searches in parallel for hybrid search
        if search_type == "hybrid":
            try:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    # Submit both search tasks to run in parallel
                    elastic_future = executor.submit(
                        self.elasticsearch_search, 
                        query, 
                        filters, 
                        size
                    )
                    
                    faiss_future = executor.submit(
                        self.faiss_search,
                        query,
                        size
                    )
                    
                    # Get results from both searches
                    elastic_results = elastic_future.result()
                    faiss_results = faiss_future.result()
                    
                # Merge and return results
                start_time = time.time()
                merged_results = self.merge_search_results(
                    elastic_results, 
                    faiss_results, 
                    alpha
                )
                
                logger.info(f"Hybrid search completed in {time.time() - start_time:.3f}s with {len(merged_results)} results")
                return merged_results[:size]
                
            except Exception as e:
                logger.error(f"Error during parallel hybrid search: {str(e)}")
                # Fall back to sequential execution
                logger.info("Falling back to sequential hybrid search")
                
                elastic_results = self.elasticsearch_search(query, filters, size)
                faiss_results = self.faiss_search(query, size)
                
                merged_results = self.merge_search_results(
                    elastic_results,
                    faiss_results,
                    alpha
                )
                
                return merged_results[:size]
                
        # For single-mode searches
        elif search_type == "elastic":
            return self.elasticsearch_search(query, filters, size)
            
        elif search_type == "faiss":
            return self.faiss_search(query, size)
            
        else:
            logger.error(f"Unknown search type: {search_type}")
            return []
    
    def cleanup(self):
        """Release resources"""
        if self._es_client is not None:
            try:
                self._es_client.close()
            except:
                pass
            self._es_client = None
            
        # Also cleanup FAISS resources
        faiss_manager.cleanup()
        
        logger.info("HybridSearchEngine resources cleaned up")

# Initialize singleton instance with default settings
search_engine = HybridSearchEngine()

# Legacy functions for backward compatibility
def elasticsearch_search(
    query: str, 
    index_name: str = DEFAULT_ES_INDEX,
    filters: Optional[Dict[str, Any]] = None,
    size: int = DEFAULT_SEARCH_SIZE
) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    return search_engine.elasticsearch_search(query, filters, size)

def faiss_search(
    query: str,
    k: int = DEFAULT_SEARCH_SIZE
) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    return search_engine.faiss_search(query, k)

def merge_search_results(
    elastic_results: List[Dict[str, Any]],
    faiss_results: List[Dict[str, Any]],
    alpha: float = DEFAULT_ALPHA
) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    return search_engine.merge_search_results(elastic_results, faiss_results, alpha)

def hybrid_search(
    query: str,
    index_name: str = DEFAULT_ES_INDEX,
    filters: Optional[Dict[str, Any]] = None,
    size: int = DEFAULT_SEARCH_SIZE,
    alpha: float = DEFAULT_ALPHA
) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility"""
    return search_engine.hybrid_search(query, filters, size, alpha)