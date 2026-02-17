# Scalable URL Shortener

## 1. Problem Statement

Design and implement a production-grade URL shortening service that:

-   Accepts a long URL and generates a unique, compact short URL
-   Redirects users from the short URL to the original destination
-   Handles high read traffic with low latency
-   Scales horizontally under increasing load
-   Ensures high availability and fault tolerance

This system is read-heavy, latency-sensitive, and must be optimized for
large-scale traffic patterns.

------------------------------------------------------------------------

## 2. Functional Requirements

### Core Features

-   Generate a unique short URL for a given long URL
-   Redirect short URL to original URL
-   Guarantee uniqueness of generated short codes
-   Persist mappings reliably in a database

### Optional Features (Phase 2)

-   Custom alias support
-   Expiration time for links
-   Click analytics (visit counter)
-   Link disabling / soft delete
-   Rate limiting per client

------------------------------------------------------------------------

## 3. Non-Functional Requirements

### Performance

-   Redirect latency \< 50ms
-   High read throughput (millions of requests per day)
-   Efficient database lookups

### Scalability

-   Horizontally scalable API layer
-   Support database sharding
-   Caching layer for hot URLs
-   Stateless application servers

### Reliability

-   No duplicate short codes
-   Graceful failure handling
-   Minimal downtime during deployments

### Storage Efficiency

-   Indexed `short_code` column
-   Compact ID representation using Base62 encoding

------------------------------------------------------------------------

## 4. Traffic Characteristics

This system is:

-   Write-light (shorten operation occurs once)
-   Read-heavy (redirect operation occurs potentially millions of times)

Example:

1 URL shortened once\
→ 2 million redirects

Therefore:

The redirect path is the critical performance path and must be
optimized.

------------------------------------------------------------------------

## 5. High-Level Architecture

### Shorten Flow (Write Path)

Client → API → Insert into DB → Generate ID → Base62 Encode → Update
short_code → Return short URL

Characteristics: - Low frequency - Requires uniqueness guarantee - Must
return consistent short code

------------------------------------------------------------------------

### Redirect Flow (Read Path -- Critical)

Client → API\
→ Check Redis Cache\
→ If cache hit → Redirect\
→ If cache miss → Query DB → Store in Cache → Redirect

Characteristics: - Extremely high frequency - Must be optimized for
latency - Caching significantly reduces DB load

------------------------------------------------------------------------

## 6. ID Generation Strategy

### Approach:

Auto-increment primary key + Base62 encoding

Why this approach?

-   Guaranteed uniqueness via database primary key
-   No collision handling logic required
-   Compact URL representation
-   Easy to shard in the future

### Example

Database ID: 12500\
Base62(12500) → dnh

Short URL: short.ly/dnh

------------------------------------------------------------------------

## 7. Database Schema

### Table: urls

-   id (BIGINT PRIMARY KEY)
-   short_code (VARCHAR(10), UNIQUE, INDEXED)
-   original_url (TEXT, NOT NULL)
-   created_at (TIMESTAMP, DEFAULT NOW())
-   expires_at (TIMESTAMP, nullable)
-   click_count (BIGINT, DEFAULT 0)

### Why Index short_code?

Redirect query:

SELECT original_url FROM urls WHERE short_code = 'abc123';

Without index → Full table scan (O(N))\
With index → B-tree lookup (O(log N))

This is critical for large-scale datasets.

------------------------------------------------------------------------

## 8. Bottlenecks & Failure Considerations

### What if 1M users hit the same link?

Without caching: - Database becomes bottleneck - High CPU usage -
Possible downtime

With Redis caching: - First request populates cache - Remaining requests
served from memory - Drastically reduced DB load

### What if Redis goes down?

-   System falls back to database
-   Higher latency
-   Service still functional (graceful degradation)

------------------------------------------------------------------------

## 9. Scaling Strategy

Future improvements:

-   Add Redis for read-through caching
-   Add read replicas for heavy traffic
-   Introduce consistent hashing for DB sharding
-   Move click counting to asynchronous processing
-   Add CDN layer for global redirect optimization
-   Implement rate limiting at API gateway

------------------------------------------------------------------------

## 10. Observability & Monitoring (Future Phase)

-   Request latency metrics
-   Cache hit/miss ratio
-   DB query performance monitoring
-   Error rate tracking
-   Distributed tracing

------------------------------------------------------------------------

## 11. Tech Stack

-   FastAPI (API Layer)
-   PostgreSQL (Persistent Storage)
-   Redis (Caching Layer -- Phase 2)
-   SQLAlchemy (ORM)
-   Uvicorn (ASGI Server)

------------------------------------------------------------------------

## 12. Project Goals

This project demonstrates:

-   Read-heavy system optimization
-   ID generation and encoding strategies
-   Database indexing and schema design
-   Caching integration strategy
-   Scalability thinking
-   Backend production mindset

------------------------------------------------------------------------



# Phase 3 – Redis Integration & System Design Notes

## Redis Integration Overview

Redirect Flow:

Client → API  
→ Check Redis Cache  
→ If cache hit → Redirect  
→ If cache miss → Query DB → Store in Redis → Redirect  

Redis is used as a read-through cache to reduce database load and improve latency.

---

## Redis Failure Handling

### What happens if Redis crashes?

- Cache becomes unavailable
- All redirect requests fall back to the database
- Latency increases
- System remains functional (graceful degradation)

Redis is a performance optimization layer — the database remains the source of truth.

---

## Cache TTL Strategy

TTL (Time To Live) determines how long a key stays in cache.

Why use TTL?

- Prevent stale data
- Control memory usage
- Automatically clean unused entries

For URL shorteners:
- URLs rarely change
- TTL can be long (1 hour to 24 hours depending on traffic pattern)

Example:
redis_client.set(short_code, original_url, ex=3600)

This stores the key for 1 hour.

---

## Hot Key Problem

A hot key occurs when one short URL becomes extremely popular (viral link).

Problem:
- Millions of requests hit the same Redis key
- That Redis instance becomes a bottleneck

Possible Solutions:
- Redis replication
- Distributed cache cluster
- Load balancing
- Key partitioning strategies

---

## Click Count Update Strategy

Should click_count update be synchronous?

No.

If we increment the database counter on every redirect:
- High write load
- Increased latency
- DB becomes bottleneck

Better approach:
- Push click event to a background queue
- Batch process updates asynchronously

This keeps the redirect path fast and scalable.

---

## Summary

This phase introduces:

- Redis caching for read-heavy optimization
- TTL strategy for memory control
- Graceful degradation when cache fails
- Hot key awareness
- Asynchronous thinking for analytics

The system is now transitioning from a simple CRUD application to a scalable backend service.


This project is designed to reflect production-grade system design and
backend engineering principles.
