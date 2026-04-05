# ⚖️ Architecture Decision Log

Because making technical choices requires understanding trade-offs.

---

### 1. Why `Flask` over `FastAPI`?
**Context:** We needed a lightweight framework that was highly reliable and predictable.
**Decision:** We chose Flask.
**Reason:** While FastAPI is inherently faster via raw Async ASGI capabilities, this application was originally scaffolded off the MLH standard template explicitly enforcing `Flask`. Flask is heavily battle-tested. SRE principles indicate that familiarity and simple synchronization (WSGI) can lead to fewer chaotic edge cases than unmanaged async loops for a small hackathon timescale.

### 2. Why `PostgreSQL` + `Peewee`?
**Decision:** Use PostgreSQL as the primary data store and Peewee ORM to communicate.
**Reason:** PostgreSQL is the gold standard for ACID compliance, enforcing extremely strict data integrity checks, ensuring zero data anomalies. Peewee is much closer to raw SQL and far less bloated than SQLAlchemy, reducing the possibility of overly complex query compilation faults.

### 3. Why NOT Redis caching (Yet)?
**Decision:** We elected to bypass Redis caching for the initial MVP.
**Reason:** The goal of "Reliability Gold" tier mandates a bullet-proof core system. Adding Redis introduces a 3rd component (API → Cache → Database) which exponentially increases network failure topologies (What happens if Redis goes offline but Postgres remains up? Do we fall back? Does it deadlock?). 
By routing directly to PostgreSQL and trusting its proprietary in-memory cache tuning, we guarantee a single point of truth with maximum data integrity. Caching should only be injected once raw horizontal scaling triggers database CPU saturation limitations.

### 4. Custom Database Retry Wrapper vs. Native Reconnection
**Decision:** We wrote a custom `retry_db_operation()` function instead of using off-the-shelf pooling libraries.
**Reason:** The SRE directive demands that we understand precisely how failure is mitigated. The custom wrapper executes code natively Pythonic (`time.sleep` with 3 iterative tries), giving us complete internal metrics if it fails over, versus a black-boxed library approach that could hang transactions silently.
