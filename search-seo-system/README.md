# 🔍 GTS Search & SEO System
## Complete Search Engine & SEO Optimization Platform

> An enterprise-grade search and SEO system for GTS Dispatcher and Gabani Logistics

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Documentation](#api-documentation)
8. [Deployment](#deployment)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **GTS Search & SEO System** is a comprehensive platform that combines:

- **Full-text Search Engine** - Elasticsearch-powered internal search for GTS platform
- **Web Crawler** - Scrapy-based crawler for automatic content discovery
- **SEO Optimization** - Technical SEO, structured data, robots.txt, sitemaps
- **Content Analysis** - NLP-based keyword extraction and readability scoring
- **Analytics** - Search metrics, user insights, content performance
- **Monitoring** - Real-time system health and performance tracking

### Target Domains
- **GTS Dispatcher**: https://gtsdispatcher.com
- **Gabani Logistics**: https://gabanilogistics.com

---

## ✨ Features

### Search Capabilities
- ✅ Full-text search with BM25 ranking
- ✅ Auto-complete with prefix matching
- ✅ Multi-field search (title, description, content)
- ✅ Advanced filtering by content type and section
- ✅ Search result highlighting
- ✅ Real-time indexing

### SEO Features
- ✅ Automatic robots.txt generation
- ✅ XML sitemap generation
- ✅ JSON-LD structured data
- ✅ Meta tag optimization
- ✅ Schema.org markup detection
- ✅ SEO health audits
- ✅ Content optimization recommendations

### Content Analysis
- ✅ Keyword extraction (TF-based)
- ✅ Key phrase identification
- ✅ Readability scoring (Flesch-Kincaid, SMOG)
- ✅ Content structure analysis
- ✅ Optimization recommendations
- ✅ Content gap detection

### Web Crawler
- ✅ Multi-domain crawling
- ✅ Automatic content type detection
- ✅ Robots.txt compliance
- ✅ Error handling and retry logic
- ✅ URL deduplication
- ✅ Direct Elasticsearch indexing

### Analytics
- ✅ Search query analytics
- ✅ Content performance metrics
- ✅ User behavior tracking
- ✅ Search success rates
- ✅ Content gap analysis

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│              SearchInterface.jsx Component                  │
└────────────┬────────────────────────────────────────────────┘
             │
             │ HTTP/REST API
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│     ├─ /api/search (Full-text search)                      │
│     ├─ /api/autocomplete (Suggestions)                     │
│     ├─ /api/stats (Index statistics)                       │
│     ├─ /health (Health check)                              │
│     ├─ /robots.txt (SEO)                                   │
│     └─ /sitemap.xml (SEO)                                  │
└────────┬──────────────────────┬─────────────────────────────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────────┐  ┌──────────────────┐
│  Elasticsearch 8.x  │  │    Redis Cache   │
│  ├─ gts_content     │  │  Query Cache     │
│  ├─ gts_search_logs │  │  Session Store   │
│  └─ seo_reports     │  │  Rate Limiting   │
└─────────────────────┘  └──────────────────┘
         ▲
         │
         │ Index
         │
┌─────────────────────────────────────────────────────────────┐
│              Scrapy Web Crawler                             │
│     ├─ GTSSpider (Multi-domain)                            │
│     ├─ Content Type Detection                              │
│     ├─ Metadata Extraction                                 │
│     └─ Error Handling                                      │
└─────────────────────────────────────────────────────────────┘

Optimization Layer:
┌─────────────────────────────────────────────────────────────┐
│  SEO Manager       │  Content Optimizer  │  Analytics Engine │
│  ├─ robots.txt     │  ├─ Keywords        │  ├─ Query Logs    │
│  ├─ Sitemaps       │  ├─ Readability     │  ├─ Metrics       │
│  ├─ Structured Data│  ├─ Structure       │  └─ Reports       │
│  └─ Meta Tags      │  └─ Recommendations │                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.10+ (for local development)
- Elasticsearch 8.x
- Node.js 18+ (for frontend)

### Option 1: Docker Compose (Recommended)

```bash
# Clone or navigate to repository
cd d:\GTS\search-seo-system

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check Elasticsearch health
curl http://localhost:9200/_cluster/health

# Check API health
curl http://localhost:8000/health
```

**Services will be available at:**
- API: http://localhost:8000
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Redis: localhost:6379

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Elasticsearch (Docker)
docker run -d -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# Start FastAPI backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in root directory:

```bash
# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Redis
REDIS_URL=redis://localhost:6379/0

# Database (Optional)
DATABASE_URL=postgresql://user:password@localhost/gts_search

# API Settings
API_TITLE=GTS Search API
API_VERSION=1.0.0
LOG_LEVEL=info
ENV=production

# Crawler Settings
CRAWL_DEPTH=3
CONCURRENT_REQUESTS=2
CRAWL_DELAY=2

# Feature Flags
ENABLE_CRAWLER=true
ENABLE_ANALYTICS=true
ENABLE_SEO=true
ENABLE_CONTENT_OPTIMIZATION=true

# Domains to crawl
DOMAINS=gtsdispatcher.com,gabanilogistics.com

# API Keys
OPENAI_API_KEY=sk-...  # Optional, for advanced NLP
```

### Elasticsearch Index Configuration

Indices are automatically created on first run:

- **gts_content** - Main content index
  - Contains all crawled pages
  - Custom analyzers for English/Arabic
  - Optimized for full-text search
  
- **gts_search_logs** - Search query logs
  - Tracks all search queries
  - Used for analytics
  
- **seo_reports** - SEO analysis reports
  - Stores audit results
  - Performance metrics

---

## 🚀 Usage

### 1. Web Crawler

```python
from crawler.gts_spider import GTSSpider
from scrapy.crawler import CrawlerProcess

# Configure and run crawler
process = CrawlerProcess({
    'USER_AGENT': 'GTS-Bot/1.0',
    'ROBOTSTXT_OBEY': True,
    'CONCURRENT_REQUESTS': 2,
})

process.crawl(GTSSpider)
process.start()
```

### 2. Search API

```bash
# Basic search
curl "http://localhost:8000/api/search?q=freight+management"

# Search with filters
curl "http://localhost:8000/api/search?q=logistics&content_type=service&section=platform"

# Autocomplete
curl "http://localhost:8000/api/autocomplete?prefix=log"

# Get statistics
curl "http://localhost:8000/api/stats"

# Health check
curl "http://localhost:8000/health"
```

### 3. React Frontend

```javascript
import SearchInterface from './SearchInterface.jsx';

export default function App() {
  return <SearchInterface />;
}
```

### 4. SEO Optimization

```python
from seo.technical_setup import SEOManager

manager = SEOManager({
    'dispatcher': 'https://gtsdispatcher.com',
    'gabani': 'https://gabanilogistics.com'
})

# Generate and save robots.txt
manager.save_robots_txt()

# Generate sitemaps
sitemaps = manager.generate_sitemaps_from_es()
manager.save_sitemaps(sitemaps)

# Generate SEO report
report = manager.generate_seo_report()
```

### 5. Content Analysis

```python
from seo.content_optimizer import ContentOptimizer

optimizer = ContentOptimizer()

page = {
    'url': 'https://example.com/blog/post',
    'title': 'Your Page Title',
    'content_text': 'Your page content...',
    'h1': ['Heading 1'],
    'word_count': 2000
}

# Analyze content
analysis = optimizer.analyze_complete_content(page)
print(analysis['keywords'])
print(analysis['readability'])
print(analysis['recommendations'])
```

---

## 📚 API Documentation

### Search Endpoints

#### POST /api/search
Full-text search with advanced filtering

**Query Parameters:**
- `q` (required): Search query
- `content_type` (optional): Filter by type (blog, service, documentation, page, platform)
- `section` (optional): Filter by section (platform, marketing)
- `page` (optional): Page number (default: 1)
- `size` (optional): Results per page (default: 10, max: 50)

**Response:**
```json
{
  "success": true,
  "query": "freight management",
  "total": 45,
  "page": 1,
  "total_pages": 5,
  "results": [
    {
      "url": "https://...",
      "title": "...",
      "score": 8.5,
      "highlight": {...}
    }
  ],
  "took_ms": 123
}
```

#### GET /api/autocomplete
Get autocomplete suggestions

**Query Parameters:**
- `prefix` (required): Search prefix (min 1 char)

**Response:**
```json
{
  "success": true,
  "prefix": "log",
  "suggestions": [
    {
      "text": "Logistics Management",
      "url": "https://...",
      "type": "service"
    }
  ],
  "count": 3
}
```

#### GET /api/stats
Get search index statistics

**Response:**
```json
{
  "success": true,
  "total_documents": 1234,
  "content_distribution": {
    "blog": 456,
    "service": 234,
    "documentation": 345
  },
  "avg_word_count": 1250
}
```

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "elasticsearch": "connected",
  "index_exists": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### SEO Endpoints

#### GET /robots.txt
Serve robots.txt file

#### GET /sitemap.xml
Serve XML sitemap

---

## 🐳 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f search-api

# Stop services
docker-compose down
```

### Production Deployment

For production, update Docker Compose:

```yaml
# Use environment-specific overrides
services:
  elasticsearch:
    environment:
      - xpack.security.enabled=true
      - xpack.security.authc.api_key.enabled=true
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Kubernetes Deployment

Example Kubernetes manifests available in `/deployment/k8s/`

```bash
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/elasticsearch.yaml
kubectl apply -f deployment/k8s/search-api.yaml
```

---

## 📊 Monitoring

### Elasticsearch Monitoring

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# Monitor indices
curl http://localhost:9200/_cat/indices?v

# Check index stats
curl http://localhost:9200/gts_content/_stats
```

### API Monitoring

```bash
# Check API health
curl http://localhost:8000/health

# View search logs
curl http://localhost:8000/api/logs?limit=100

# Get performance metrics
curl http://localhost:8000/api/metrics
```

### Kibana Dashboards

Access Kibana at http://localhost:5601 to:
- Monitor Elasticsearch
- View search query logs
- Create custom dashboards
- Set up alerts

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Elasticsearch Connection Failed

```bash
# Check if Elasticsearch is running
docker ps | grep elasticsearch

# Check Elasticsearch logs
docker logs gts-elasticsearch

# Verify connectivity
curl http://localhost:9200
```

#### 2. Search Returns No Results

```bash
# Check if index exists
curl http://localhost:9200/_cat/indices

# Check document count
curl http://localhost:9200/gts_content/_count

# Re-index from crawler
python -m crawler.gts_spider
```

#### 3. API Timeout Issues

```bash
# Check API logs
docker logs gts-search-api

# Monitor Elasticsearch performance
curl http://localhost:9200/_nodes/stats

# Increase timeout in .env
ELASTICSEARCH_TIMEOUT=60
```

#### 4. Memory Issues

```bash
# Increase Elasticsearch memory
docker-compose down
# Edit docker-compose.yml: ES_JAVA_OPTS=-Xms2g -Xmx2g
docker-compose up -d
```

---

## 📈 Performance Optimization

### Elasticsearch Tuning

```bash
# Adjust refresh interval
curl -X PUT http://localhost:9200/gts_content/_settings -d '{
  "index": {
    "refresh_interval": "60s"
  }
}'

# Enable compression
curl -X PUT http://localhost:9200/gts_content/_settings -d '{
  "index": {
    "codec": "best_compression"
  }
}'
```

### API Optimization

```python
# Enable query caching via Redis
from redis import Redis
redis_client = Redis(host='localhost', port=6379)

# Cache search results
cache_key = f"search:{query}:{page}"
```

---

## 📝 Logging

Logs are stored in `/logs/` directory:

- `api.log` - FastAPI logs
- `crawler.log` - Web crawler logs
- `elasticsearch.log` - ES operations
- `seo.log` - SEO optimization logs

View logs:

```bash
# API logs
tail -f logs/api.log

# All logs
tail -f logs/*.log | grep ERROR
```

---

## 🤝 Integration with GTS Platform

### Add to Existing GTS Installation

```python
# In backend/main.py
from search_seo_system.api import search_router

app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
```

### Frontend Integration

```jsx
// In frontend/src/App.jsx
import SearchInterface from '../search-seo-system/frontend/SearchInterface.jsx';

// Add search route
<Route path="/search" element={<SearchInterface />} />
```

---

## 📄 License

GTS Logistics Search & SEO System © 2024

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in `/logs/`
3. Contact: support@gtsdispatcher.com

---

## 📚 Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [React Documentation](https://react.dev/)

---

**Last Updated:** January 2024  
**Status:** Production Ready
