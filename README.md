# RAG POC - Flask + RQ Worker

This project demonstrates a Flask application integrated with RQ for background processing. The worker processes documents asynchronously, storing embeddings and status updates in PostgreSQL and Redis.

---

## Prerequisites

- Python 3.10+  
- Docker & Docker Compose  

---

## Setup Instructions

### 1. Run Flask:

```bash
flask run --port 5001
```
### 2. Run Redis and PostgreSQL containers:

```bash
docker compose up -d
```

### 3. Set Python path and run the RQ worker:

```bash


```