# SEO Optimization System
# SEO Optimization System

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
from xml.etree import ElementTree as ET
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOManager:
    """Manages SEO optimization for GTS properties"""
    
    def __init__(self, base_urls: Dict[str, str], es_client: Optional[Elasticsearch] = None):
        """
        Initialize SEO Manager
        
        Args:
            base_urls: Dictionary with keys 'dispatcher' and 'gabani' containing base URLs
            es_client: Optional Elasticsearch client for content retrieval
        """
        self.base_urls = base_urls
        self.es = es_client or self._init_es()
        self.site_name = "GTS Logistics"
        self.company_name = "GTS Dispatcher & Gabani Logistics"
        
    def _init_es(self):
        """Initialize Elasticsearch connection"""
        try:
            client = Elasticsearch(['http://localhost:9200'])
            if client.ping():
                logger.info("✅ Elasticsearch connected for SEO Manager")
            return client
        except Exception as e:
            logger.error(f"Elasticsearch initialization failed: {e}")
            return None
    
    # ================================
    # ROBOTS.TXT GENERATION
    # ================================
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt file with optimization rules"""
        
        robots_content = f"""# GTS Logistics - Robots.txt
# Generated on {datetime.utcnow().isoformat()}
# This file tells search engines how to crawl our sites

# Allow all bots by default
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /private/
Disallow: /api/v*/
Disallow: /internal/
Disallow: /.git/
Disallow: /.env*
Disallow: /node_modules/
Disallow: /venv/
Disallow: /*?*sort=
Disallow: /*?*filter=
Disallow: /search?
Disallow: /tmp/

# Specific rules for different bots
User-agent: Googlebot
Allow: /
Crawl-delay: 1
Request-rate: 1/1s

User-agent: Bingbot
Allow: /
Crawl-delay: 2
Request-rate: 1/2s

User-agent: Slurp
Allow: /
Crawl-delay: 1

# Disallow bad bots
User-agent: MJ12bot
Disallow: /

User-agent: AhrefsBot
Disallow: /

# Sitemaps
Sitemap: {self.base_urls.get('dispatcher', 'https://gtsdispatcher.com')}/sitemap.xml
Sitemap: {self.base_urls.get('dispatcher', 'https://gtsdispatcher.com')}/sitemap-pages.xml
Sitemap: {self.base_urls.get('dispatcher', 'https://gtsdispatcher.com')}/sitemap-blog.xml

Sitemap: {self.base_urls.get('gabani', 'https://gabanilogistics.com')}/sitemap.xml

# Crawl rate
Crawl-delay: 1.5
Request-rate: 1/1.5s
Visit-time: 0600-2300
Comment: GTS Logistics is a freight management platform
Comment: Optimal crawl time: Off-peak hours
"""
        return robots_content
    
    def save_robots_txt(self, output_dir: str = "static/seo"):
        """Save robots.txt to file"""
        os.makedirs(output_dir, exist_ok=True)
        
        robots_path = os.path.join(output_dir, "robots.txt")
        with open(robots_path, 'w') as f:
            f.write(self.generate_robots_txt())
        
        logger.info(f"✅ Robots.txt saved to {robots_path}")
        return robots_path
    
    # ================================
    # SITEMAP GENERATION
    # ================================
    
    def generate_sitemap(self, pages: List[Dict]) -> str:
        """Generate XML sitemap from crawled pages"""
        
        root = ET.Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        root.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        
        for page in pages:
            url_elem = ET.SubElement(root, 'url')
            
            # Location
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = page['url']
            
            # Last modified
            if 'crawled_at' in page:
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = page['crawled_at'].split('T')[0]  # YYYY-MM-DD format
            
            # Change frequency based on content type
            changefreq = ET.SubElement(url_elem, 'changefreq')
            if page.get('content_type') == 'blog':
                changefreq.text = 'weekly'
            elif page.get('content_type') == 'documentation':
                changefreq.text = 'monthly'
            else:
                changefreq.text = 'weekly'
            
            # Priority based on content type and section
            priority = ET.SubElement(url_elem, 'priority')
            priority_value = 0.5
            
            if page.get('platform_section') == 'platform':
                priority_value = 0.9
            elif page.get('content_type') == 'service':
                priority_value = 0.8
            elif page.get('content_type') == 'blog':
                priority_value = 0.6
            
            priority.text = str(priority_value)
            
            # Images if available
            if page.get('images'):
                for image_url in page['images'][:5]:  # Max 5 images per page
                    image_elem = ET.SubElement(url_elem, 'image:image')
                    img_loc = ET.SubElement(image_elem, 'image:loc')
                    img_loc.text = image_url
        
        return ET.tostring(root, encoding='unicode')
    
    def generate_sitemaps_from_es(self) -> Dict[str, str]:
        """Generate sitemaps from Elasticsearch data"""
        
        if not self.es:
            logger.error("Elasticsearch not available for sitemap generation")
            return {}
        
        try:
            # Fetch all pages from ES
            response = self.es.search(
                index="gts_content",
                body={
                    "size": 50000,
                    "query": {"match_all": {}},
                    "_source": ["url", "title", "content_type", "platform_section", "crawled_at", "images"]
                }
            )
            
            pages = [hit['_source'] for hit in response['hits']['hits']]
            
            # Generate main sitemap
            main_sitemap = self.generate_sitemap(pages)
            
            # Generate category-specific sitemaps
            sitemaps = {
                'main': main_sitemap
            }
            
            # Blog sitemap
            blog_pages = [p for p in pages if p.get('content_type') == 'blog']
            if blog_pages:
                sitemaps['blog'] = self.generate_sitemap(blog_pages)
            
            # Service sitemap
            service_pages = [p for p in pages if p.get('content_type') == 'service']
            if service_pages:
                sitemaps['services'] = self.generate_sitemap(service_pages)
            
            # Platform sitemap
            platform_pages = [p for p in pages if p.get('platform_section') == 'platform']
            if platform_pages:
                sitemaps['platform'] = self.generate_sitemap(platform_pages)
            
            logger.info(f"✅ Generated {len(sitemaps)} sitemaps with {len(pages)} pages")
            return sitemaps
            
        except Exception as e:
            logger.error(f"Sitemap generation error: {e}")
            return {}
    
    def save_sitemaps(self, sitemaps: Dict[str, str], output_dir: str = "static/seo"):
        """Save sitemaps to files"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main sitemap
        with open(os.path.join(output_dir, "sitemap.xml"), 'w') as f:
            f.write(sitemaps.get('main', ''))
        
        # Save category sitemaps
        for name, content in sitemaps.items():
            if name != 'main':
                with open(os.path.join(output_dir, f"sitemap-{name}.xml"), 'w') as f:
                    f.write(content)
        
        logger.info(f"✅ Saved {len(sitemaps)} sitemaps to {output_dir}")
    
    # ================================
    # STRUCTURED DATA (JSON-LD)
    # ================================
    
    def generate_organization_schema(self) -> Dict:
        """Generate Organization schema for JSON-LD"""
        
        return {
            "@context": "https://schema.org/",
            "@type": "Organization",
            "name": self.company_name,
            "url": self.base_urls.get('dispatcher', 'https://gtsdispatcher.com'),
            "logo": urljoin(self.base_urls.get('dispatcher'), '/logo.png'),
            "description": "AI-powered freight management and logistics platform",
            "sameAs": [
                "https://www.linkedin.com/company/gts-dispatcher",
                "https://twitter.com/gtsdispatcher",
            ],
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "SA",
                "addressRegion": "Riyadh"
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "Customer Service",
                "email": "support@gtsdispatcher.com",
                "availableLanguage": ["en", "ar"]
            }
        }
    
    def generate_breadcrumb_schema(self, url: str, breadcrumbs: List[Dict]) -> Dict:
        """Generate breadcrumb schema for a page"""
        
        items = []
        for idx, crumb in enumerate(breadcrumbs):
            items.append({
                "@type": "ListItem",
                "position": idx + 1,
                "name": crumb['name'],
                "item": urljoin(self.base_urls.get('dispatcher'), crumb['url'])
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
    
    def generate_article_schema(self, article: Dict) -> Dict:
        """Generate Article schema for blog posts"""
        
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": article.get('title', ''),
            "description": article.get('meta_description', ''),
            "url": article.get('url', ''),
            "image": article.get('image_url', ''),
            "datePublished": article.get('published_date', datetime.utcnow().isoformat()),
            "dateModified": article.get('crawled_at', datetime.utcnow().isoformat()),
            "author": {
                "@type": "Organization",
                "name": self.company_name
            },
            "publisher": {
                "@type": "Organization",
                "name": self.company_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": urljoin(self.base_urls.get('dispatcher'), '/logo.png')
                }
            }
        }
    
    # ================================
    # META TAG OPTIMIZATION
    # ================================
    
    def generate_meta_tags(self, page: Dict) -> Dict[str, str]:
        """Generate optimized meta tags for a page"""
        
        title = page.get('title', 'GTS Logistics')
        meta_desc = page.get('meta_description', '')
        keywords = page.get('keywords', '')
        content_type = page.get('content_type', '')
        
        # Optimize title (55-60 chars optimal)
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Optimize meta description (155-160 chars optimal)
        if not meta_desc:
            meta_desc = page.get('content_text', '')[:155]
        elif len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."
        
        # Generate keywords if missing
        if not keywords:
            keywords = self._extract_keywords(page.get('content_text', ''))
        
        meta_tags = {
            'title': title,
            'description': meta_desc,
            'keywords': keywords,
            'robots': 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1',
            'viewport': 'width=device-width, initial-scale=1',
            'charset': 'UTF-8',
            'language': 'en-US',
            'author': self.company_name,
            'og:title': title,
            'og:description': meta_desc,
            'og:type': 'website',
            'og:url': page.get('url', ''),
            'og:image': page.get('image_url', ''),
            'og:site_name': 'GTS Dispatcher',
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': meta_desc,
            'twitter:image': page.get('image_url', ''),
        }
        
        # Add canonical tag
        meta_tags['canonical'] = page.get('url', '')
        
        # Content-specific meta tags
        if content_type == 'blog':
            meta_tags['article:author'] = self.company_name
            meta_tags['article:published_time'] = page.get('published_date', '')
            meta_tags['article:modified_time'] = page.get('crawled_at', '')
        
        return meta_tags
    
    def _extract_keywords(self, text: str, count: int = 5) -> str:
        """Extract keywords from text using simple frequency analysis"""
        
        # Simple keyword extraction (in production, use NLTK or similar)
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'is', 'be', 'are', 'was', 'were', 'been', 'have', 'has'}
        
        # Filter and count
        word_freq = {}
        for word in words:
            word = word.strip('.,!?;:')
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:count]
        return ', '.join([kw[0] for kw in top_keywords])
    
    # ================================
    # SEO AUDIT
    # ================================
    
    def audit_page_seo(self, page: Dict) -> Dict:
        """Perform SEO audit on a page"""
        
        audit = {
            'url': page.get('url', ''),
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Check title
        title = page.get('title', '')
        if not title:
            audit['issues'].append("Missing title tag")
        elif len(title) < 30:
            audit['issues'].append(f"Title too short ({len(title)} chars, aim for 50-60)")
        elif len(title) > 60:
            audit['issues'].append(f"Title too long ({len(title)} chars, aim for 50-60)")
        else:
            audit['score'] += 10
        
        # Check meta description
        meta_desc = page.get('meta_description', '')
        if not meta_desc:
            audit['issues'].append("Missing meta description")
        elif len(meta_desc) < 120:
            audit['issues'].append(f"Meta description too short ({len(meta_desc)} chars, aim for 155-160)")
        elif len(meta_desc) > 160:
            audit['issues'].append(f"Meta description too long ({len(meta_desc)} chars, aim for 155-160)")
        else:
            audit['score'] += 10
        
        # Check headings (h1)
        h1_count = len(page.get('h1', []))
        if h1_count == 0:
            audit['issues'].append("Missing H1 tag")
        elif h1_count > 1:
            audit['issues'].append(f"Multiple H1 tags found ({h1_count}), should have exactly 1")
        else:
            audit['score'] += 10
        
        # Check content length
        word_count = page.get('word_count', 0)
        if word_count == 0:
            audit['issues'].append("No content found")
        elif word_count < 300:
            audit['issues'].append(f"Content too short ({word_count} words, aim for 300+)")
        elif word_count > 5000:
            audit['recommendations'].append(f"Consider breaking long content ({word_count} words) into multiple pages")
        else:
            audit['score'] += 15
        
        # Check image optimization
        images = page.get('images', [])
        if images:
            audit['score'] += 10
        else:
            audit['recommendations'].append("Add relevant images to improve engagement")
        
        # Check internal links
        internal_links = page.get('internal_links', 0)
        if internal_links < 3:
            audit['recommendations'].append(f"Add more internal links ({internal_links} found, aim for 3+)")
        else:
            audit['score'] += 10
        
        # Check external links
        external_links = page.get('external_links', 0)
        if external_links > 0:
            audit['score'] += 10
        
        # Check mobile friendliness
        if page.get('schema_org_detected'):
            audit['score'] += 15
        else:
            audit['recommendations'].append("Add structured data (JSON-LD) for better search visibility")
        
        audit['max_score'] = 100
        audit['percentage'] = min(audit['score'], 100)
        
        return audit
    
    def generate_seo_report(self) -> Dict:
        """Generate comprehensive SEO report from Elasticsearch"""
        
        if not self.es:
            logger.error("Elasticsearch not available for SEO report")
            return {}
        
        try:
            response = self.es.search(
                index="gts_content",
                body={
                    "size": 10000,
                    "query": {"match_all": {}},
                    "_source": ["url", "title", "meta_description", "h1", "word_count", 
                               "content_type", "platform_section", "images", "internal_links", 
                               "external_links", "schema_org_detected"]
                }
            )
            
            pages = [hit['_source'] for hit in response['hits']['hits']]
            audits = [self.audit_page_seo(page) for page in pages]
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'total_pages': len(pages),
                'pages_audited': len(audits),
                'average_seo_score': sum(a['score'] for a in audits) / len(audits) if audits else 0,
                'pages_with_issues': len([a for a in audits if a['issues']]),
                'critical_issues': [],
                'top_recommendations': [],
                'audit_details': audits[:50]  # First 50 for report
            }
            
            # Aggregate issues and recommendations
            all_issues = {}
            all_recommendations = {}
            
            for audit in audits:
                for issue in audit['issues']:
                    all_issues[issue] = all_issues.get(issue, 0) + 1
                for rec in audit['recommendations']:
                    all_recommendations[rec] = all_recommendations.get(rec, 0) + 1
            
            report['critical_issues'] = sorted(
                all_issues.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            report['top_recommendations'] = sorted(
                all_recommendations.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            logger.info(f"✅ Generated SEO report for {len(pages)} pages")
            return report
            
        except Exception as e:
            logger.error(f"SEO report generation error: {e}")
            return {}


if __name__ == "__main__":
    # Example usage
    base_urls = {
        'dispatcher': 'https://gtsdispatcher.com',
        'gabani': 'https://gabanilogistics.com'
    }
    
    seo_manager = SEOManager(base_urls)
    
    # Generate and save robots.txt
    seo_manager.save_robots_txt()
    
    # Generate sitemaps
    sitemaps = seo_manager.generate_sitemaps_from_es()
    seo_manager.save_sitemaps(sitemaps)
    
    # Generate SEO report
    report = seo_manager.generate_seo_report()
    print(json.dumps(report, indent=2))
