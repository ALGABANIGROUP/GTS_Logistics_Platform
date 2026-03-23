# Elasticsearch Setup & Configuration
# Elasticsearch Setup & Configuration

import logging
from typing import Optional, Dict, List
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GTSSearchEngine:
    """Manages Elasticsearch setup and search operations for GTS"""
    
    def __init__(self, host: str = "localhost", port: int = 9200):
        """
        Initialize Elasticsearch connection
        
        Args:
            host: Elasticsearch host
            port: Elasticsearch port
        """
        self.host = host
        self.port = port
        self.client = None
        self.connect()
    
    def connect(self):
        """Establish connection to Elasticsearch"""
        try:
            self.client = Elasticsearch([{'host': self.host, 'port': self.port}])
            if self.client.ping():
                logger.info(f"✅ Connected to Elasticsearch at {self.host}:{self.port}")
                return True
            else:
                logger.error("❌ Failed to connect to Elasticsearch")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def create_index(self):
        """Create gts_content index with optimized settings and mappings"""
        
        index_name = "gts_content"
        
        # Check if index exists
        if self.client.indices.exists(index=index_name):
            logger.info(f"Index '{index_name}' already exists")
            return True
        
        # Index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "refresh_interval": "30s",
                "analysis": {
                    "analyzer": {
                        "english_analyzer": {
                            "type": "standard",
                            "stopwords": "_english_"
                        },
                        "arabic_analyzer": {
                            "type": "standard",
                            "stopwords": "_arabic_"
                        },
                        "text_analyzer": {
                            "type": "standard",
                            "stopwords": ["the", "a", "an", "and", "or", "but", "in", "on", "at"]
                        },
                        "autocomplete_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "length"]
                        }
                    },
                    "normalizer": {
                        "lowercase_normalizer": {
                            "type": "custom",
                            "filter": ["lowercase"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    # Main content fields
                    "url": {
                        "type": "keyword",
                        "index": True
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "english_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete_analyzer"
                            }
                        }
                    },
                    "meta_description": {
                        "type": "text",
                        "analyzer": "english_analyzer"
                    },
                    "content_text": {
                        "type": "text",
                        "analyzer": "english_analyzer",
                        "term_vector": "with_positions_offsets"
                    },
                    
                    # Headings
                    "h1": {
                        "type": "text",
                        "analyzer": "english_analyzer",
                        "fields": {"keyword": {"type": "keyword"}}
                    },
                    "h2": {
                        "type": "text",
                        "analyzer": "english_analyzer"
                    },
                    "h3": {
                        "type": "text",
                        "analyzer": "english_analyzer"
                    },
                    
                    # Categorization
                    "content_type": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer"
                    },
                    "platform_section": {
                        "type": "keyword",
                        "normalizer": "lowercase_normalizer"
                    },
                    "domain": {
                        "type": "keyword"
                    },
                    "language": {
                        "type": "keyword"
                    },
                    
                    # SEO fields
                    "keywords": {
                        "type": "text",
                        "analyzer": "english_analyzer"
                    },
                    "schema_org_detected": {
                        "type": "boolean"
                    },
                    "robots_noindex": {
                        "type": "boolean"
                    },
                    
                    # Statistics
                    "word_count": {
                        "type": "integer"
                    },
                    "character_count": {
                        "type": "integer"
                    },
                    "internal_links": {
                        "type": "integer"
                    },
                    "external_links": {
                        "type": "integer"
                    },
                    "image_count": {
                        "type": "integer"
                    },
                    
                    # Crawl data
                    "crawled_at": {
                        "type": "date"
                    },
                    "crawl_depth": {
                        "type": "integer"
                    },
                    "http_status": {
                        "type": "integer"
                    },
                    
                    # Performance
                    "response_time_ms": {
                        "type": "integer"
                    },
                    "page_size_bytes": {
                        "type": "integer"
                    },
                    
                    # Media
                    "images": {
                        "type": "keyword"
                    },
                    "videos": {
                        "type": "keyword"
                    },
                    
                    # Metadata
                    "author": {
                        "type": "keyword"
                    },
                    "published_date": {
                        "type": "date"
                    },
                    "updated_date": {
                        "type": "date"
                    },
                    "canonical_url": {
                        "type": "keyword"
                    }
                }
            }
        }
        
        try:
            self.client.indices.create(index=index_name, body=settings)
            logger.info(f"✅ Index '{index_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating index: {e}")
            return False
    
    def index_document(self, doc_id: str, document: Dict) -> bool:
        """Index a single document"""
        
        try:
            self.client.index(index="gts_content", id=doc_id, document=document)
            return True
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {e}")
            return False
    
    def bulk_index(self, documents: List[Dict]) -> Dict:
        """Bulk index multiple documents"""
        
        actions = []
        for doc in documents:
            action = {
                "_index": "gts_content",
                "_id": doc.get('url', ''),
                "_source": doc
            }
            actions.append(action)
        
        try:
            success, errors = bulk(self.client, actions, raise_on_error=False)
            logger.info(f"✅ Indexed {success} documents, {len(errors)} errors")
            return {"success": success, "errors": errors}
        except Exception as e:
            logger.error(f"❌ Bulk indexing error: {e}")
            return {"success": 0, "errors": [str(e)]}
    
    def search(self, query: str, filters: Dict = None, page: int = 1, size: int = 10) -> Dict:
        """
        Perform full-text search with filtering
        
        Args:
            query: Search query string
            filters: Optional filters (content_type, section, etc.)
            page: Page number (1-indexed)
            size: Results per page
        
        Returns:
            Search results dictionary
        """
        
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
                                        "prefix_length": 2
                                    }
                                }
                            ],
                            "filter": []
                        }
                    },
                    "functions": [
                        # Boost service pages
                        {"filter": {"term": {"content_type": "service"}}, "weight": 1.5},
                        # Boost platform content
                        {"filter": {"term": {"platform_section": "platform"}}, "weight": 1.3},
                        # Boost by word count (prefer comprehensive content)
                        {
                            "field_value_factor": {
                                "field": "word_count",
                                "factor": 0.0001,
                                "missing": 100
                            }
                        },
                        # Boost recent content with exponential decay
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
                    }
                }
            }
        }
        
        # Add filters if provided
        if filters:
            if filters.get('content_type'):
                search_body["query"]["function_score"]["query"]["bool"]["filter"].append(
                    {"term": {"content_type": filters['content_type']}}
                )
            if filters.get('platform_section'):
                search_body["query"]["function_score"]["query"]["bool"]["filter"].append(
                    {"term": {"platform_section": filters['platform_section']}}
                )
            if filters.get('domain'):
                search_body["query"]["function_score"]["query"]["bool"]["filter"].append(
                    {"term": {"domain": filters['domain']}}
                )
        
        try:
            results = self.client.search(index="gts_content", body=search_body)
            return {
                "success": True,
                "total": results["hits"]["total"]["value"],
                "results": results["hits"]["hits"],
                "took_ms": results.get("took", 0)
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"success": False, "error": str(e), "results": []}
    
    def autocomplete(self, prefix: str, field: str = "title", limit: int = 5) -> List[Dict]:
        """Get autocomplete suggestions"""
        
        search_body = {
            "query": {
                "match_phrase_prefix": {
                    field: {
                        "query": prefix,
                        "boost": 2
                    }
                }
            },
            "size": limit,
            "_source": ["title", "url", "content_type"]
        }
        
        try:
            results = self.client.search(index="gts_content", body=search_body)
            suggestions = []
            
            for hit in results["hits"]["hits"]:
                suggestions.append({
                    "text": hit["_source"].get("title", ""),
                    "url": hit["_source"].get("url", ""),
                    "type": hit["_source"].get("content_type", "")
                })
            
            return suggestions
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get search index statistics"""
        
        try:
            # Total documents
            count = self.client.count(index="gts_content")
            total_docs = count["count"]
            
            # Aggregations
            agg_body = {
                "aggs": {
                    "content_types": {"terms": {"field": "content_type", "size": 20}},
                    "sections": {"terms": {"field": "platform_section"}},
                    "domains": {"terms": {"field": "domain"}},
                    "avg_word_count": {"avg": {"field": "word_count"}},
                    "latest_crawl": {"max": {"field": "crawled_at"}}
                }
            }
            
            results = self.client.search(index="gts_content", body=agg_body, size=0)
            aggs = results["aggregations"]
            
            stats = {
                "total_documents": total_docs,
                "content_distribution": {
                    bucket["key"]: bucket["doc_count"] 
                    for bucket in aggs.get("content_types", {}).get("buckets", [])
                },
                "section_distribution": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("sections", {}).get("buckets", [])
                },
                "domain_distribution": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in aggs.get("domains", {}).get("buckets", [])
                },
                "average_word_count": round(
                    aggs.get("avg_word_count", {}).get("value", 0), 2
                ),
                "latest_crawl": aggs.get("latest_crawl", {}).get("value_as_string", "")
            }
            
            return stats
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}
    
    def delete_index(self):
        """Delete the gts_content index (for cleanup/reset)"""
        
        try:
            if self.client.indices.exists(index="gts_content"):
                self.client.indices.delete(index="gts_content")
                logger.info("✅ Index deleted")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False
    
    def health_check(self) -> Dict:
        """Check Elasticsearch health"""
        
        try:
            if not self.client or not self.client.ping():
                return {"status": "disconnected"}
            
            health = self.client.cluster.health()
            index_exists = self.client.indices.exists(index="gts_content")
            
            return {
                "status": "healthy",
                "cluster_status": health.get("status"),
                "index_exists": index_exists,
                "active_shards": health.get("active_shards")
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Initialize search engine
    engine = GTSSearchEngine()
    
    # Create index
    engine.create_index()
    
    # Sample documents
    sample_docs = [
        {
            "url": "https://gtsdispatcher.com/about",
            "title": "About GTS Dispatcher",
            "meta_description": "Learn about GTS Dispatcher, our mission and values",
            "content_text": "GTS Dispatcher is an AI-powered freight management platform...",
            "h1": ["About GTS Dispatcher"],
            "content_type": "page",
            "platform_section": "platform",
            "domain": "gtsdispatcher.com",
            "word_count": 500,
            "crawled_at": "2024-01-15T10:30:00Z"
        },
        {
            "url": "https://gabanilogistics.com/services/warehousing",
            "title": "Warehousing Services",
            "meta_description": "Professional warehousing solutions for freight logistics",
            "content_text": "Our warehousing services provide secure storage and management...",
            "h1": ["Warehousing Services"],
            "content_type": "service",
            "platform_section": "marketing",
            "domain": "gabanilogistics.com",
            "word_count": 800,
            "crawled_at": "2024-01-15T10:30:00Z"
        }
    ]
    
    # Bulk index documents
    engine.bulk_index(sample_docs)
    
    # Search
    results = engine.search("freight management")
    print("Search Results:", json.dumps(results, indent=2))
    
    # Get stats
    stats = engine.get_stats()
    print("Stats:", json.dumps(stats, indent=2))
    
    # Health check
    health = engine.health_check()
    print("Health:", json.dumps(health, indent=2))
