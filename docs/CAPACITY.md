# 🚀 Capacity Plan

How many users can we handle? Where is the limit?

## 📈 Current Capacity Baseline (Uncached)

Currently, the architecture consists of:
- 1 WSGI Gunicorn Container
- 1 PostgreSQL Database Instance

Based on standard benchmarks for synchronously served Python Flask HTTP architectures hitting DBs sequentially via Peewee:
- **Baseline limits:** We can comfortably handle roughly **50 to 100 concurrent requests per second** depending completely on the hardware executing the Postgres transactions.
- **The True Bottleneck:** The absolute ceiling in the current system is the **PostgreSQL Connection Pool and Disk IO**. Because we hit the DB for every single `POST /users` and `POST /posts` validation check (checking for duplicates or invalid referential limits), the disk is tasked heavily.

## 🚧 Expected Failure Points Under Tsunami Load (500+ Users/sec)

If 500 users per second strike the API right now, the following will occur:
1. **Thread Saturation:** Gunicorn worker threads will saturate waiting for PostgreSQL transaction locks to complete.
2. **502/504 Nightmares:** As workers are 100% occupied, NGINX or the edge load balancer will begin receiving timeouts.
3. **The `retry_db_operation` Trap:** Our robust retry logic (`retry_db_operation`), which solves transient drops brilliantly, will actually **compound the failure** under high load. By instructing every failing worker thread to wait `0.2` seconds and try again, we trap the pipeline in a massive traffic jam.

## 🔧 Roadmap to Scale (The Next Evolution)

When traffic scaling beyond 200 concurrent users is demanded, the following steps must be taken to safely restructure without sacrificing our Gold Tier Resilience.

### Phase 1: Horizontal API Scaling
Update `docker-compose.yml` to launch `api` replicas. Deploy an `NGINX` container to utilize round-robin load balancing amongst the Flask containers. This resolves Thread Saturation.

### Phase 2: Redis Query Caching
Inject Redis. Implement `GET /posts` to poll Redis. If the cache is warm, return 200 OK instantly. Only hit PostgreSQL for cache misses. Introduce Background Tasks (Celery) to invalidate caching on new posts.

### Phase 3: DB Read Replicas
Offload all analytical or read-heavy traffic (`GET /users`) to PostgreSQL read-only replicas, isolating the master database entirely for high-reliability `POST` (create) operations.
