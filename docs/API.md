# 📡 MarketMind AI - API Reference

Complete API documentation for interacting with MarketMind AI agent.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Request Format](#request-format)
- [Response Format](#response-format)
- [Query Syntax](#query-syntax)
- [Error Codes](#error-codes)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [Client Libraries](#client-libraries)

---

## Base URL

```
http://localhost:8080
```

For production deployments, replace with your actual domain.

---

## Authentication

Currently, the agent runs without authentication in development mode. For production deployments, consider adding:

- API key authentication
- JWT tokens
- OAuth 2.0
- IP whitelist

**Example with API Key** (future):
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8080/assist
```

---

## Endpoints

### POST `/assist`

Primary endpoint for submitting analysis requests.

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "session_id": "string (required)",
  "query": {
    "prompt": "string (required)"
  }
}
```

**Response**: Server-Sent Events (SSE) stream

**Response Content-Type**: `text/event-stream`

---

### GET `/health` (Recommended to implement)

Health check endpoint for monitoring.

**Method**: `GET`

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "redis": "connected",
  "timestamp": "2025-11-07T17:00:00Z"
}
```

---

## Request Format

### Complete Request Example

```bash
curl -X POST http://localhost:8080/assist \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123-session-456",
    "query": {
      "prompt": "Give me channel analysis for stripe.com"
    }
  }'
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique identifier for the session. Used for tracking and rate limiting. |
| `query.prompt` | string | Yes | Natural language query or command. See [Query Syntax](#query-syntax) for details. |

### Session ID Format

Session IDs should be:
- **Unique** per user session
- **Persistent** across multiple requests
- **Format**: Any string, recommended: `{user_id}-{session_id}`

**Examples**:
```
"user-123-session-456"
"alice-2025-11-07-001"
"test-session-001"
```

---

## Response Format

### Server-Sent Events (SSE) Stream

The agent streams responses in real-time using SSE format.

### Event Types

#### 1. Text Block Event

Progress updates and messages.

```json
{
  "type": "text_block",
  "block_id": "ANALYSIS_START",
  "content": "🔍 Starting Market Research for Stripe\n\n📍 Website: https://stripe.com..."
}
```

#### 2. Text Stream Event

Streaming analysis results.

```json
{
  "type": "text_stream",
  "stream_id": "FINAL_RESPONSE",
  "chunk": "# Company Overview\n\nStripe is a financial infrastructure..."
}
```

#### 3. JSON Event

Structured data (optional).

```json
{
  "type": "json",
  "block_id": "SMARTCRAWLER_COMPLETE",
  "data": {
    "status": "success",
    "data_length": 5432
  }
}
```

#### 4. Complete Event

Signals end of stream.

```json
{
  "type": "complete"
}
```

### Complete Response Flow

```
1. ANALYSIS_START (text_block)
   └─> "🔍 Starting Market Research for Stripe..."

2. DATA_COLLECTION (text_block)
   └─> "🕷️ Step 1/3: Crawling company website..."

3. SMARTCRAWLER_KEEPALIVE_1 (text_block)
   └─> "⏳ Still processing smartcrawler... (15s elapsed)"

4. SMARTCRAWLER_KEEPALIVE_2 (text_block)
   └─> "⏳ Still processing smartcrawler... (30s elapsed)"

5. SMARTCRAWLER_COMPLETE (json)
   └─> {"status": "success", "data_length": 5432}

6. COMPETITOR_SEARCH (text_block)
   └─> "🔍 Step 2/3: Searching for competitor intelligence..."

7. SEARCHSCRAPER_KEEPALIVE_1 (text_block)
   └─> "⏳ Still processing searchscraper... (15s elapsed)"

8. SEARCHSCRAPER_COMPLETE (json)
   └─> {"status": "success", "data_length": 3210}

9. AGENT_PROCESSING (text_block)
   └─> "🤖 Step 3/3: Generating Market Research analysis..."

10. FINAL_RESPONSE (text_stream) - Multiple chunks
    └─> Chunk 1: "# Company Overview\n\nStripe is..."
    └─> Chunk 2: "a financial infrastructure platform..."
    └─> Chunk 3: "that enables businesses to accept payments..."
    └─> ... (continues streaming)

11. COMPLETE (complete)
    └─> End of stream
```

---

## Query Syntax

### Natural Language Queries (Recommended)

Simply describe what you want in plain English.

**Research Analysis**:
```
"Research stripe.com"
"Give me competitive intelligence on shopify.com"
"Analyze github.com for market insights"
"I need company research for https://airbnb.com"
```

**Go-To-Market Strategy**:
```
"Create go-to-market strategy for stripe.com"
"I need GTM playbook for shopify.com"
"Give me launch strategy for github.com"
"go to market plan for airbnb.com"
```

**Channel Strategy**:
```
"Give me channel analysis for stripe.com"
"What are the best distribution channels for shopify.com?"
"channel strategy for github.com"
"How should airbnb.com distribute their product?"
```

### Legacy Format (Also Supported)

```
"{url} | {analysis_type}"
```

**Examples**:
```
"stripe.com | research"
"https://shopify.com | go-to-market"
"www.github.com | channel"
```

### URL Formats Supported

```
✅ https://example.com
✅ http://example.com
✅ www.example.com
✅ example.com
✅ subdomain.example.com

❌ example (no TLD)
❌ file://example.com
❌ ftp://example.com
```

### Analysis Types

| Type | Description | Keywords |
|------|-------------|----------|
| **research** | Company overview, competitors, market trends | research, analyze, study, investigate, intel |
| **go-to-market** | GTM strategy, ICP, messaging, pricing | gtm, go-to-market, launch, strategy, market strategy |
| **channel** | Distribution channels, partnerships, economics | channel, distribution, sales channel, marketing channel |

---

## Error Codes

### Error Response Format

Errors are returned as text blocks with descriptive messages.

```json
{
  "type": "text_block",
  "block_id": "ERROR_TYPE",
  "content": "❌ Error message with details..."
}
```

### Common Errors

#### 1. Invalid URL Format

**Block ID**: `URL_VALIDATION_ERROR`

```
❌ Invalid URL format: 'invalid-url'

Please provide a valid URL:
✅ https://example.com
✅ www.example.com
✅ example.com

Example requests:
• "Give me channel analysis for stripe.com"
• "I need go-to-market strategy for https://github.com"
• "Research shopify.com"
```

#### 2. Rate Limit Exceeded

**Block ID**: `RATE_LIMIT_ERROR`

```
⚠️ Rate Limit Exceeded

User rate limit exceeded: 3 requests per minute

Please wait a moment before making more requests.
This helps ensure optimal performance for all users.
```

#### 3. Parsing Error

**Block ID**: `PARSING_ERROR`

```
❌ No URL detected in your request.

I need a company website URL to analyze. Please try again with:

Examples:
• "Give me a channel analysis for example.com"
• "I need go-to-market strategy for https://github.com"
• "Research shopify.com for me"
```

#### 4. Timeout Error

**Block ID**: `TIMEOUT_ERROR`

```
⏱️ Operation Timed Out

SMARTCRAWLER operation exceeded timeout

This can happen when:
• The website is very large or slow to respond
• The website blocks automated crawling
• Network issues

Please try again or try a different website.
```

#### 5. System Error

**Block ID**: `SYSTEM_ERROR`

```
❌ An unexpected error occurred:

```
[Error details]
```

Please try again or contact support if the issue persists.
```

---

## Rate Limiting

### Limits

| Scope | Limit | Window |
|-------|-------|--------|
| Per User | 3 requests | 60 seconds |
| Platform-wide | 200 requests | 60 seconds |

### Rate Limit Headers (Future)

Recommended headers to implement:

```
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1699372860
```

### Handling Rate Limits

When rate limited, the client should:
1. Wait for the window to reset (60 seconds)
2. Implement exponential backoff
3. Display user-friendly message

**Example Retry Logic**:
```python
import time

def request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=payload)
        
        if "RATE_LIMIT_ERROR" in response.text:
            wait_time = 60 * (2 ** attempt)  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

---

## Examples

### Example 1: Research Analysis (Python)

```python
import requests
import json

url = "http://localhost:8080/assist"

payload = {
    "session_id": "python-client-001",
    "query": {
        "prompt": "Research stripe.com for competitive intelligence"
    }
}

response = requests.post(url, json=payload, stream=True)

for line in response.iter_lines():
    if line:
        try:
            event = json.loads(line.decode('utf-8'))
            
            if event.get("type") == "text_block":
                print(f"\n{event['content']}")
            
            elif event.get("type") == "text_stream":
                print(event['chunk'], end="", flush=True)
            
            elif event.get("type") == "complete":
                print("\n\n✅ Analysis complete!")
                break
        except:
            continue
```

### Example 2: Go-To-Market Strategy (cURL)

```bash
curl -X POST http://localhost:8080/assist \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "curl-client-002",
    "query": {
      "prompt": "Create go-to-market strategy for shopify.com"
    }
  }' \
  --no-buffer
```

### Example 3: Channel Analysis (JavaScript/Node.js)

```javascript
const fetch = require('node-fetch');

async function analyzeChannel(companyUrl) {
  const response = await fetch('http://localhost:8080/assist', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: `js-client-${Date.now()}`,
      query: {
        prompt: `Give me channel analysis for ${companyUrl}`
      }
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.trim()) {
        try {
          const event = JSON.parse(line);
          
          if (event.type === 'text_block') {
            console.log(`\n${event.content}`);
          } else if (event.type === 'text_stream') {
            process.stdout.write(event.chunk);
          } else if (event.type === 'complete') {
            console.log('\n\n✅ Analysis complete!');
            return;
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }
  }
}

// Usage
analyzeChannel('stripe.com');
```

### Example 4: Batch Processing (Python)

```python
import asyncio
import aiohttp

async def analyze_company(session, company_url, analysis_type):
    url = "http://localhost:8080/assist"
    
    payload = {
        "session_id": f"batch-{company_url}",
        "query": {
            "prompt": f"{analysis_type} {company_url}"
        }
    }
    
    async with session.post(url, json=payload) as response:
        result = []
        async for line in response.content:
            if line:
                try:
                    event = json.loads(line.decode('utf-8'))
                    if event.get("type") == "text_stream":
                        result.append(event['chunk'])
                except:
                    continue
        
        return ''.join(result)

async def batch_analyze(companies):
    async with aiohttp.ClientSession() as session:
        tasks = [
            analyze_company(session, url, "research")
            for url in companies
        ]
        results = await asyncio.gather(*tasks)
        return results

# Usage
companies = ["stripe.com", "shopify.com", "square.com"]
results = asyncio.run(batch_analyze(companies))

for company, analysis in zip(companies, results):
    print(f"\n{'='*50}")
    print(f"Analysis for {company}")
    print(f"{'='*50}")
    print(analysis)
```

---

## Client Libraries

### Official Sentient Client

```bash
# Install
npm install -g @sentient-xyz/client

# Usage
sentient assist "Research stripe.com" \
  --agent-url http://localhost:8080 \
  --session-id my-session-123
```

### Python Client (Recommended)

```python
from sentient_agent_framework import Client

client = Client(agent_url="http://localhost:8080")

# Simple request
response = client.assist(
    session_id="python-session",
    prompt="Research stripe.com"
)

# Streaming
for chunk in response:
    print(chunk, end="", flush=True)
```

### Custom Client Implementation

If you need a custom client, implement these features:

1. **SSE Parsing**: Handle Server-Sent Events format
2. **Error Handling**: Catch and handle error events
3. **Retry Logic**: Implement exponential backoff for rate limits
4. **Streaming Display**: Stream output to user in real-time
5. **Timeout Handling**: Set appropriate timeouts (5+ minutes)

---

## Best Practices

### 1. Session Management

```python
# ✅ GOOD: Unique session per user
session_id = f"user-{user_id}-{timestamp}"

# ❌ BAD: Reusing same session ID
session_id = "default-session"  # Don't do this
```

### 2. Error Handling

```python
# ✅ GOOD: Handle all event types
if event['type'] == 'text_block':
    if 'ERROR' in event['block_id']:
        handle_error(event['content'])
    else:
        display_message(event['content'])

# ❌ BAD: Ignore errors
if event['type'] == 'text_stream':
    print(event['chunk'])  # Misses errors
```

### 3. Timeout Configuration

```python
# ✅ GOOD: Long timeout for analysis
response = requests.post(url, json=payload, timeout=600)  # 10 min

# ❌ BAD: Short timeout
response = requests.post(url, json=payload, timeout=30)  # 30s - too short!
```

### 4. Rate Limit Respect

```python
# ✅ GOOD: Check rate limit response
if "RATE_LIMIT_ERROR" in response:
    time.sleep(60)  # Wait for window reset
    retry_request()

# ❌ BAD: Ignore rate limits
while True:
    make_request()  # Spam the API
```

### 5. Resource Cleanup

```python
# ✅ GOOD: Proper cleanup
response = requests.post(url, json=payload, stream=True)
try:
    for line in response.iter_lines():
        process(line)
finally:
    response.close()  # Always close

# ❌ BAD: No cleanup
response = requests.post(url, json=payload, stream=True)
for line in response.iter_lines():
    process(line)
# Connection left open
```

---

## Testing

### Test with cURL

```bash
# Basic test
curl -X POST http://localhost:8080/assist \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","query":{"prompt":"stripe.com | research"}}'

# With verbose output
curl -v -X POST http://localhost:8080/assist \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","query":{"prompt":"Research github.com"}}'

# Save output to file
curl -X POST http://localhost:8080/assist \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","query":{"prompt":"shopify.com | go-to-market"}}' \
  > analysis.txt
```

### Test with Python Script

```python
import requests
import json

def test_agent():
    url = "http://localhost:8080/assist"
    
    test_cases = [
        "Research stripe.com",
        "github.com | go-to-market",
        "Give me channel analysis for shopify.com",
    ]
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"\nTest {i}: {prompt}")
        print("-" * 50)
        
        payload = {
            "session_id": f"test-{i}",
            "query": {"prompt": prompt}
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=600)
        
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line.decode('utf-8'))
                    if event.get("type") == "text_stream":
                        print(event['chunk'], end="", flush=True)
                except:
                    pass
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_agent()
```

---

## Webhooks (Future Feature)

For long-running analyses, consider implementing webhooks:

**Request**:
```json
{
  "session_id": "webhook-session",
  "query": {"prompt": "Research stripe.com"},
  "webhook_url": "https://your-app.com/webhook",
  "webhook_secret": "your_secret_key"
}
```

**Webhook Payload**:
```json
{
  "session_id": "webhook-session",
  "status": "complete",
  "analysis": "# Company Overview\n...",
  "timestamp": "2025-11-07T17:30:00Z",
  "signature": "hmac_sha256_signature"
}
```

---

For more details, see:
- [Architecture Documentation](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Contributing Guidelines](CONTRIBUTING.md)
