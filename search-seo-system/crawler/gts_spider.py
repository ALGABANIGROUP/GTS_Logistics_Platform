# Web Crawler for GTS Domains
# Web Crawler for GTS Domains

import scrapy
from scrapy.crawler import CrawlerProcess
from elasticsearch import Elasticsearch
import logging
from urllib.parse import urlparse, urljoin
from datetime import datetime
import json
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GTSSpider(scrapy.Spider):
    """Web spider for crawling GTS and Gabani Logistics domains"""
    
    name = "gts_crawler"
    allowed_domains = ['gtsdispatcher.com', 'gabanilogistics.com']
    
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'GTS-SearchBot/1.0 (+https://gtsdispatcher.com)',
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
        'DEPTH_LIMIT': 3,
        'COOKIES_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504],
        'REDIRECT_ENABLED': True,
        'REDIRECT_MAX_TIMES': 2,
        'TIMEOUT': 30,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize Elasticsearch
        try:
            self.es = Elasticsearch(
                ['http://localhost:9200'],
                request_timeout=30
            )
            # Test connection
            if self.es.ping():
                logger.info("✅ Connected to Elasticsearch")
            else:
                logger.error("❌ Failed to connect to Elasticsearch")
                raise Exception("Elasticsearch connection failed")
        except Exception as e:
            logger.error(f"Elasticsearch initialization error: {e}")
            raise
        
        # Start URLs
        self.start_urls = [
            'https://gtsdispatcher.com',
            'https://gabanilogistics.com',
        ]
        
        # Tracking
        self.crawled_urls = set()
        self.error_urls = []
    
    def parse(self, response):
        """Parse individual pages and extract content"""
        
        url = response.url
        
        # Skip duplicates
        if url in self.crawled_urls:
            return
        
        self.crawled_urls.add(url)
        
        try:
            # Extract page data
            page_data = self._extract_page_data(response)
            
            # Index in Elasticsearch
            self._index_in_elasticsearch(page_data)
            
            logger.info(f"✅ Indexed: {url}")
            
            # Follow internal links
            for href in response.css('a::attr(href)').getall():
                absolute_url = urljoin(response.url, href)
                parsed_url = urlparse(absolute_url)
                
                # Only follow internal links
                if parsed_url.netloc in self.allowed_domains and absolute_url not in self.crawled_urls:
                    # Don't crawl common non-content URLs
                    if not self._should_skip(absolute_url):
                        yield response.follow(absolute_url, self.parse)
        
        except Exception as e:
            logger.error(f"❌ Error parsing {url}: {e}")
            self.error_urls.append({'url': url, 'error': str(e)})
    
    def _extract_page_data(self, response) -> Dict:
        """Extract and structure page data"""
        
        # Extract title
        title = response.css('title::text').get() or ''
        title = title.strip() if title else ''
        
        # Extract meta description
        meta_desc = response.css('meta[name="description"]::attr(content)').get() or ''
        meta_desc = meta_desc.strip() if meta_desc else ''
        
        # Extract headings
        h1_texts = response.css('h1::text').getall()
        h2_texts = response.css('h2::text').getall()
        h3_texts = response.css('h3::text').getall()
        
        # Extract main content
        body_text = ' '.join(response.css('body *::text').getall())
        # Clean up text
        import re
        body_text = re.sub(r'\s+', ' ', body_text).strip()
        content_text = body_text[:15000]  # Limit to 15K chars
        
        # Extract images
        images = response.css('img::attr(src)').getall()
        
        # Count words
        word_count = len(content_text.split())
        
        # Determine content type
        content_type = self._determine_content_type(response.url)
        
        # Determine section
        platform_section = self._determine_section(response.url)
        
        page_data = {
            'url': response.url,
            'title': title,
            'meta_description': meta_desc,
            'h1': [h.strip() for h in h1_texts if h.strip()],
            'h2': [h.strip() for h in h2_texts if h.strip()],
            'h3': [h.strip() for h in h3_texts if h.strip()],
            'content_text': content_text,
            'images': images[:10],  # Limit to 10 images
            'crawled_at': datetime.utcnow().isoformat() + 'Z',
            'content_type': content_type,
            'platform_section': platform_section,
            'language': 'en',
            'word_count': word_count,
            'status_code': response.status,
            'response_time': response.meta.get('download_timeout', 0),
            'internal_links_count': len(response.css('a::attr(href)').getall()),
            'image_count': len(images),
            'has_schema': bool(response.css('script[type="application/ld+json"]::text').get()),
        }
        
        return page_data
    
    def _determine_content_type(self, url: str) -> str:
        """Determine content type based on URL and structure"""
        url_lower = url.lower()
        
        if any(keyword in url_lower for keyword in ['blog', 'article', 'news', 'post']):
            return 'blog'
        elif any(keyword in url_lower for keyword in ['service', 'solution', 'product', 'feature']):
            return 'service'
        elif any(keyword in url_lower for keyword in ['about', 'company', 'team']):
            return 'about'
        elif any(keyword in url_lower for keyword in ['contact', 'support']):
            return 'contact'
        elif any(keyword in url_lower for keyword in ['tms', 'dashboard', 'platform', 'app']):
            return 'platform'
        elif 'pricing' in url_lower:
            return 'pricing'
        elif 'documentation' in url_lower or 'docs' in url_lower:
            return 'documentation'
        else:
            return 'page'
    
    def _determine_section(self, url: str) -> str:
        """Determine which section of the platform"""
        if 'gtsdispatcher.com' in url:
            return 'platform'
        elif 'gabanilogistics.com' in url:
            return 'marketing'
        else:
            return 'other'
    
    def _should_skip(self, url: str) -> bool:
        """Check if URL should be skipped"""
        skip_patterns = [
            '/admin',
            '/login',
            '/register',
            '/private',
            '/api',
            '/callback',
            '/webhook',
            '.pdf',
            '.jpg',
            '.png',
            '.gif',
            '.zip',
            '.exe',
            '#',
        ]
        
        return any(pattern in url.lower() for pattern in skip_patterns)
    
    def _index_in_elasticsearch(self, data: Dict):
        """Index page data in Elasticsearch"""
        try:
            # Create index if needed
            if not self.es.indices.exists(index='gts_content'):
                self._create_elasticsearch_index()
            
            # Generate document ID from URL
            doc_id = data['url'].replace('https://', '').replace('http://', '')
            
            # Index document
            response = self.es.index(
                index='gts_content',
                id=doc_id,
                document=data,
                refresh=True
            )
            
            logger.info(f"Indexed: {data['url']} -> {response['_id']}")
            
        except Exception as e:
            logger.error(f"Error indexing {data['url']}: {e}")
            raise
    
    def _create_elasticsearch_index(self):
        """Create Elasticsearch index with proper mappings"""
        index_settings = {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "index": {
                    "max_result_window": 10000,
                    "refresh_interval": "30s"
                },
                "analysis": {
                    "analyzer": {
                        "gts_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "stemmer"]
                        },
                        "autocomplete_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    },
                    "filter": {
                        "stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "url": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "gts_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "autocomplete": {"type": "text", "analyzer": "autocomplete_analyzer"}
                        }
                    },
                    "meta_description": {
                        "type": "text",
                        "analyzer": "gts_analyzer"
                    },
                    "content_text": {
                        "type": "text",
                        "analyzer": "gts_analyzer"
                    },
                    "h1": {"type": "text", "analyzer": "gts_analyzer"},
                    "h2": {"type": "text", "analyzer": "gts_analyzer"},
                    "h3": {"type": "text", "analyzer": "gts_analyzer"},
                    "content_type": {"type": "keyword"},
                    "platform_section": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "word_count": {"type": "integer"},
                    "status_code": {"type": "integer"},
                    "crawled_at": {"type": "date"},
                    "images": {"type": "keyword"},
                    "internal_links_count": {"type": "integer"},
                    "image_count": {"type": "integer"},
                    "has_schema": {"type": "boolean"},
                    "popularity_score": {
                        "type": "float",
                        "default": 1.0
                    }
                }
            }
        }
        
        try:
            self.es.indices.create(index='gts_content', body=index_settings)
            logger.info("✅ Created Elasticsearch index: gts_content")
        except Exception as e:
            logger.error(f"❌ Error creating index: {e}")
            raise
    
    def closed(self, reason):
        """Called when spider closes"""
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Crawled URLs: {len(self.crawled_urls)}")
        logger.info(f"Error URLs: {len(self.error_urls)}")
        
        # Save error report
        if self.error_urls:
            with open('crawler_errors.json', 'w') as f:
                json.dump(self.error_urls, f, indent=2)


def run_crawler():
    """Run the crawler"""
    process = CrawlerProcess({
        'USER_AGENT': 'GTS-SearchBot/1.0',
        'ROBOTSTXT_OBEY': True,
    })
    
    process.crawl(GTSSpider)
    process.start()


if __name__ == "__main__":
    logger.info("Starting GTS Web Crawler...")
    run_crawler()
