# Content Optimizer with NLP Analysis
# Content Optimizer with NLP Analysis

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentOptimizer:
    """Analyzes and optimizes content for SEO and readability"""
    
    def __init__(self, es_client: Optional[Elasticsearch] = None):
        self.es = es_client or self._init_es()
        self.keywords_extracted = {}
        
    def _init_es(self):
        """Initialize Elasticsearch connection"""
        try:
            client = Elasticsearch(['http://localhost:9200'])
            if client.ping():
                logger.info("✅ Elasticsearch connected for Content Optimizer")
            return client
        except Exception as e:
            logger.error(f"Elasticsearch initialization failed: {e}")
            return None
    
    # ================================
    # KEYWORD ANALYSIS
    # ================================
    
    def extract_keywords(self, text: str, min_length: int = 3, top_n: int = 10) -> Dict[str, int]:
        """
        Extract main keywords from text using TF (Term Frequency)
        
        Args:
            text: Text to analyze
            min_length: Minimum word length
            top_n: Number of top keywords to return
        
        Returns:
            Dictionary of keywords and their frequencies
        """
        
        # Normalize text
        text = text.lower().strip()
        
        # Remove special characters and split
        words = re.findall(r'\b[a-z0-9]+\b', text)
        
        # Common stop words (English and Arabic concepts)
        stop_words = {
            # Common English
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'be', 'are', 'was', 'were', 'been', 'have', 'has', 'do',
            'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'it', 'its', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'her', 'our', 'their', 'as', 'by',
            'with', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'each', 'every', 'some', 'any', 'both', 'few', 'more',
            'most', 'other', 'very', 'just', 'so', 'too', 'not', 'no', 'nor',
            'only', 'same', 'such', 'own', 'now', 'being'
        }
        
        # Filter words
        filtered_words = [
            word for word in words 
            if len(word) >= min_length and word not in stop_words
        ]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        return dict(word_freq.most_common(top_n))
    
    def extract_keyphrases(self, text: str, phrase_length: int = 2, top_n: int = 5) -> Dict[str, int]:
        """Extract key phrases (2-4 word combinations) from text"""
        
        # Split into sentences and words
        sentences = re.split(r'[.!?]\s+', text)
        phrases = []
        
        for sentence in sentences:
            words = re.findall(r'\b[a-z0-9]+\b', sentence.lower())
            
            # Extract n-grams
            for i in range(len(words) - phrase_length + 1):
                phrase = ' '.join(words[i:i + phrase_length])
                phrases.append(phrase)
        
        # Count and filter
        phrase_freq = Counter(phrases)
        
        # Filter out phrases with mostly stop words
        stop_words = {'the', 'a', 'and', 'or', 'is', 'be', 'in', 'on', 'at'}
        filtered_phrases = {
            phrase: count for phrase, count in phrase_freq.items()
            if sum(1 for word in phrase.split() if word not in stop_words) > 0
        }
        
        return dict(sorted(filtered_phrases.items(), key=lambda x: x[1], reverse=True)[:top_n])
    
    def analyze_keyword_density(self, text: str, keyword: str) -> float:
        """Calculate keyword density (keyword mentions / total words)"""
        
        words = re.findall(r'\b[a-z0-9]+\b', text.lower())
        total_words = len(words)
        
        if total_words == 0:
            return 0
        
        keyword_lower = keyword.lower()
        keyword_matches = sum(1 for word in words if word == keyword_lower)
        
        density = (keyword_matches / total_words) * 100
        
        return round(density, 2)
    
    # ================================
    # READABILITY ANALYSIS
    # ================================
    
    def calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """Calculate multiple readability metrics"""
        
        # Basic metrics
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b[a-z0-9]+\b', text.lower())
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not sentences or not words:
            return {
                'flesch_kincaid_grade': 0,
                'flesch_reading_ease': 100,
                'gunning_fog_index': 0,
                'dale_chall_score': 0,
                'smog_index': 0,
                'automated_readability_index': 0,
                'average_words_per_sentence': 0,
                'average_syllables_per_word': 0,
                'recommended_grade_level': 0
            }
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid = max(0, flesch_kincaid)
        
        # Flesch Reading Ease
        flesch_ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_ease = max(0, min(100, flesch_ease))
        
        # Gunning Fog Index
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        gunning_fog = (0.4 * ((len(words) / len(sentences)) + (100 * complex_words / len(words))))
        gunning_fog = max(0, gunning_fog)
        
        # SMOG Index
        smog = (1.0430 * (complex_words * (30 / len(sentences))) ** 0.5) + 3.1291
        smog = max(0, smog)
        
        # Automated Readability Index
        ari = (4.71 * (len(words) / len(sentences))) + (0.5 * (len(words) / sum(1 for word in words if re.match(r'[a-z]', word))))
        
        return {
            'flesch_kincaid_grade': round(flesch_kincaid, 2),
            'flesch_reading_ease': round(flesch_ease, 2),
            'gunning_fog_index': round(gunning_fog, 2),
            'smog_index': round(smog, 2),
            'automated_readability_index': round(ari, 2),
            'average_words_per_sentence': round(avg_words_per_sentence, 2),
            'average_syllables_per_word': round(avg_syllables_per_word, 2),
            'recommended_grade_level': self._interpret_grade_level(flesch_kincaid),
            'total_sentences': len(sentences),
            'total_words': len(words),
            'total_paragraphs': len(paragraphs),
            'character_count': len(text)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counter for English"""
        
        word = word.lower()
        vowels = 'aeiou'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            
            previous_was_vowel = is_vowel
        
        # Adjustments
        if word.endswith('e'):
            syllable_count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllable_count += 1
        
        return max(1, syllable_count)
    
    def _interpret_grade_level(self, flesch_kincaid: float) -> str:
        """Interpret Flesch-Kincaid grade level"""
        
        if flesch_kincaid < 6:
            return "Elementary School"
        elif flesch_kincaid < 9:
            return "Middle School"
        elif flesch_kincaid < 13:
            return "High School"
        elif flesch_kincaid < 16:
            return "College"
        else:
            return "Graduate School"
    
    # ================================
    # CONTENT STRUCTURE ANALYSIS
    # ================================
    
    def analyze_content_structure(self, text: str, title: str = "", h1_tags: List[str] = None) -> Dict:
        """Analyze content structure and organization"""
        
        if h1_tags is None:
            h1_tags = []
        
        # Count headings by level
        h2_count = len(re.findall(r'^#{2}[^#]', text, re.MULTILINE))
        h3_count = len(re.findall(r'^#{3}[^#]', text, re.MULTILINE))
        h4_count = len(re.findall(r'^#{4}[^#]', text, re.MULTILINE))
        
        # Count lists
        ul_items = len(re.findall(r'^\s*[-*]\s', text, re.MULTILINE))
        ol_items = len(re.findall(r'^\s*\d+\.\s', text, re.MULTILINE))
        
        # Count images and links
        images = len(re.findall(r'!\[', text))
        internal_links = len(re.findall(r'\[([^\]]+)\]\(/[^)]*\)', text))
        external_links = len(re.findall(r'\[([^\]]+)\]\(https?://[^)]*\)', text))
        
        # Check for table of contents
        has_toc = bool(re.search(r'#{2,}\s+Table of Contents', text))
        
        # Analyze paragraph length
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        return {
            'title_exists': bool(title),
            'title_length': len(title) if title else 0,
            'h1_count': len(h1_tags),
            'h2_count': h2_count,
            'h3_count': h3_count,
            'h4_count': h4_count,
            'unordered_lists': ul_items,
            'ordered_lists': ol_items,
            'total_list_items': ul_items + ol_items,
            'images': images,
            'internal_links': internal_links,
            'external_links': external_links,
            'has_table_of_contents': has_toc,
            'paragraph_count': len(paragraphs),
            'average_paragraph_length': round(avg_para_length, 2),
            'is_well_structured': h2_count >= 2 and (ul_items + ol_items) >= 2
        }
    
    # ================================
    # OPTIMIZATION RECOMMENDATIONS
    # ================================
    
    def get_optimization_recommendations(self, page_data: Dict) -> List[Dict]:
        """Generate actionable optimization recommendations"""
        
        recommendations = []
        
        # Title optimization
        title = page_data.get('title', '')
        if not title:
            recommendations.append({
                'priority': 'high',
                'category': 'Meta Tags',
                'issue': 'Missing page title',
                'recommendation': 'Add a descriptive title tag (50-60 characters)',
                'action': 'Create title with target keyword'
            })
        elif len(title) < 30:
            recommendations.append({
                'priority': 'medium',
                'category': 'Meta Tags',
                'issue': 'Title too short',
                'recommendation': f'Expand title from {len(title)} to 50-60 characters',
                'action': 'Add more descriptive keywords to title'
            })
        elif len(title) > 60:
            recommendations.append({
                'priority': 'low',
                'category': 'Meta Tags',
                'issue': 'Title too long',
                'recommendation': f'Reduce title from {len(title)} to 50-60 characters',
                'action': 'Remove unnecessary words'
            })
        
        # Content length
        word_count = page_data.get('word_count', 0)
        if word_count < 300:
            recommendations.append({
                'priority': 'high',
                'category': 'Content',
                'issue': 'Thin content',
                'recommendation': f'Expand content from {word_count} to at least 300 words',
                'action': 'Add more detailed information about your topic'
            })
        elif word_count > 5000:
            recommendations.append({
                'priority': 'medium',
                'category': 'Content',
                'issue': 'Excessive content length',
                'recommendation': f'Consider splitting {word_count}-word content into multiple pages',
                'action': 'Create separate pages for subtopics'
            })
        else:
            recommendations.append({
                'priority': 'none',
                'category': 'Content',
                'issue': 'Content length optimal',
                'recommendation': 'Content length is good for SEO',
                'action': 'Monitor for changes'
            })
        
        # Keyword optimization
        keywords = page_data.get('keywords', {})
        if not keywords:
            recommendations.append({
                'priority': 'high',
                'category': 'Keywords',
                'issue': 'No keywords identified',
                'recommendation': 'Add focus keywords to your content',
                'action': 'Research and naturally incorporate target keywords'
            })
        
        # Structure analysis
        structure = page_data.get('structure', {})
        if structure.get('h1_count', 0) == 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Structure',
                'issue': 'Missing H1 heading',
                'recommendation': 'Add exactly one H1 tag with main keyword',
                'action': 'Add H1 at the beginning of your content'
            })
        
        if structure.get('h2_count', 0) < 2:
            recommendations.append({
                'priority': 'medium',
                'category': 'Structure',
                'issue': 'Insufficient subheadings',
                'recommendation': 'Add at least 2 H2 subheadings',
                'action': 'Organize content with descriptive subheadings'
            })
        
        # Media
        if structure.get('images', 0) == 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'Media',
                'issue': 'No images',
                'recommendation': 'Add relevant images to improve engagement',
                'action': 'Include 1 image per 500 words'
            })
        
        # Internal linking
        if structure.get('internal_links', 0) < 3:
            recommendations.append({
                'priority': 'medium',
                'category': 'Links',
                'issue': 'Insufficient internal links',
                'recommendation': 'Add 3+ internal links to other relevant pages',
                'action': 'Link to related content on your site'
            })
        
        # Readability
        readability = page_data.get('readability', {})
        grade_level = readability.get('recommended_grade_level', '')
        
        if 'Graduate' in grade_level or 'College' in grade_level:
            recommendations.append({
                'priority': 'medium',
                'category': 'Readability',
                'issue': 'Complex writing',
                'recommendation': 'Simplify language for better readability',
                'action': 'Use shorter sentences and common words'
            })
        
        return recommendations
    
    # ================================
    # COMPREHENSIVE ANALYSIS
    # ================================
    
    def analyze_complete_content(self, page: Dict) -> Dict:
        """Perform comprehensive content analysis"""
        
        text = page.get('content_text', '')
        title = page.get('title', '')
        
        if not text:
            logger.warning(f"Empty content for page: {page.get('url')}")
            return {}
        
        analysis = {
            'url': page.get('url', ''),
            'title': title,
            'analyzed_at': datetime.utcnow().isoformat(),
            
            # Keywords
            'keywords': self.extract_keywords(text),
            'keyphrases': self.extract_keyphrases(text),
            
            # Readability
            'readability': self.calculate_readability_scores(text),
            
            # Structure
            'structure': self.analyze_content_structure(text, title, page.get('h1', [])),
            
            # Recommendations
            'recommendations': self.get_optimization_recommendations({
                'title': title,
                'word_count': len(text.split()),
                'keywords': self.extract_keywords(text),
                'structure': self.analyze_content_structure(text, title, page.get('h1', [])),
                'readability': self.calculate_readability_scores(text)
            })
        }
        
        return analysis
    
    def generate_content_report(self) -> Dict:
        """Generate comprehensive content analysis report from all indexed pages"""
        
        if not self.es:
            logger.error("Elasticsearch not available for content report")
            return {}
        
        try:
            response = self.es.search(
                index="gts_content",
                body={
                    "size": 1000,
                    "query": {"match_all": {}},
                    "_source": ["url", "title", "content_text", "h1", "word_count"]
                }
            )
            
            pages = [hit['_source'] for hit in response['hits']['hits']]
            analyses = []
            
            for page in pages:
                analysis = self.analyze_complete_content(page)
                if analysis:
                    analyses.append(analysis)
            
            # Aggregate insights
            all_keywords = {}
            avg_readability = {'flesch_kincaid_grade': 0, 'flesch_reading_ease': 0}
            
            for analysis in analyses:
                for kw, count in analysis.get('keywords', {}).items():
                    all_keywords[kw] = all_keywords.get(kw, 0) + count
                
                readability = analysis.get('readability', {})
                avg_readability['flesch_kincaid_grade'] += readability.get('flesch_kincaid_grade', 0)
                avg_readability['flesch_reading_ease'] += readability.get('flesch_reading_ease', 0)
            
            if analyses:
                avg_readability['flesch_kincaid_grade'] /= len(analyses)
                avg_readability['flesch_reading_ease'] /= len(analyses)
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'total_pages_analyzed': len(analyses),
                'top_keywords': dict(sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:20]),
                'average_readability': {k: round(v, 2) for k, v in avg_readability.items()},
                'analyses': analyses[:50]  # First 50 for report
            }
            
            logger.info(f"✅ Generated content report for {len(analyses)} pages")
            return report
            
        except Exception as e:
            logger.error(f"Content report generation error: {e}")
            return {}


if __name__ == "__main__":
    # Example usage
    optimizer = ContentOptimizer()
    
    # Example page data
    sample_page = {
        'url': 'https://gtsdispatcher.com/blog/logistics-101',
        'title': 'Complete Guide to Modern Logistics Management',
        'content_text': '''Logistics management is the backbone of modern supply chains...
        This comprehensive guide covers everything from warehouse management to last-mile delivery.
        Learn how to optimize your freight operations and reduce costs...[full content]''',
        'h1': ['Complete Guide to Modern Logistics Management'],
        'word_count': 2500
    }
    
    # Analyze content
    analysis = optimizer.analyze_complete_content(sample_page)
    print(json.dumps(analysis, indent=2))
