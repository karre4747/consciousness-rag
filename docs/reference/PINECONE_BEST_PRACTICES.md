# Pinecone Best Practices & Performance Guide

**Last Updated:** December 9, 2025  
**Based on:** Pinecone Official Documentation (2025-10 API)

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [SDK Setup & Configuration](#sdk-setup--configuration)
3. [Performance Optimization](#performance-optimization)
4. [Data Modeling](#data-modeling)
5. [Error Handling](#error-handling)
6. [Production Checklist](#production-checklist)

---

## Core Principles

### 1. **Always Use Async Operations**
- Pinecone SDK calls are **synchronous** and **blocking**
- In async frameworks (FastAPI), wrap ALL Pinecone calls in `asyncio.to_thread()`
- Add timeouts to prevent indefinite hanging
- Never call Pinecone SDK methods directly from async endpoints

### 2. **Target Indexes by Host (Production)**
- ❌ **BAD:** `index = pc.Index(name="my-index")` - Adds extra `describe_index` call
- ✅ **GOOD:** `index = pc.Index(host="INDEX_HOST")` - Direct connection, faster
- Get host once at startup, cache it, reuse it

### 3. **Reuse Connections**
- Create index connection **once** at startup
- Reuse the same `index` object throughout application lifetime
- Don't create new connections for each request

### 4. **Batch Operations**
- Upsert in batches of up to **1000 records**
- Process queries in parallel when possible
- Use `upsert_from_dataframe` for large datasets

---

## SDK Setup & Configuration

### Installation

```bash
# Standard installation
pip install pinecone

# With gRPC for better performance (RECOMMENDED)
pip install "pinecone[grpc]"

# With async support (for FastAPI/async frameworks)
pip install "pinecone[asyncio]"
```

### Initialization Pattern

```python
from pinecone import Pinecone, ServerlessSpec
import os

# Initialize client ONCE at startup
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Get index host ONCE and cache it
index_description = pc.describe_index("your-index-name")
index_host = index_description.host

# Create index connection ONCE and reuse
index = pc.Index(host=index_host)  # Use host, not name!
```

### For Async Frameworks (FastAPI)

```python
from pinecone import PineconeAsyncio, ServerlessSpec
import asyncio

# Use async context manager
async with PineconeAsyncio(api_key="YOUR_API_KEY") as pc:
    # Create index connection
    async with pc.IndexAsyncio(host="INDEX_HOST") as index:
        # Use index for operations
        results = await index.query(...)
```

---

## Performance Optimization

### 1. **Use gRPC Instead of HTTP**

```python
# Install: pip install "pinecone[grpc]"
from pinecone.grpc import PineconeGRPC as Pinecone

pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.Index(host="INDEX_HOST")
```

**Benefits:**
- Modest performance improvement
- Better for high-throughput scenarios
- Lower latency

### 2. **Batch Upserts**

```python
# GOOD: Batch up to 1000 records
vectors = []
for i in range(1000):
    vectors.append({
        "id": f"doc{i}",
        "values": embedding,
        "metadata": {...}
    })

index.upsert(vectors=vectors)

# BAD: One at a time
for i in range(1000):
    index.upsert(vectors=[{"id": f"doc{i}", ...}])  # Slow!
```

### 3. **Parallel Operations**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Pinecone is thread-safe - run multiple queries in parallel
async def parallel_queries(query_vectors):
    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [
            asyncio.to_thread(index.query, vector=v, top_k=5)
            for v in query_vectors
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### 4. **Use Namespaces for Faster Queries**

```python
# Divide data into logical namespaces
index.upsert(
    vectors=vectors,
    namespace="user_123"  # Faster queries when filtering by namespace
)

# Query specific namespace
results = index.query(
    vector=query_vector,
    top_k=10,
    namespace="user_123"  # Only searches this namespace
)
```

### 5. **Filter by Metadata**

```python
# Metadata filters reduce search space = faster queries
results = index.query(
    vector=query_vector,
    top_k=10,
    filter={
        "document_type": "tutorial",
        "created_at": {"$gte": "2024-01-01"}
    }
)
```

### 6. **Connection Pool Configuration**

```python
# For parallel queries across namespaces
index = pc.Index(
    host="INDEX_HOST",
    pool_threads=50,              # Number of threads
    connection_pool_maxsize=50    # Cached HTTP connections
)
```

---

## Data Modeling

### 1. **Structured IDs**

```python
# GOOD: Structured, human-readable IDs
{
    "id": "document1#chunk1",      # Document + chunk
    "id": "user_123#preference",   # User + data type
    "id": "tenant_abc#doc1#chunk1" # Multi-tenant
}

# BAD: Random/unstructured IDs
{
    "id": "a7f3b2c1",
    "id": "xyz789"
}
```

**Benefits:**
- Easy to identify record type
- Enables efficient list operations
- Better debugging and maintenance

### 2. **Comprehensive Metadata**

```python
{
    "id": "document1#chunk1",
    "values": embedding,
    "metadata": {
        # Core document info
        "document_id": "document1",
        "document_title": "Introduction to Vector Databases",
        "chunk_number": 1,
        "total_chunks": 10,
        
        # Filterable fields
        "document_type": "tutorial",
        "created_at": "2024-01-15",
        "program_level": "beginner",
        
        # Searchable tags (as lists)
        "tags": ["vector-db", "pinecone", "tutorial"],
        "all_chakras": ["root", "crown"],
        "all_traditions": ["buddhism", "taoism"],
        
        # Link back to source
        "document_url": "https://example.com/docs/document1",
        "chunk_text": "First chunk content..."
    }
}
```

**Metadata Rules:**
- Keys must be strings
- Values: string, number, boolean, or list of strings
- Max 40 KB per record
- Use lists for multi-value fields (enables `$in` queries)

### 3. **Chunk Management Pattern**

```python
# Upsert chunks with structured IDs
chunks = []
for i, chunk_text in enumerate(document_chunks):
    chunks.append({
        "id": f"{document_id}#chunk{i+1}",
        "values": generate_embedding(chunk_text),
        "metadata": {
            "document_id": document_id,
            "chunk_number": i + 1,
            "total_chunks": len(document_chunks),
            "chunk_text": chunk_text,
            "title": document_title
        }
    })

index.upsert(vectors=chunks)
```

---

## Error Handling

### 1. **Retry Logic with Exponential Backoff**

```python
import time
import random
from pinecone.exceptions import PineconeException

async def pinecone_with_retry(func, max_retries=5, base_delay=1, max_delay=60):
    """
    Execute Pinecone operation with exponential backoff retry.
    
    Only retries on:
    - 5xx server errors (500, 502, 503, 504)
    - 429 rate limiting
    
    Does NOT retry on:
    - 4xx client errors (400, 401, 403, 404)
    """
    for attempt in range(max_retries):
        try:
            # Wrap sync Pinecone call in thread
            return await asyncio.wait_for(
                asyncio.to_thread(func),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail="Pinecone timeout")
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)
        except PineconeException as e:
            status_code = getattr(e, 'status', None)
            
            # Don't retry client errors (except 429)
            if status_code and status_code < 500 and status_code != 429:
                raise
            
            # Last attempt - re-raise
            if attempt == max_retries - 1:
                raise
            
            # Retry on 5xx or 429
            if status_code and (status_code >= 500 or status_code == 429):
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = random.uniform(0, delay * 0.1)
                await asyncio.sleep(delay + jitter)
            else:
                raise
```

### 2. **Error Types**

| Code | Type | Retry? | Action |
|------|------|--------|--------|
| 200-299 | Success | N/A | None |
| 400 | Invalid Argument | ❌ | Fix request |
| 401 | Unauthenticated | ❌ | Check API key |
| 402 | Payment Required | ❌ | Check billing |
| 403 | Forbidden | ❌ | Check quotas |
| 404 | Not Found | ❌ | Verify resource exists |
| 409 | Already Exists | ❌ | Handle conflict |
| 429 | Rate Limited | ✅ | Retry with backoff |
| 500 | Internal Error | ✅ | Retry with backoff |
| 502 | Bad Gateway | ✅ | Retry with backoff |
| 503 | Unavailable | ✅ | Retry with backoff |
| 504 | Gateway Timeout | ✅ | Retry with backoff |

### 3. **Rate Limit Handling**

```python
# Monitor rate limits proactively
# Implement exponential backoff for 429 errors
# Use batching to reduce request count
# Contact support if you need higher limits
```

---

## Production Checklist

### ✅ Connection Management
- [ ] Use `host` parameter instead of `name` for index connection
- [ ] Cache index connection object, don't recreate per request
- [ ] Use gRPC for better performance (`pinecone[grpc]`)
- [ ] Configure connection pool size appropriately

### ✅ Async Operations
- [ ] Wrap ALL Pinecone calls in `asyncio.to_thread()`
- [ ] Add timeouts to prevent hanging (5-30 seconds depending on operation)
- [ ] Use `PineconeAsyncio` if available for your use case

### ✅ Batching & Performance
- [ ] Batch upserts (up to 1000 records per batch)
- [ ] Use `upsert_from_dataframe` for large datasets
- [ ] Run parallel queries when possible (Pinecone is thread-safe)
- [ ] Use namespaces to partition data logically

### ✅ Data Modeling
- [ ] Use structured IDs (`document1#chunk1`)
- [ ] Include comprehensive metadata (max 40 KB)
- [ ] Use lists for multi-value metadata fields
- [ ] Add filterable fields for faster queries

### ✅ Error Handling
- [ ] Implement retry logic with exponential backoff
- [ ] Only retry on 5xx errors and 429
- [ ] Add jitter to retry delays
- [ ] Set maximum retry attempts
- [ ] Log retry attempts for monitoring

### ✅ Monitoring
- [ ] Monitor request latency
- [ ] Track error rates
- [ ] Monitor rate limit hits (429 errors)
- [ ] Set up alerts for high error rates

---

## Code Patterns

### Pattern 1: Async Endpoint with Pinecone Query

```python
@app.post("/query")
async def query_knowledge(request: QueryRequest):
    try:
        # Generate embedding (can be async)
        question_embedding = await asyncio.to_thread(
            generate_embedding, request.question
        )
        
        # Query Pinecone with timeout and retry
        query_response = await pinecone_with_retry(
            lambda: index.query(
                vector=question_embedding,
                top_k=request.top_k or 5,
                include_metadata=True,
                filter=request.filters
            ),
            max_retries=3,
            base_delay=1
        )
        
        return {"results": query_response.matches}
    except PineconeException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Pattern 2: Batch Upsert with Error Handling

```python
async def batch_upsert(vectors, batch_size=100):
    """Upsert vectors in batches with error handling."""
    total_uploaded = 0
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        
        try:
            await pinecone_with_retry(
                lambda: index.upsert(vectors=batch),
                max_retries=3
            )
            total_uploaded += len(batch)
        except Exception as e:
            logger.error(f"Failed to upsert batch {i}: {e}")
            # Continue with next batch
    
    return total_uploaded
```

### Pattern 3: Health Check with Timeout

```python
@app.get("/health")
async def health_check():
    try:
        stats = await asyncio.wait_for(
            asyncio.to_thread(index.describe_index_stats),
            timeout=5.0  # Short timeout for health checks
        )
        return {"status": "healthy", "vectors": stats.total_vector_count}
    except asyncio.TimeoutError:
        return {"status": "degraded", "error": "timeout"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## Performance Benchmarks

### Recommended Batch Sizes
- **Upserts:** 100-1000 records per batch
- **Queries:** Run up to 10-50 in parallel
- **Fetches:** Up to 1000 IDs per request

### Timeout Guidelines
- **Health checks:** 5 seconds
- **Queries:** 10 seconds
- **Upserts:** 15-30 seconds (depends on batch size)
- **Large queries (top_k=10000):** 30 seconds

### Connection Pool Sizing
- **pool_threads:** 10-50 (depends on concurrent requests)
- **connection_pool_maxsize:** Match pool_threads

---

## Common Pitfalls

### ❌ DON'T:
1. Call Pinecone SDK methods directly from async endpoints
2. Create new index connections for each request
3. Use index name instead of host in production
4. Retry on 4xx errors (except 429)
5. Upsert one record at a time
6. Ignore timeouts - always set them
7. Use unstructured/random IDs

### ✅ DO:
1. Wrap all Pinecone calls in `asyncio.to_thread()` with timeouts
2. Create index connection once, reuse it
3. Use `host` parameter for index connection
4. Only retry on 5xx errors and 429
5. Batch operations (100-1000 records)
6. Set appropriate timeouts for each operation
7. Use structured IDs (`document#chunk`)

---

## References

- [Pinecone Python SDK Docs](https://docs.pinecone.io/reference/python-sdk)
- [Increase Throughput Guide](https://docs.pinecone.io/guides/optimize/increase-throughput)
- [Decrease Latency Guide](https://docs.pinecone.io/guides/optimize/decrease-latency)
- [Error Handling Guide](https://docs.pinecone.io/guides/production/error-handling)
- [Data Modeling Guide](https://docs.pinecone.io/guides/index-data/data-modeling)

---

**Remember:** The key to efficient Pinecone integration is:
1. **Async-first** - Never block the event loop
2. **Connection reuse** - Create once, use many times
3. **Batch operations** - Group related operations
4. **Smart retries** - Only retry transient errors
5. **Structured data** - Use clear IDs and metadata

