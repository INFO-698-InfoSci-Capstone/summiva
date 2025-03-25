import numpy as np
from bson import ObjectId
from datetime import datetime

from src.database.mongo_session import mongo_db
from src.database.postgres_session import get_pg_session, Cluster
from src.core.grouper import get_embedding, find_best_cluster

from src.config.config import settings
import celery

celery_app = celery.Celery("grouping", broker=settings.CELERY_BROKER_URL)

@celery_app.task
def run_grouping(doc_id: str):
    doc = mongo_db["docs"].find_one({"_id": ObjectId(doc_id)})
    if not doc or not doc.get("summary_text"):
        return "No summary found"

    summary = doc["summary_text"]
    embedding = get_embedding(summary)

    # Get all clusters from Postgres
    session = get_pg_session()
    clusters = session.query(Cluster).all()
    cluster_data = [{"id": c.id, "centroid": np.array(c.centroid)} for c in clusters]

    best_cluster = find_best_cluster(embedding, cluster_data)

    if best_cluster:
        cluster_id = best_cluster["id"]
        # Optionally: update centroid as moving average (not shown here)
    else:
        # Create new cluster
        cluster = Cluster(
            name=f"Cluster-{doc_id[:6]}",
            centroid=embedding.tolist(),
            created_at=datetime.utcnow()
        )
        session.add(cluster)
        session.commit()
        cluster_id = cluster.id

    # Update MongoDB
    mongo_db["docs"].update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"group_id": str(cluster_id)}}
    )

    # Optionally update PostgreSQL links (e.g., document-group join table)
    session.close()
    return {"doc_id": doc_id, "group_id": cluster_id}
