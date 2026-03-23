# FastAPI Search Engine
# FastAPI Search Engine

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GTS Search & SEO API",
    description="Complete search engine and SEO system for GTS Dispatcher and Gabani Logistics",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Elasticsearch
try:
    es = Elasticsearch(
        ['http://localhost:9200'],
        request_timeout=30
    )
    if es.ping():
        logger.info("✅ Connected to Elasticsearch")
    else:
        raise Exception("Elasticsearch connection failed")
except Exception as e:
    logger.error(f"❌ Elasticsearch initialization error: {e}")
    es = None


# ============================================
# SEARCH ENDPOINTS
# ============================================

@app.get("/api/search")
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    content_type: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50)
):
    """
    Search endpoint with filtering and pagination
    """
    if not es or not es.ping():
        raise HTTPException(status_code=503, detail="Search engine is unavailable")
    
    try:
        # Build search query
        search_body = _build_search_query(q, content_type, section, page, size)
        
        # Execute search
        results = es.search(index="gts_content", body=search_body)
        
        # Process results
        processed_results = _process_search_results(results, page, size)
        
        # Log search for analytics
        _log_search(q, processed_results['total'])
        
        return {
            "success": True,
            "query": q,
            "timestamp": datetime.utcnow().isoformat(),
            **processed_results
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/autocomplete")
async def autocomplete(
    prefix: str = Query(..., min_length=1, max_length=50)
):
    """
    Autocomplete suggestions endpoint
    """
    if not es or not es.ping():
        raise HTTPException(status_code=503, detail="Search engine is unavailable")
    
    try:
        # Build autocomplete query
        search_body = {
            "query": {
                "match_phrase_prefix": {
                    "title": {
                        "query": prefix,
                        "boost": 2
                    }
                }
            },
            "size": 5,
            "_source": ["title", "url"]
        }
        
        results = es.search(index="gts_content", body=search_body)
        
        suggestions = []
        for hit in results['hits']['hits']:
            suggestions.append({
                "text": hit['_source']['title'],
                "url": hit['_source']['url']
            })
        
        return {
            "success": True,
            "prefix": prefix,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        return {
            "success": False,
            "suggestions": [],
            "error": str(e)
        }


# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@app.get("/api/stats")
async def get_stats():
    """
    Get search statistics and index metrics
    """
    if not es or not es.ping():
        raise HTTPException(status_code=503, detail="Search engine is unavailable")
    
    try:
        # Total documents
        count_response = es.count(index="gts_content")
        total_docs = count_response['count']
        
        # Content type distribution
        aggs_response = es.search(
            index="gts_content",
            body={
                "size": 0,
                "aggs": {
                    "content_types": {
                        "terms": {"field": "content_type", "size": 20}
                    },
                    "sections": {
                        "terms": {"field": "platform_section"}
                    },
                    "avg_word_count": {
                        "avg": {"field": "word_count"}
                    }
                }
            }
        )
        
        content_dist = {}
        for bucket in aggs_response['aggregations']['content_types']['buckets']:
            content_dist[bucket['key']] = bucket['doc_count']
        
        sections_dist = {}
        for bucket in aggs_response['aggregations']['sections']['buckets']:
            sections_dist[bucket['key']] = bucket['doc_count']
        
        return {
            "success": True,
            "total_documents": total_docs,
            "content_distribution": content_dist,
            "sections_distribution": sections_dist,
            "avg_word_count": round(aggs_response['aggregations']['avg_word_count']['value'], 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH & MONITORING
# ============================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        es_health = es.ping() if es else False
        index_exists = es.indices.exists(index="gts_content") if es else False
        
        return {
            "status": "healthy" if es_health and index_exists else "degraded",
            "elasticsearch": "connected" if es_health else "disconnected",
            "index_exists": index_exists,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/")
async def root():
    """
    API root endpoint
    """
    return {
        "service": "GTS Search & SEO API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "search": "/api/search?q=your+query",
            "autocomplete": "/api/autocomplete?prefix=log",
            "stats": "/api/stats",
            "health": "/health",
            "docs": "/docs"
        },
        "documentation": "/docs"
    }


# ============================================
# SEO ENDPOINTS
# ============================================

@app.get("/robots.txt")
async def get_robots_txt():
    """
    Serve robots.txt file
    """
    robots_path = "static/seo/robots.txt"
    if os.path.exists(robots_path):
        return FileResponse(robots_path, media_type="text/plain")
    
    # Generate on-the-fly if doesn't exist
    robots_content = """# GTS Search & SEO System
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/
Disallow: /api/v*/
Disallow: /internal/

# Sitemaps
Sitemap: https://gtsdispatcher.com/sitemap.xml
Sitemap: https://gabanilogistics.com/sitemap.xml

# Crawl delay
Crawl-delay: 2
Request-rate: 1/2s
"""
    
    return robots_content


@app.get("/sitemap.xml")
async def get_sitemap():
    """
    Generate and serve sitemap
    """
    sitemap_path = "static/seo/sitemap.xml"
    if os.path.exists(sitemap_path):
        return FileResponse(sitemap_path, media_type="application/xml")
    
    raise HTTPException(status_code=404, detail="Sitemap not found")


# ============================================
# HELPER FUNCTIONS
# ============================================

def _build_search_query(query: str, content_type: Optional[str], 
                        section: Optional[str], page: int, size: int) -> Dict:
    """Build Elasticsearch query with ranking"""
    
    search_body = {
        "from": (page - 1) * size,
        "size": size,
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        "title^3",
                                        "h1^2.5",
                                        "meta_description^2",
                                        "content_text"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "operator": "OR"
                                }
                            }
                        ],
                        "filter": []
                    }
                },
                "functions": [
                    # Boost service and platform content
                    {
                        "filter": {"term": {"content_type": "service"}},
                        "weight": 1.5
                    },
                    {
                        "filter": {"term": {"content_type": "platform"}},
                        "weight": 2.0
                    },
                    # Boost platform section
                    {
                        "filter": {"term": {"platform_section": "platform"}},
                        "weight": 1.3
                    },
                    # Boost by word count (prefer comprehensive content)
                    {
                        "field_value_factor": {
                            "field": "word_count",
                            "factor": 0.0001,
                            "missing": 100
                        }
                    },
                    # Boost recent content
                    {
                        "exp": {
                            "crawled_at": {
                                "origin": "now",
                                "scale": "30d",
                                "decay": 0.3
                            }
                        },
                        "weight": 1.1
                    }
                ],
                "score_mode": "sum",
                "boost_mode": "multiply"
            }
        },
        "highlight": {
            "fields": {
                "title": {"number_of_fragments": 0},
                "content_text": {
                    "fragment_size": 150,
                    "number_of_fragments": 3,
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"]
                },
                "meta_description": {"number_of_fragments": 0}
            },
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"]
        },
        "aggs": {
            "content_types": {
                "terms": {"field": "content_type", "size": 10}
            },
            "sections": {
                "terms": {"field": "platform_section"}
            }
        }
    }
    
    # Add filters if specified
    if content_type:
        search_body["query"]["function_score"]["query"]["bool"]["filter"].append(
            {"term": {"content_type": content_type}}
        )
    
    if section:
        search_body["query"]["function_score"]["query"]["bool"]["filter"].append(
            {"term": {"platform_section": section}}
        )
    
    return search_body


def _process_search_results(results: Dict, page: int, size: int) -> Dict:
    """Process Elasticsearch results"""
    
    processed_results = {
        "total": results["hits"]["total"]["value"],
        "page": page,
        "page_size": size,
        "total_pages": (results["hits"]["total"]["value"] + size - 1) // size,
        "results": [],
        "aggregations": results.get("aggregations", {}),
        "took_ms": results.get("took", 0)
    }
    
    for hit in results["hits"]["hits"]:
        result = hit["_source"].copy()
        result["score"] = hit["_score"]
        result["highlight"] = hit.get("highlight", {})
        
        # Add ranking info
        result["rank"] = (page - 1) * size + len(processed_results["results"]) + 1
        
        processed_results["results"].append(result)
    
    return processed_results


def _log_search(query: str, result_count: int):
    """Log search query for analytics"""
    try:
        log_doc = {
            "query": query,
            "result_count": result_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results_returned": min(result_count, 10)
        }
        
        # Create search logs index if needed
        if not es.indices.exists(index="gts_search_logs"):
            es.indices.create(
                index="gts_search_logs",
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    },
                    "mappings": {
                        "properties": {
                            "query": {"type": "keyword"},
                            "result_count": {"type": "integer"},
                            "timestamp": {"type": "date"},
                            "results_returned": {"type": "integer"}
                        }
                    }
                }
            )
        
        es.index(index="gts_search_logs", document=log_doc)
        logger.debug(f"Logged search: {query} -> {result_count} results")
        
    except Exception as e:
        logger.warning(f"Failed to log search: {e}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
