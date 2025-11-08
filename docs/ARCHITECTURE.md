# 🏗️ MarketMind AI - Technical Architecture

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Thread Management](#thread-management)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)

---

## System Overview

MarketMind AI is built on a **microservices-inspired architecture** using the Sentient Agent Framework as the orchestration layer. The system is designed for:

- **Scalability**: Per-request isolation with thread pool executors
- **Reliability**: Retry logic, timeouts, and graceful degradation
- **Performance**: Redis caching with intelligent cache invalidation
- **Maintainability**: Clean separation of concerns with modular components

### Key Design Principles

1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Fail-Safe Defaults**: System continues operation even if non-critical components fail
3. **Resource Cleanup**: Explicit cleanup of threads, connections, and file handles
4. **Observability**: Comprehensive logging at every layer
5. **Idempotency**: Requests can be safely retried without side effects

---

## Component Architecture

### 1. Agent Layer (`app/agent/`)

#### `gtm_agent.py` - Main Orchestrator

**Responsibilities**:
- Query routing and validation
- Thread pool management (per-request executors)
- Progress streaming with keepalive messages
- Cache coordination
- Error handling and recovery

**Key Features**:
```python
class SmartGTMAgent(AbstractAgent):
    async def assist(self, session, query, response_handler):
        # Per-request executor (prevents thread leaks)
        request_executor = ThreadPoolExecutor(max_workers=3)
        request_handlers = AnalysisHandlers(request_executor)
        
        try:
            # 1. Parse query (natural language)
            url, feature, error = parse_query(query.prompt)
            
            # 2. Rate limit check (Redis)
            allowed, msg = rate_limiter.check_rate_limit(user_id)
            
            # 3. Cache check (Redis)
            cached = cache_manager.get(url, feature)
            
            # 4. Data collection (with timeout)
            crawler_data = await self._run_with_keepalive(
                request_executor,
                smartcrawler_service.crawl,
                response_handler,
                "SMARTCRAWLER",
                300,  # 5 min timeout
                url
            )
            
            # 5. Analysis generation (streaming)
            async for chunk in request_handlers.run_research_analysis(data):
                await response_handler.stream(chunk)
                
        finally:
            # CRITICAL: Always cleanup executor
            request_executor.shutdown(wait=True, cancel_futures=True)
```

**Thread Management Strategy**:
- Creates fresh `ThreadPoolExecutor` per request
- Guarantees cleanup in `finally` block
- Prevents thread leaks across requests
- Logs thread count at key points

#### `handlers.py` - Analysis Handlers

**Responsibilities**:
- Execute LLM analysis in thread pool
- Stream results in chunks
- Apply domain-specific prompts

**Handler Types**:
```python
class AnalysisHandlers:
    async def run_research_analysis(self, context: str) -> AsyncIterator[str]:
        # Apply research prompt template
        # Run LLM in executor
        # Stream results in 100-char chunks
        
    async def run_gtm_analysis(self, context: str) -> AsyncIterator[str]:
        # Apply GTM strategy prompt template
        
    async def run_channel_analysis(self, context: str) -> AsyncIterator[str]:
        # Apply channel strategy prompt template
```

---

### 2. Core Layer (`app/core/`)

#### `query_parser.py` - Natural Language Understanding

**Capabilities**:
- Extract URLs from natural language
- Identify analysis type (research/gtm/channel)
- Support legacy pipe format (`url | type`)
- Generate helpful error messages

**Parsing Logic**:
```python
class QueryParser:
    # Pattern 1: URLs with protocol
    https?://example.com
    
    # Pattern 2: www domains
    www.example.com
    
    # Pattern 3: Bare domains
    example.com
    
    # Keyword matching for analysis types
    ANALYSIS_KEYWORDS = {
        'research': ['research', 'analyze', 'study', 'investigate'],
        'go-to-market': ['gtm', 'go-to-market', 'launch', 'strategy'],
        'channel': ['channel', 'distribution', 'sales channel']
    }
```

#### `rate_limiter.py` - Redis Rate Limiting

**Strategy**: Token bucket algorithm using Redis sorted sets

```python
class RateLimiter:
    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        # 1. Remove expired entries (outside time window)
        window_start = current_time - 60  # 60 second window
        redis.zremrangebyscore(user_key, 0, window_start)
        
        # 2. Count requests in window
        count = redis.zcard(user_key)
        
        # 3. Check against limits
        if count >= RATE_LIMIT_PER_USER:
            return False, "Rate limit exceeded"
        
        # 4. Add current request
        redis.zadd(user_key, {request_id: current_time})
        
        # 5. Set expiry (auto-cleanup)
        redis.expire(user_key, 120)  # 2x window
        
        return True, f"{remaining} requests remaining"
```

**Limits**:
- Per-user: 3 requests/minute
- Platform-wide: 200 requests/minute

#### `cache.py` - Redis Response Caching

**Strategy**: URL + feature as composite key

```python
class CacheManager:
    def _generate_cache_key(self, url: str, feature: str) -> str:
        # Extract domain: https://stripe.com → stripe.com
        domain = extract_domain(url)
        
        # Create composite key
        key_content = f"{domain}:{feature}"
        
        # Hash for consistent length
        key_hash = hashlib.md5(key_content.encode()).hexdigest()
        
        return f"cache:analysis:{feature}:{key_hash}"
    
    def get(self, url: str, feature: str) -> Optional[dict]:
        # Returns: {"analysis": "...", "company_name": "...", ...}
        
    def set(self, url: str, feature: str, data: dict) -> bool:
        # Store with 7-day TTL
        redis.setex(cache_key, 604800, json.dumps(data))
```

**Cache Structure**:
```json
{
  "url": "https://stripe.com",
  "feature": "research",
  "data": {
    "analysis": "# Company Overview\n...",
    "company_name": "Stripe",
    "crawler_data_length": 5432,
    "search_data_length": 3210
  },
  "cached_at": 1699372800
}
```

#### `url_validator.py` - URL Normalization

**Transformations**:
```python
# Input variations → Normalized output
"stripe.com"           → "https://stripe.com"
"www.stripe.com"       → "https://www.stripe.com"
"http://stripe.com"    → "http://stripe.com"  (preserved)
"https://stripe.com"   → "https://stripe.com" (no change)

# Validation checks:
✓ Has scheme (http/https)
✓ Has netloc (domain)
✓ Domain contains '.' or is 'localhost'
✗ Invalid TLD (file extensions)
✗ Missing domain
```

---

### 3. Services Layer (`app/services/`)

#### `smartcrawler.py` - Website Crawling

**API**: ScrapeGraph SmartCrawler

**Process**:
```python
def crawl(self, url: str) -> str:
    # 1. Start crawl job
    response = client.crawl(
        url=url,
        prompt="Extract detailed company information",
        data_schema={...},
        depth=2,  # 2 levels deep
        max_pages=5,  # Max 5 pages
        same_domain_only=True
    )
    
    # 2. Get crawl ID
    crawl_id = response["id"]
    
    # 3. Poll for results (5 min timeout)
    for attempt in range(60):  # 60 × 5s = 5 min
        time.sleep(5)
        result = client.get_crawl(crawl_id)
        
        if result["status"] == "success":
            # 4. Process markdown content
            pages = result["result"]["pages"]
            markdown = "\n\n".join(p["markdown"] for p in pages)
            
            # 5. LLM summarize
            summary = llm_service.invoke(
                "Summarize this company data:\n" + markdown
            )
            return summary
```

**Retry Logic**:
- 2 attempts with exponential backoff
- Handles `RemoteDisconnected` errors
- Falls back gracefully on failure

#### `searchscraper.py` - Competitive Intelligence

**API**: ScrapeGraph SearchScraper

**Multi-Query Strategy**:
```python
def search_competitors(self, company_overview: str, company_url: str) -> str:
    company_name = extract_from_url(company_url)
    
    # Execute 5 targeted queries
    queries = [
        f"{company_name} competitors direct rivals",
        f"{company_name} vs alternative similar companies",
        f"{company_name} founders CEO leadership team funding",
        f"{company_name} revenue business model market size TAM SAM SOM",
        f"{company_name} company history and founders"
    ]
    
    all_results = []
    for query in queries:
        result = self._search_request(query, num_results=5)
        all_results.append(result["result"])
    
    # Combine and analyze
    combined_data = combine_search_results(all_results)
    analysis = generate_competitor_analysis(combined_data)
    
    return analysis
```

**Company Name Extraction**:
```python
# Special handling for common platforms
common_platforms = ['github.com', 'google.com', 'facebook.com', ...]

if domain in common_platforms:
    return domain  # Use full domain
else:
    return format_domain_name(domain.split('.')[0])  # Extract main part
```

#### `llm_service.py` - AI Analysis

**Provider**: Nebius AI (Hermes-4-70B model)

```python
class LLMService:
    def __init__(self):
        self.llm = ChatNebius(
            model="NousResearch/Hermes-4-70B",
            api_key=SecretStr(settings.NEBIUS_API_KEY)
        )
    
    def invoke(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return response.content
```

**Model Selection**:
- **Hermes-4-70B**: Balanced performance and cost
- Strong reasoning capabilities for market analysis
- Good at structured output generation

---

### 4. Prompts Layer (`app/prompts/`)

#### Prompt Engineering Strategy

**Structure**:
1. Role definition ("You are a professional GTM Strategist")
2. Task description (clear, specific objectives)
3. Output requirements (format, structure, depth)
4. Data context (crawler + scraper data)

**Example: Research Prompt**
```python
RESEARCH_PROMPT_TEMPLATE = """You are a professional Company Research & Market Intelligence Assistant.

Analyze the provided company and competitor data and create a comprehensive research report.

Structure your report with these sections:

1. **Company Overview** – history, mission, vision, key offerings
2. **Founders & Leadership** – key people and their background
3. **Funding & Financials** – funding rounds, investors, financial health
4. **Industry & Market Size** – sector, growth rate, TAM/SAM/SOM if available
5. **Competitors** – top direct & indirect competitors with brief comparison
6. **Market Insights & Trends** – opportunities, risks, and emerging trends
7. **Assumptions & Gaps** – list any missing or uncertain information

Guidelines:
- Be concise, factual, and business-ready
- Use bullet points where appropriate
- Include units (USD, %, year) for numbers
- State uncertainty explicitly when data is missing or unclear
- Focus on actionable insights for strategic decision-making

DATA TO ANALYZE:
{context}

Provide your comprehensive research report below:
"""
```

---

## Data Flow

### Complete Request Lifecycle

```
1. CLIENT REQUEST
   └─> POST /assist
       {
         "session_id": "user-123",
         "query": {"prompt": "Research stripe.com"}
       }

2. SENTIENT FRAMEWORK
   └─> Validate request
   └─> Create Session object
   └─> Create Query object
   └─> Create ResponseHandler
   └─> Call agent.assist()

3. AGENT ORCHESTRATION
   ├─> Parse query
   │   └─> URL: "https://stripe.com"
   │   └─> Type: "research"
   │
   ├─> Rate limit check (Redis)
   │   └─> User: 2/3 remaining ✓
   │   └─> Platform: 195/200 remaining ✓
   │
   ├─> Cache check (Redis)
   │   └─> Key: "cache:analysis:research:md5hash"
   │   └─> Result: MISS
   │
   └─> Create executor (3 workers)

4. DATA COLLECTION PHASE
   ├─> SmartCrawler (Worker Thread 1)
   │   ├─> Start crawl job
   │   │   └─> Depth: 2, Max pages: 5
   │   │
   │   ├─> Poll status (every 5s)
   │   │   └─> Status: queued → processing → success
   │   │
   │   ├─> Extract markdown
   │   │   └─> 5 pages, ~8KB content
   │   │
   │   └─> LLM summarize
   │       └─> Prompt: "Summarize this company data..."
   │       └─> Result: Structured company overview
   │
   └─> SearchScraper (Worker Thread 2)
       ├─> Query 1: "Stripe competitors direct rivals"
       │   └─> 5 results
       ├─> Query 2: "Stripe vs alternative companies"
       │   └─> 5 results
       ├─> Query 3: "Stripe founders CEO leadership"
       │   └─> 5 results
       ├─> Query 4: "Stripe revenue business model"
       │   └─> 5 results
       └─> Query 5: "Stripe company history"
           └─> 5 results
       
       └─> LLM analyze competitors
           └─> Prompt: "Analyze competitor data..."
           └─> Result: Competitive intelligence report

5. ANALYSIS GENERATION PHASE
   └─> Combine data
       └─> Crawler: Company overview
       └─> Scraper: Competitor intelligence
   
   └─> Apply research prompt (Worker Thread 3)
       └─> LLM: Generate comprehensive analysis
       
   └─> Stream results
       └─> Chunk 1: "# Company Overview\nStripe is..."
       └─> Chunk 2: "a financial infrastructure..."
       └─> ... (streaming in 100-char chunks)

6. CACHING & CLEANUP
   ├─> Store in Redis
   │   └─> Key: "cache:analysis:research:md5hash"
   │   └─> TTL: 7 days
   │
   └─> Cleanup executor
       └─> Shutdown threads
       └─> Release resources

7. RESPONSE COMPLETE
   └─> Send completion event
   └─> Close connection
```

### Keepalive Messages

```
Purpose: Prevent client timeout during long operations

Strategy:
- Send message every 15 seconds
- Include elapsed time
- Continue until operation completes

Example Flow:
T=0s:   "🕷️ Step 1/3: Crawling company website..."
T=15s:  "⏳ Still processing smartcrawler... (15s elapsed)"
T=30s:  "⏳ Still processing smartcrawler... (30s elapsed)"
T=45s:  [Crawl completes]
        "🔍 Step 2/3: Searching for competitor intelligence..."
```

---

## Thread Management

### Problem: Thread Leaks

**Before v2.0.0** (Problematic):
```python
class SmartGTMAgent:
    def __init__(self):
        # PROBLEM: Shared executor across all requests
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    async def assist(self, ...):
        # All requests use same executor
        await loop.run_in_executor(self.executor, blocking_func)
        # Threads never fully release

# Result:
Request 1: 🧵 1 → 4 → 4 ❌ (leaks 3 threads)
Request 2: 🧵 4 → 7 → 7 ❌ (leaks 3 more threads)
Request 3: 🧵 7 → 10 → 10 ❌ (keeps growing)
```

**After v2.0.0** (Fixed):
```python
class SmartGTMAgent:
    def __init__(self):
        # Don't create shared executor
        self.executor = None
    
    async def assist(self, ...):
        # Create fresh executor per request
        request_executor = ThreadPoolExecutor(
            max_workers=3,
            thread_name_prefix=f"gtm_req_{id(query)}_"
        )
        
        try:
            # Use executor for this request only
            await loop.run_in_executor(request_executor, blocking_func)
        finally:
            # CRITICAL: Always cleanup
            request_executor.shutdown(wait=True, cancel_futures=True)

# Result:
Request 1: 🧵 1 → 4 → 1 ✓ (cleanup successful)
Request 2: 🧵 1 → 4 → 1 ✓ (isolated executor)
Request 3: 🧵 1 → 4 → 1 ✓ (no leaks)
```

### Thread Pool Sizing

```python
max_workers = 3

# Worker 1: SmartCrawler (blocking I/O)
# Worker 2: SearchScraper (blocking I/O)
# Worker 3: LLM Analysis (blocking I/O)

# Why 3?
# - Each request needs max 3 concurrent operations
# - Prevents thread exhaustion
# - Balances parallelism vs overhead
```

---

## Error Handling

### Multi-Layer Error Handling

```python
# Layer 1: Service Level (Retry)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def _search_request(self, query):
    try:
        return self.client.searchscraper(query)
    except RemoteDisconnected:
        logger.warning("RemoteDisconnected, retrying...")
        raise  # Trigger retry

# Layer 2: Agent Level (Timeout)
try:
    result = await asyncio.wait_for(
        loop.run_in_executor(executor, func, *args),
        timeout=300  # 5 minutes
    )
except asyncio.TimeoutError:
    await response_handler.emit_text_block(
        "TIMEOUT_ERROR",
        "⏱️ Operation Timed Out\n\nThe website may be too large..."
    )

# Layer 3: Top Level (Catch-All)
try:
    # ... entire request processing ...
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    await response_handler.emit_text_block(
        "SYSTEM_ERROR",
        f"❌ An unexpected error occurred: {str(e)}"
    )
finally:
    # Always cleanup resources
    executor.shutdown(wait=True, cancel_futures=True)
```

### Graceful Degradation

```python
# If SmartCrawler fails, continue with SearchScraper only
try:
    crawler_data = await smartcrawler_service.crawl(url)
except Exception as e:
    logger.warning(f"Crawler failed: {e}")
    crawler_data = "⚠️ Website crawl unavailable"

# If SearchScraper fails, continue with crawler data only
try:
    search_data = await searchscraper_service.search(url)
except Exception as e:
    logger.warning(f"Search failed: {e}")
    search_data = "⚠️ Competitor search unavailable"

# Combine whatever data we have
combined = f"Crawler: {crawler_data}\n\nSearch: {search_data}"

# Analysis continues with available data
```

---

## Performance Optimization

### 1. Caching Strategy

```python
# Cache Hit Path (< 2 seconds)
Request → Rate Check → Cache HIT → Stream Cached Data → Complete

# Cache Miss Path (2-5 minutes)
Request → Rate Check → Cache MISS → Crawl → Search → Analyze → Cache Store → Complete
```

**Cache Effectiveness**:
- First request: 2-5 minutes (full analysis)
- Subsequent requests: < 2 seconds (from cache)
- Cache hit rate: ~60% for popular companies

### 2. Parallel Data Collection

```python
# Sequential (slow) - 8 minutes total
crawler_data = await crawl(url)  # 5 min
search_data = await search(url)  # 3 min

# Parallel (fast) - 5 minutes total (limited by slowest)
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(crawl(url))   # 5 min
    task2 = tg.create_task(search(url))  # 3 min
# Both complete after 5 min (max of the two)
```

### 3. Content Truncation

```python
# Limit content size to prevent memory issues
MAX_CONTENT_LENGTH = 10000  # 10KB crawler data
MAX_SEARCH_DATA_LENGTH = 8000  # 8KB search data

if len(content) > MAX_CONTENT_LENGTH:
    content = content[:MAX_CONTENT_LENGTH]
    content += "\n\n[Content truncated due to length]"
```

### 4. Streaming Responses

```python
# Stream in chunks (better UX, lower memory)
STREAM_CHUNK_SIZE = 100  # characters

for i in range(0, len(result), STREAM_CHUNK_SIZE):
    chunk = result[i:i + STREAM_CHUNK_SIZE]
    await response_handler.emit_chunk(chunk)
    await asyncio.sleep(0.01)  # Yield control
```

---

## Security Considerations

### 1. API Key Management

```python
# ✓ GOOD: Environment variables
NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")

# ✗ BAD: Hardcoded
NEBIUS_API_KEY = "sk-abc123..."  # Never do this!

# ✓ GOOD: SecretStr for sensitive data
self.llm = ChatNebius(
    api_key=SecretStr(settings.NEBIUS_API_KEY)
)
```

### 2. Rate Limiting

```python
# Prevents abuse and ensures fair usage
RATE_LIMIT_PER_USER = 3  # requests per minute
RATE_LIMIT_PLATFORM = 200  # platform-wide limit

# User isolation via unique IDs
user_id = session.user_id  # Each user tracked separately
```

### 3. Input Validation

```python
# URL validation prevents malicious inputs
def is_valid_url(url: str) -> bool:
    # ✓ Checks protocol (http/https only)
    # ✓ Validates domain format
    # ✗ Rejects file:// and other protocols
    # ✗ Rejects localhost (except explicitly allowed)
```

### 4. Resource Limits

```python
# Timeout protection
CRAWL_TIMEOUT = 300  # Max 5 minutes per crawl
SEARCH_TIMEOUT = 180  # Max 3 minutes per search

# Content limits
MAX_CONTENT_LENGTH = 10000  # Prevent memory exhaustion

# Thread limits
max_workers = 3  # Prevent thread pool exhaustion
```

### 5. Error Information Disclosure

```python
# ✓ GOOD: Generic error to client
"❌ An unexpected error occurred. Please try again."

# ✓ GOOD: Detailed logging server-side
logger.error(f"Database error: {e}", exc_info=True)

# ✗ BAD: Expose internal details to client
f"❌ Error: Database connection failed at 192.168.1.100:5432"
```

---

## Observability

### Logging Strategy

```python
# Structured logging with levels
logger.info("✅ Parsed query - URL: {url}, Type: {type}")  # Important events
logger.debug("Attempting cache lookup...")  # Debug details
logger.warning("⚠️ Redis not available, caching disabled")  # Degraded state
logger.error("❌ Crawler failed: {error}", exc_info=True)  # Errors with stack trace
```

### Key Metrics to Monitor

```python
# Performance Metrics
- Request latency (p50, p95, p99)
- Cache hit rate
- Thread count (should return to baseline)
- Memory usage per request

# Operational Metrics
- Rate limit hits (per user, platform)
- API quota usage (Nebius, ScrapeGraph)
- Redis connection health
- Error rates by type

# Business Metrics
- Requests per analysis type
- Popular companies (most queried)
- User retention
- Cache effectiveness
```

---

## Deployment Considerations

### Production Checklist

- [ ] Redis persistence enabled (RDB or AOF)
- [ ] Proper logging aggregation (e.g., ELK stack)
- [ ] Health check endpoint
- [ ] Graceful shutdown handling
- [ ] Environment-specific configs
- [ ] Monitoring and alerting
- [ ] Rate limit tuning for scale
- [ ] API key rotation policy
- [ ] Backup and disaster recovery

### Scaling Strategies

```python
# Horizontal Scaling
- Multiple agent instances behind load balancer
- Shared Redis cluster for consistency
- Distributed rate limiting

# Vertical Scaling
- Increase thread pool size (test for optimal)
- More memory for caching
- Faster Redis (cluster mode)

# Database Optimization
- Redis Cluster for high availability
- Read replicas for cache hits
- Eviction policy tuning
```

---

This architecture is designed for **reliability, performance, and maintainability** at scale. Each component is independently testable, and the system degrades gracefully when components fail.
