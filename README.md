# 🚀 MarketMind AI - Intelligent Go-To-Market Research Agent

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

**AI-Powered Market Intelligence & GTM Strategy Assistant**

[Features](#-features) • [Architecture](#-architecture) • [Usage](#-usage) • [API Reference](#-api-reference)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#%EF%B8%8F-architecture)
- [Technology Stack](#-technology-stack-1)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**MarketMind AI** is an intelligent autonomous agent that performs comprehensive market research and generates actionable Go-To-Market strategies for any company. Built on the **Sentient Agent Framework**, it combines advanced web crawling, competitive intelligence gathering, and AI-powered analysis to deliver professional-grade insights in minutes.

### What It Does

- 🔍 **Deep Company Research** - Analyzes company websites, extracts key information about founders, funding, products, and market positioning
- 🏢 **Competitive Intelligence** - Identifies and analyzes direct competitors with detailed market positioning
- 🚀 **GTM Strategy Generation** - Creates comprehensive go-to-market playbooks with ICP, messaging, pricing, and distribution strategies
- 📢 **Channel Strategy** - Recommends optimal distribution channels with prioritization matrix and ROI analysis

### Why MarketMind AI?

- ⏱️ **Saves 20+ hours** of manual research per company
- 📊 **Professional-grade reports** ready for strategic decision-making
- 🤖 **Natural language interface** - No special syntax required
- 💾 **Smart caching** - Instant results for previously analyzed companies
- 🔒 **Enterprise-ready** - Rate limiting, Redis caching, proper error handling

---

## ✨ Features

### 🧠 Intelligent Analysis Types

| Analysis Type | Description | Use Case |
|--------------|-------------|----------|
| **🔍 Research** | Company overview, founders, funding, competitors, market trends | Due diligence, market entry planning |
| **🚀 Go-To-Market** | ICP, messaging, pricing, sales channels, growth tactics | Product launch, market expansion |
| **📢 Channel Strategy** | Distribution channels, partnerships, channel economics | Sales planning, partnership strategy |

### 🎨 Natural Language Queries

No complex syntax - just ask naturally:

```
✅ "Give me a channel analysis for stripe.com"
✅ "I need go-to-market strategy for https://github.com"
✅ "Research shopify.com for competitive intelligence"
✅ "airbnb.com | research" (legacy format also supported)
```

### 🔧 Advanced Capabilities

- **Multi-source Data Collection**: Combines website crawling + search engine data
- **Smart Caching**: Redis-backed caching with 7-day TTL
- **Rate Limiting**: User and platform-wide limits for fair usage
- **Streaming Responses**: Real-time progress updates.
- **Thread-safe Processing**: Per-request executors prevent memory leaks
- **Timeout Protection**: 5-minute crawler timeout, 3-minute search timeout
- **Graceful Degradation**: Continues processing even if some data sources fail

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER QUERY                         │
│  (Sentient Client / cURL / HTTP POST)                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SENTIENT AGENT FRAMEWORK                    │
│  • Session Management  • Query Routing  • Response Streaming    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MARKETMIND AI AGENT                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  QUERY PARSER (Natural Language Understanding)          │   │
│  │  • Extract URLs from natural language                   │   │
│  │  • Identify analysis type (research/gtm/channel)        │   │
│  │  • Support legacy pipe format                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ORCHESTRATION LAYER                                    │   │
│  │  • Rate Limiting (Redis)                                │   │
│  │  • Cache Check (Redis)                                  │   │
│  │  • URL Validation & Normalization                       │   │
│  │  • Thread Pool Management (Per-Request Executors)       │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────┬───────────────────────────────┬─────────────────┘
                │                               │
    ┌───────────▼──────────┐       ┌───────────▼──────────┐
    │  DATA COLLECTION     │       │   ANALYSIS ENGINE    │
    │                      │       │                      │
    │  ┌────────────────┐ │       │  ┌────────────────┐ │
    │  │ SmartCrawler   │ │       │  │ Research       │ │
    │  │ (Website Data) │ │       │  │ Analyzer       │ │
    │  └────────────────┘ │       │  └────────────────┘ │
    │  • Depth: 2 levels  │       │  • LLM: Hermes-4   │ │
    │  • Max: 5 pages     │       │  • Structured      │ │
    │  • Timeout: 5 min   │       │    Prompts         │ │
    │                      │       │  • Stream Results  │ │
    │  ┌────────────────┐ │       │                      │
    │  │ SearchScraper  │ │       │  ┌────────────────┐ │
    │  │ (Competitor)   │ │       │  │ GTM Strategy   │ │
    │  └────────────────┘ │       │  │ Generator      │ │
    │  • 5 queries/run    │       │  └────────────────┘ │
    │  • 5 results each   │       │                      │
    │  • Timeout: 3 min   │       │  ┌────────────────┐ │
    │                      │       │  │ Channel        │ │
    │  ┌────────────────┐ │       │  │ Strategist     │ │
    │  │ LLM Summarizer │ │       │  └────────────────┘ │
    │  └────────────────┘ │       │                      │
    └──────────────────────┘       └──────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                ┌───────────────────────────────┐
                │     STORAGE & CACHING          │
                │  • Redis (Rate Limits)         │
                │  • Redis (Response Cache)      │
                │  • TTL: 7 days                 │
                └───────────────────────────────┘
```

### Request Flow

```
1. CLIENT REQUEST
   └─> Natural language query: "Research stripe.com"

2. QUERY PARSING
   ├─> Extract URL: "stripe.com" → "https://stripe.com"
   ├─> Identify type: "research"
   └─> Validate format

3. RATE LIMIT CHECK (Redis)
   ├─> User limit: 3/min ✓
   └─> Platform limit: 200/min ✓

4. CACHE CHECK (Redis)
   └─> Key: "cache:analysis:research:stripe.com"
       └─> MISS → Proceed to data collection

5. DATA COLLECTION (Parallel Executors)
   ├─> SmartCrawler (5 min timeout)
   │   ├─> Crawl website (depth=2, max=5 pages)
   │   ├─> Extract markdown content
   │   └─> LLM summarize → Company overview
   │
   └─> SearchScraper (3 min timeout)
       ├─> Query 1: "Stripe competitors direct rivals"
       ├─> Query 2: "Stripe vs alternative companies"
       ├─> Query 3: "Stripe founders CEO leadership"
       ├─> Query 4: "Stripe revenue business model"
       └─> Query 5: "Stripe company history"
       └─> LLM analyze → Competitive intelligence

6. ANALYSIS GENERATION (LLM)
   └─> Combine: crawler_data + search_data
       └─> Apply: RESEARCH_PROMPT_TEMPLATE
           └─> Stream: Results in 100-char chunks

7. CACHING (Redis)
   └─> Store: analysis + metadata
       └─> TTL: 7 days

8. RESPONSE STREAMING
   └─> Client receives: Real-time progress + final analysis

9. CLEANUP
   └─> Shutdown executor → Release threads
```

### Thread Management

```
Per-Request Isolation:
┌─────────────────────────────────────┐
│  Request 1                          │
│  ┌──────────────────────────────┐  │
│  │ Executor (3 workers)         │  │
│  │ • Thread 1: Crawler          │  │
│  │ • Thread 2: Scraper          │  │
│  │ • Thread 3: LLM              │  │
│  └──────────────────────────────┘  │
│  finally: executor.shutdown()      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Request 2 (Independent)            │
│  ┌──────────────────────────────┐  │
│  │ Fresh Executor (3 workers)   │  │
│  │ • No shared state            │  │
│  │ • Clean thread pool          │  │
│  └──────────────────────────────┘  │
│  finally: executor.shutdown()      │
└─────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Framework
- **[Sentient Agent Framework](https://github.com/sentient-agi/Sentient-Agent-Framework)** - Autonomous agent orchestration
- **Python 3.10+** - Runtime environment

### AI & NLP
- **[Nebius AI](https://nebius.ai/)** - LLM Provider (Hermes-4-70B model)
- **[LangChain](https://python.langchain.com/)** - LLM integration framework
- **Custom Query Parser** - Natural language understanding

### Data Collection
- **[ScrapeGraph](https://scrapegraph.io/)** - SmartCrawler & SearchScraper APIs
- **Tenacity** - Retry logic for resilient scraping

### Storage & Caching
- **[Redis](https://redis.io/)** - Rate limiting + response caching
- **TTL-based expiration** - 7-day cache lifetime

### Infrastructure
- **ThreadPoolExecutor** - Concurrent processing
- **AsyncIO** - Asynchronous orchestration
- **Pydantic** - Data validation

---

## 📦 Prerequisites

### Required
- **Python 3.10 or higher**
- **Redis Server** (local or cloud)
- **API Keys**:
  - Nebius AI API Key ([Get here](https://studio.nebius.ai/))
  - ScrapeGraph API Key ([Get here](https://dashboard.scrapegraph.ai/))

### Optional
- **Docker** (for containerized Redis)
- **Git** (for cloning repository)

---

## 🚀 Installation

### 1. Clone Repository

```bash
git clone https://github.com/Legendandy/Market-research-agent.git
cd Market-research-agent
```

### 2. Create Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n marketmind python=3.10
conda activate marketmind
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Redis

**Option A: Local Redis (Recommended for Development)**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

```

**Option B: Cloud Redis (Recommended for Production)**
- [Redis Cloud](https://redis.com/try-free/)
- [AWS ElastiCache](https://aws.amazon.com/elasticache/)
- [DigitalOcean Redis](https://www.digitalocean.com/products/managed-databases-redis)

### 5. Configure Environment

Edit `api.env` file in the root directory:

```bash
# Edit with your keys
nano api.env
```

---

## ⚙️ Configuration

### `api.env` Configuration

```bash
# Required: AI Provider
NEBIUS_API_KEY=your_nebius_api_key_here

# Required: Web Scraping
SMARTCRAWLER_API_KEY=your_scrapegraph_api_key_here

# Required: Redis Connection
REDIS_URL=redis://localhost:6379/0

# Optional: Rate Limiting (defaults shown)
RATE_LIMIT_PER_USER=3          # Max requests per user per minute
RATE_LIMIT_PLATFORM=200        # Max platform-wide requests per minute

# Optional: Caching (defaults shown)
CACHE_TTL_DAYS=7               # Cache expiration in days
```

### Advanced Configuration (`app/config/settings.py`)

```python
# SmartCrawler Settings
CRAWL_DEPTH = 2                # How deep to crawl (1-3)
CRAWL_MAX_PAGES = 5            # Max pages per domain (1-10)
CRAWL_TIMEOUT = 300            # Crawler timeout in seconds

# Content Limits
MAX_CONTENT_LENGTH = 10000     # Max crawler content length
MAX_SEARCH_DATA_LENGTH = 8000  # Max search data length

# Streaming
STREAM_CHUNK_SIZE = 100        # Characters per stream chunk
KEEPALIVE_INTERVAL = 15        # Keepalive message interval (seconds)
```

---

## 🎮 Usage

### Starting the Agent

```bash
python run.py
```

Expected output:
```
2025-11-07 17:00:00,000 - app.services.llm_service - INFO - ✅ LLM Service initialized
2025-11-07 17:00:00,001 - app.services.smartcrawler - INFO - ✅ SmartCrawler Service initialized
2025-11-07 17:00:00,002 - app.services.searchscraper - INFO - ✅ SearchScraper Service initialized
2025-11-07 17:00:00,003 - app.core.rate_limiter - INFO - ✅ Rate limiter connected to Redis
2025-11-07 17:00:00,004 - app.core.cache - INFO - ✅ Cache manager connected to Redis
2025-11-07 17:00:00,005 - app.agent.gtm_agent - INFO - ✅ Smart GTM Agent initialized successfully with natural language support
2025-11-07 17:00:00,006 - __main__ - INFO - 🚀 Starting Smart GTM Agent server on port 8080...
2025-11-07 17:00:00,007 - __main__ - INFO - 💡 Press Ctrl+C to stop gracefully
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Query Methods

#### Method 1: Sentient Client (Recommended)

```bash
# Install Sentient Client

git clone https://github.com/sentient-agi/Sentient-Agent-Client.git
cd Sentient-Agent-Client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.sentient_agent_client --url http://localhost:8000/assist


# Run query
"Give me channel analysis for stripe.com"
```

### Query Examples

#### Natural Language Queries (Recommended)

```bash
# Research Analysis
"Research stripe.com for me"
"Give me competitive intelligence on shopify.com"
"Analyze github.com"
"I need market research for https://airbnb.com"

# Go-To-Market Strategy
"Create go-to-market strategy for stripe.com"
"I need go-to-market playbook for shopify.com"
"Give me go-to-market strategy for github.com"
"go-to-market plan for airbnb.com"

# Channel Strategy
"Give me channel analysis for stripe.com"
"What are the best distribution channel for shopify.com?"
"channel strategy for github.com"
"How should airbnb.com channel their product?"
```

#### Legacy Format (Also Supported)

```bash
"stripe.com | research"
"https://shopify.com | go-to-market"
"www.github.com | channel"
```

### Expected Response Format

```
🔍 Starting Market Research for Stripe

📍 Website: https://stripe.com
⏱️ Estimated time: 2-5 minutes


🕷️ Step 1/3: Crawling company website for data extraction...
⏱️ This may take 2-3 minutes

⏳ Still processing smartcrawler... (15s elapsed)
⏳ Still processing smartcrawler... (30s elapsed)

🔍 Step 2/3: Searching for competitor intelligence...
⏱️ This may take 1-2 minutes

⏳ Still processing searchscraper... (15s elapsed)

🤖 Step 3/3: Generating Market Research analysis...

# Company Overview
Stripe is a financial infrastructure platform...

# Founders & Leadership
Founded by Patrick Collison and John Collison...

# Funding & Financials
- Series H: $600M at $95B valuation (2021)
- Total raised: $2.2B
...

[Full analysis continues...]
```

---

## 📚 API Reference

### POST `/assist`

**Description**: Submit a query for market intelligence analysis

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

**Response Events**:
```json
// Progress Update
{
  "type": "text_block",
  "block_id": "DATA_COLLECTION",
  "content": "🕷️ Step 1/3: Crawling company website..."
}

// Keepalive
{
  "type": "text_block",
  "block_id": "SMARTCRAWLER_KEEPALIVE_1",
  "content": "⏳ Still processing smartcrawler... (15s elapsed)"
}

// Final Analysis (Streamed)
{
  "type": "text_stream",
  "stream_id": "FINAL_RESPONSE",
  "chunk": "# Company Overview\nStripe is..."
}

// Completion
{
  "type": "complete"
}
```

**Error Responses**:
```json
// Rate Limit Exceeded
{
  "type": "text_block",
  "block_id": "RATE_LIMIT_ERROR",
  "content": "⚠️ Rate Limit Exceeded\n\nUser rate limit exceeded: 3 requests per minute..."
}


// Timeout
{
  "type": "text_block",
  "block_id": "TIMEOUT_ERROR",
  "content": "⏱️ Operation Timed Out..."
}
```

---

## ⚡ Performance

### Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Average Response Time** | 2-5 minutes | Depends on website size |
| **Cache Hit Response** | < 2 seconds | Instant from Redis |
| **Memory Usage** | ~200MB | Per request |
| **Thread Overhead** | 3 threads | Per request (cleaned up after) |
| **Concurrent Requests** | 50+ | Limited by Redis/API keys |
| **Success Rate** | 95%+ | With retry logic |

### Optimization Tips

1. **Use Caching**: Cached results return instantly (< 2s)
2. **Batch Queries**: Group similar companies to benefit from cache
3. **Rate Limiting**: Respect limits to avoid queueing
4. **Redis Tuning**: Use Redis persistence for production
5. **API Key Quotas**: Monitor ScrapeGraph API usage

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Redis Connection Failed

```
⚠️ Redis not available, caching disabled: Error 111 connecting to localhost:6379
```

**Solution**:
```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis if not running
redis-server

```

#### 2. API Key Invalid

```
❌ Failed to start server: NEBIUS_API_KEY is not set in environment
```

**Solution**:
```bash
# Verify api.env exists and has correct keys
cat api.env

# Ensure keys are not empty
NEBIUS_API_KEY=your_actual_key_here
SMARTCRAWLER_API_KEY=your_actual_key_here
```

#### 3. Crawler Queued for Long Time

```
[SmartCrawler] Status: queued (35s elapsed)
[SmartCrawler] Status: queued (70s elapsed)
```

**Cause**: ScrapeGraph API is experiencing high demand or rate limiting

**Solutions**:
- Wait for queue to clear (usually < 2 minutes)
- Upgrade to paid ScrapeGraph tier for priority
- Try a different time of day
- Check ScrapeGraph status page

#### 4. Thread Count Not Returning to Baseline

```
🧵 Initial: 1 → Peak: 4 → Final: 4 ❌  (Should return to 1)
```

**Cause**: Executor not being cleaned up properly


#### 5. Timeout Errors

```
⏱️ Operation Timed Out
SMARTCRAWLER operation exceeded timeout
```

**Causes**:
- Website is very large (> 5 pages)
- Website is slow to respond
- Website blocks crawlers

**Solutions**:
- Try a smaller/faster website
- Increase timeout in `settings.py`:
  ```python
  CRAWL_TIMEOUT = 600  # 10 minutes
  ```
- Check if website has crawler protection

### Debug Mode

Enable detailed logging:

```python
# In run.py, change logging level:
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Check

```bash
# Check if agent is running
curl http://localhost:8080/health

# Check Redis connection
redis-cli ping

# Check thread count
ps -eLf | grep python | wc -l
```

---

## 📊 Project Structure

```
market-research-agent/
├── app/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── gtm_agent.py          # Main agent logic
│   │   └── handlers.py            # Analysis handlers (research/gtm/channel)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── url_validator.py      # URL normalization & validation
│   │   ├── query_parser.py       # Natural language query parser
│   │   ├── rate_limiter.py       # Redis rate limiting
│   │   └── cache.py               # Redis caching layer
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py         # Nebius AI integration
│   │   ├── smartcrawler.py        # Website crawling service
│   │   └── searchscraper.py       # Competitor search service
│   └── prompts/
│       ├── __init__.py
│       ├── research.py            # Research analysis prompts
│       ├── gtm.py                 # GTM strategy prompts
│       └── channel.py             # Channel strategy prompts
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_parser.py
│   └── test_services.py
├── docs/
│   ├── ARCHITECTURE.md            # Detailed architecture
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── CONTRIBUTING.md            # Contribution guidelines
├── api.env                        # Environment variables (gitignored)
├── api.env.example                # Environment template
├── requirements.txt               # Python dependencies
├── run.py                         # Application entry point
├── README.md                      # This file
└── LICENSE                        # MIT License
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.



### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Sentient Labs](https://sentient.xyz/)** - Agent framework
- **[Nebius AI](https://nebius.ai/)** - LLM provider
- **[ScrapeGraph](https://scrapegraph.io/)** - Web scraping infrastructure
- **[Redis](https://redis.io/)** - Caching and rate limiting

---

## 📧 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Legendandy/Market-research-agent/issues)
- **Email**: LegendAndy07@gmail.com
- **Discord**: Check Sentient's Builder Junior for support. 

---

## 🗺️ Roadmap

### v2.1.0 (Q1 2026)
- [ ] Multi-language support (Spanish, French, German)
- [ ] PDF export for reports
- [ ] Webhook notifications for long-running queries
- [ ] Advanced competitor tracking

### v2.2.0 (Q2 2026)
- [ ] Web dashboard UI
- [ ] Team collaboration features
- [ ] Historical trend analysis
- [ ] Custom prompt templates

### v3.0.0 (Q3 2026)
- [ ] Multi-agent orchestration
- [ ] Real-time market monitoring
- [ ] Integration with CRM systems
- [ ] Enterprise SSO

---

<div align="center">

**Built with ❤️ by the MarketMind AI Team**

[Website](https://marketmind.ai) • [Documentation](docs/) • [Twitter](https://twitter.com/_hadeelen)

</div>
