Below is a **high-level system diagram** and explanation of how **Auth Service** (FastAPI + PostgreSQL) interacts with the **Summarization Service** (FastAPI + MongoDB + PostgreSQL doc ownership). We’ll also note how **Celery/RabbitMQ** and **Docker/Kubernetes** fit into this architecture.

---

## **1. High-Level System Diagram**

```
                 ┌─────────────────────┐
                 │    Auth Service     │
                 │  (FastAPI, Postgres)│
                 │   /api/v1/auth/*    │
                 └─────────────────────┘
                         ▲
                         │
         [JWT Login]     │  [Register/Login => JWT]
         [User Info]     │
                         │
          ┌──────────────┴──────────────┐
          │          User (Flutter/Web) │
          └──────────────┬──────────────┘
                         │
                         │
          [Bearer Token] │  [Summarize Request => doc_id]
                         │
             ┌───────────▼───────────┐
             │ Summarization Service │
             │(FastAPI, Postgres,    │
             │    MongoDB, RabbitMQ) │
             └───────────┬───────────┘
                         │
        ┌────────────────┴─────────────────┐
        │    [Doc Ownership in Postgres]   │
        │  (doc_id, user_id, created_at...)│
        └───────────────┬──────────────────┘
                        │
                        │
             ┌──────────▼───────────┐
             │    MongoDB           │
             │(raw & summarized txt)│
             └──────────────────────┘
```

**Key Points**:  
1. **User** obtains a **JWT** token by logging in via the **Auth Service**.  
2. User calls the **Summarization Service** with **Bearer token** → Summarization verifies user’s identity (via JWT).  
3. Summarization Service logs ownership info in **Postgres** (e.g., a `doc_ownership` table referencing `user_id + doc_id`).  
4. Actual text (raw/summarized) is stored in **MongoDB**.  
5. Summarization tasks can be done **async** with **Celery + RabbitMQ** for large texts.

---

## **2. User Data in PostgreSQL & Doc Ownership**

1. **Auth Service** manages `users` table in **PostgreSQL**:
   - **Schema**: `id`, `email`, `hashed_password`, `role`, `is_active`, etc.
   - Endpoints: `/register`, `/login`, `/refresh`, `/users/me`.
2. **Summarization Service** references a `doc_ownership` (or `docs`) table:
   - **Fields**:
     - `doc_id` (PK),
     - `user_id` (FK referencing `users.id`),
     - `created_at` / `updated_at`,
     - maybe `title` or `status`.
3. When a user calls `POST /api/v1/summarize`, Summarization Service:
   - Decodes `JWT` → obtains `user_id`.
   - Inserts a row in `doc_ownership` linking `doc_id` → `user_id`.
   - Summarized content is stored in MongoDB; doc metadata (e.g., creation time) goes in Postgres.

---

## **3. How Summarization Service Retrieves `user_id` from Auth**

1. **JWT-based**:
   - **Auth Service**: On successful login, returns a **JWT** with `sub: user.email` (or user.id).
   - **Summarization Service**: Has a small function (using `fastapi.security.OAuth2PasswordBearer` or similar) that **verifies the token** → extracts `user_id`.
   - Summarization then:
     - **Associates doc** with `user_id` in Postgres,
     - **Stores text** in MongoDB with a matching `doc_id`.
2. **Retrieval**:
   - For `GET /api/v1/docs/{doc_id}`:
     - Summarization Service checks if `doc_id` belongs to `user_id` in Postgres, then fetches text from MongoDB.

---

## **4. Recommended Technologies & Flow**

1. **Celery + RabbitMQ**:
   - Summarization tasks can be CPU-heavy or slow (especially with large texts).
   - Summarization can happen **async**:
     - `POST /api/v1/summarize` returns a **job_id** immediately,
     - Celery workers read tasks from RabbitMQ,
     - Once done, results are stored in MongoDB.
2. **Docker Compose** (Local Dev):
   - Start containers:
     - **Auth Service** (ex: port 8000),
     - **Summarization Service** (ex: port 8001),
     - **PostgreSQL** (structured data),
     - **MongoDB** (unstructured text),
     - **RabbitMQ** (optional, for async tasks).
   - Single `docker-compose.yml` can define these services.
3. **Kubernetes** (Production):
   - Each microservice is a **Deployment** + **Service** in K8s.
   - Use **PersistentVolumeClaims** for Postgres & MongoDB data.
   - **Horizontal Pod Autoscaler** if needed for Summarization load.

---

### **End-to-End Flow Summary**

1. **User** logs in → gets **JWT** from Auth Service (PostgreSQL store).  
2. **User** calls Summarization with the JWT → Summarization checks doc ownership in Postgres, stores raw + summarized text in MongoDB.  
3. **User** can retrieve the doc or summary. Summarization checks `doc_ownership` for correct `user_id` → fetch from MongoDB → returns result.  
4. Optional:
   - **Async** approach with Celery: Summarization enqueues tasks in RabbitMQ, returns `job_id` → user polls or Summarization notifies when done.

This architecture ensures **secure, scalable** handling of both user credentials (PostgreSQL) and large text data (MongoDB).