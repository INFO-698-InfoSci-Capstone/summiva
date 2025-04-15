import time
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from .models import Group, GroupMember, GroupingResult
from .schemas import GroupingRequest, GroupingResponse
from apps.documents.models import Document
from core.database.database import get_db

class GroupingService:
    def __init__(self, db: Session):
        self.db = db
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _get_document_embeddings(self, document_ids: List[int]) -> Tuple[List[int], np.ndarray]:
        """Get document embeddings for the given document IDs."""
        documents = self.db.query(Document).filter(Document.id.in_(document_ids)).all()
        texts = [doc.content for doc in documents]
        embeddings = self.model.encode(texts)
        return [doc.id for doc in documents], embeddings

    def _kmeans_grouping(self, embeddings: np.ndarray, n_clusters: int) -> np.ndarray:
        """Group documents using K-means clustering."""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        return kmeans.fit_predict(embeddings)

    def _dbscan_grouping(self, embeddings: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
        """Group documents using DBSCAN clustering."""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
        return dbscan.fit_predict(embeddings)

    def _similarity_grouping(self, embeddings: np.ndarray, threshold: float) -> List[List[int]]:
        """Group documents based on similarity threshold."""
        similarity_matrix = cosine_similarity(embeddings)
        groups = []
        visited = set()

        for i in range(len(embeddings)):
            if i not in visited:
                group = [i]
                visited.add(i)
                for j in range(i + 1, len(embeddings)):
                    if similarity_matrix[i, j] >= threshold:
                        group.append(j)
                        visited.add(j)
                groups.append(group)
        return groups

    def group_documents(self, request: GroupingRequest) -> GroupingResponse:
        """Group documents based on the specified algorithm and parameters."""
        start_time = time.time()

        # Get document embeddings
        doc_ids, embeddings = self._get_document_embeddings(request.document_ids)

        # Apply grouping algorithm
        if request.algorithm == "kmeans":
            n_clusters = request.parameters.get("n_clusters", 5)
            labels = self._kmeans_grouping(embeddings, n_clusters)
            groups = [[] for _ in range(n_clusters)]
            for i, label in enumerate(labels):
                groups[label].append(doc_ids[i])
        elif request.algorithm == "dbscan":
            eps = request.parameters.get("eps", 0.5)
            min_samples = request.parameters.get("min_samples", 2)
            labels = self._dbscan_grouping(embeddings, eps, min_samples)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            groups = [[] for _ in range(n_clusters)]
            for i, label in enumerate(labels):
                if label != -1:  # Skip noise points
                    groups[label].append(doc_ids[i])
        else:  # similarity
            threshold = request.parameters.get("threshold", 0.7)
            group_indices = self._similarity_grouping(embeddings, threshold)
            groups = [[doc_ids[i] for i in group] for group in group_indices]

        # Create groups and members in database
        created_groups = []
        created_members = []
        current_user_id = 1  # TODO: Get from auth context

        # Create grouping result
        grouping_result = GroupingResult(
            user_id=current_user_id,
            algorithm=request.algorithm,
            parameters=str(request.parameters)
        )
        self.db.add(grouping_result)
        self.db.commit()

        # Create groups and members
        for i, group_doc_ids in enumerate(groups):
            if not group_doc_ids:  # Skip empty groups
                continue

            # Create group
            group = Group(
                user_id=current_user_id,
                name=f"Group {i+1}",
                description=f"Automatically created group using {request.algorithm} algorithm"
            )
            self.db.add(group)
            self.db.commit()
            created_groups.append(group)

            # Create group members
            for doc_id in group_doc_ids:
                # Calculate average similarity with other group members
                doc_idx = doc_ids.index(doc_id)
                doc_embedding = embeddings[doc_idx]
                group_embeddings = embeddings[[doc_ids.index(gid) for gid in group_doc_ids if gid != doc_id]]
                if len(group_embeddings) > 0:
                    similarity_scores = cosine_similarity([doc_embedding], group_embeddings)[0]
                    avg_similarity = float(np.mean(similarity_scores))
                else:
                    avg_similarity = 1.0

                member = GroupMember(
                    group_id=group.id,
                    document_id=doc_id,
                    similarity_score=avg_similarity
                )
                self.db.add(member)
                created_members.append(member)

        self.db.commit()

        processing_time = time.time() - start_time
        return GroupingResponse(
            groups=created_groups,
            members=created_members,
            processing_time=processing_time
        ) 