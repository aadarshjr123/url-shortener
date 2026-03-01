# 🚀 Scalable URL Shortener

A production-grade URL shortening service built with scalability,
performance, and system design principles in mind.

This project is intentionally designed as a read-heavy distributed
system, optimized for low-latency redirects and horizontal scalability.

------------------------------------------------------------------------

# 1️⃣ Problem Statement

Design and implement a scalable URL shortening service that:

-   Generates compact, unique short URLs
-   Redirects users with minimal latency
-   Handles millions of redirect requests
-   Scales horizontally
-   Maintains high availability
-   Optimizes read-heavy workloads

This system prioritizes redirect performance, since one shortened link
may be accessed millions of times.

------------------------------------------------------------------------

# 2️⃣ System Characteristics

-   Write-light system (shorten once)
-   Read-heavy system (redirect many times)
-   Latency-sensitive
-   High concurrency environment
-   Stateless API layer

Example:

1 URL shortened once\
→ 2 million redirect requests

Redirect path is the critical performance path.

------------------------------------------------------------------------

# 3️⃣ High-Level Architecture

Client\
↓\
Load Balancer\
↓\
FastAPI Application (Stateless)\
↓\
---------------------------------\
Redis (Cache Layer)\
PostgreSQL (Primary Database)\
---------------------------------

------------------------------------------------------------------------

## 🔹 Shorten Flow (Write Path)

Client → API → Rate Limit Check\
→ Insert into DB\
→ Generate ID\
→ Base62 Encode\
→ Update short_code\
→ Return short URL

------------------------------------------------------------------------

## 🔹 Redirect Flow (Read Path --- Critical)

Client → API → Rate Limit Check\
→ Check Redis Cache\
→ Cache Hit → Redirect\
→ Cache Miss → DB Lookup → Cache → Redirect\
→ Async Click Increment

------------------------------------------------------------------------

# 4️⃣ Tech Stack

-   FastAPI --- API layer\
-   PostgreSQL --- Persistent storage\
-   Redis --- Cache + rate limiting\
-   SQLAlchemy --- ORM\
-   Uvicorn --- ASGI server

Architecture Layers:

Router Layer → HTTP\
Service Layer → Business Logic\
Repository Layer → DB Access

------------------------------------------------------------------------

# 5️⃣ ID Generation Strategy

Auto-increment primary key + Base62 encoding.

Why: - Guaranteed uniqueness - No collision handling - Compact
representation - Future sharding support

Example:

Database ID: 12500\
Base62(12500) → dnh

------------------------------------------------------------------------

# 6️⃣ Database Schema

Table: urls

-   id (BIGINT, Primary Key)
-   short_code (VARCHAR(10), UNIQUE, INDEXED)
-   original_url (TEXT, NOT NULL)
-   created_at (TIMESTAMP, DEFAULT NOW())
-   expires_at (TIMESTAMP, nullable)
-   click_count (BIGINT, DEFAULT 0)

Indexing short_code ensures O(log N) lookup performance.

------------------------------------------------------------------------

# 7️⃣ Caching Strategy (Redis)

Read-through cache:

-   First request → DB → Cache
-   Subsequent requests → Redis

TTL Strategy: - If expires_at exists → TTL = remaining time - Otherwise
→ Default 1 hour

Ensures no stale data and memory control.

------------------------------------------------------------------------

# 8️⃣ Rate Limiting

Redis-based atomic counters.

-   Configurable per route
-   Separate limits for shorten and redirect
-   Returns 429 Too Many Requests
-   Includes Retry-After header

Protects system stability.

------------------------------------------------------------------------

# 9️⃣ Async Click Tracking

Click count updates run in background tasks.

Benefits: - Redirect path remains fast - Write-heavy operations
isolated - Easily extendable to queue-based processing

------------------------------------------------------------------------

# 🔟 Failure Handling

Redis Failure: - Falls back to DB - Higher latency but functional

PostgreSQL Failure: - Writes fail - Redirect may fail if not cached

API Failure: - Load balancer routes traffic to healthy instances

------------------------------------------------------------------------

# 1️⃣1️⃣ Scaling Path

Stage 1 (\~1M URLs): - Single DB + Redis

Stage 2 (\~10M URLs): - Add read replicas - Async click processing

Stage 3 (\~100M URLs): - DB sharding - Distributed ID generation - Redis
Cluster - CDN for global redirect

------------------------------------------------------------------------

# 1️⃣2️⃣ Monitoring Strategy

Monitor:

API: - Requests per second - P95 latency - Error rate

Redis: - Cache hit ratio - Memory usage

DB: - Query latency - Slow queries

Business: - Click volume - Rate limit violations

------------------------------------------------------------------------

# ✅ Current Capabilities

✔ Layered architecture\
✔ Redis caching\
✔ Expiration logic\
✔ Async click tracking\
✔ Configurable rate limiting\
✔ Indexed database\
✔ Health endpoint\
✔ System design documentation

------------------------------------------------------------------------

This project demonstrates production-grade backend engineering and
scalable system design principles.
