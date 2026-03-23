"""
NLP Processor - Natural Language Processing for user queries
Processes user reports and questions using NLP techniques
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("maintenance.nlp")


class NLPProcessor:
    """Natural Language Processor for maintenance bot conversations"""
    
    def __init__(self):
        self.keywords = self._load_keywords()
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """Load keyword dictionaries for classification"""
        return {
            'bug': [
                'error', 'bug', 'crash', 'broken', 'not working', 'issue', 'problem',
                'failure', 'fault', 'malfunction', 'defect', 'exception'
            ],
            'performance': [
                'slow', 'lag', 'latency', 'timeout', 'performance', 'fast', 'speed',
                'throughput', 'delay', 'bottleneck', 'response time'
            ],
            'security': [
                'security', 'hack', 'breach', 'vulnerability', 'unauthorized', 'access',
                'attack', 'phishing', 'exploit', 'compromised'
            ],
            'ui': [
                'ui', 'interface', 'design', 'layout', 'display', 'screen', 'button',
                'dropdown', 'form', 'menu', 'alignment', 'rendering'
            ],
            'data': [
                'data', 'database', 'record', 'missing', 'lost', 'corrupt',
                'inconsistent', 'duplicate', 'sync', 'backup', 'restore'
            ],
            'api': [
                'api', 'endpoint', 'request', 'response', 'integration', 'service',
                'payload', 'webhook', 'authentication', 'rate limit'
            ],
            'deployment': [
                'deploy', 'deployment', 'release', 'update', 'upgrade', 'version',
                'rollback', 'pipeline', 'build', 'migration'
            ]
        }
    
    def _load_intent_patterns(self) -> List[Dict[str, Any]]:
        """Load intent detection patterns"""
        return [
            {
                'intent': 'report_bug',
                'patterns': [
                    r'(found|discovered|encountered|experiencing)\s+(a|an)?\s*(bug|error|issue)',
                    r'(not|isn\'t|doesn\'t)\s+work(ing)?',
                    r'(broken|crash|fail|fails|failed)',
                    r'(something|this|it)\s+(is|seems)\s+(broken|failing)',
                    r'(keeps|continues to)\s+(crashing|failing|timing out)'
                ],
                'confidence_boost': 0.3
            },
            {
                'intent': 'ask_question',
                'patterns': [
                    r'^(how|what|why|when|where|who|which|can|could|should|would)',
                    r'\?$',
                    r'^(is|are|do|does|did|will|can|could)'
                ],
                'confidence_boost': 0.2
            },
            {
                'intent': 'request_help',
                'patterns': [
                    r'(help|assist|support|need)',
                    r'(please|kindly)',
                    r'(can you|could you|please help|need assistance)'
                ],
                'confidence_boost': 0.25
            },
            {
                'intent': 'provide_feedback',
                'patterns': [
                    r'(suggest|suggestion|recommend|improve|feedback)',
                    r'(should|could|would)\s+(be|have)',
                    r'(it would be better|consider adding|feature request|enhancement)'
                ],
                'confidence_boost': 0.2
            },
            {
                'intent': 'request_status',
                'patterns': [
                    r'(status|state|condition|health)',
                    r'(check|test|verify|validate)',
                    r'(is it up|any update|what\'s the status|system health)'
                ],
                'confidence_boost': 0.25
            }
        ]
    
    def _load_entity_patterns(self) -> Dict[str, str]:
        """Load entity extraction patterns"""
        return {
            'url': r'https?://[^\s]+',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'error_code': r'(error|code|ERR)[-_]?\d{3,5}',
            'version': r'v?\d+\.\d+\.\d+',
            'ip_address': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            'file_path': r'[/\\]?[a-zA-Z0-9_\-./\\]+\.[a-zA-Z0-9]{2,5}',
            'percentage': r'\d+(\.\d+)?%',
            'duration': r'\d+\s*(ms|sec|seconds|min|minutes|hour|hours|day|days)'
        }
    
    async def process_message(self, message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message and extract intent and entities"""
        try:
            # Clean and normalize message
            cleaned_message = self.clean_text(message)
            
            # Extract intent
            intent = self.extract_intent(cleaned_message)
            
            # Extract entities
            entities = self.extract_entities(cleaned_message)
            
            # Classify issue type
            issue_type = self.classify_issue_type(cleaned_message)
            
            # Extract sentiment
            sentiment = self.analyze_sentiment(cleaned_message)
            
            # Calculate urgency
            urgency = self.calculate_urgency(cleaned_message, intent, sentiment)
            
            return {
                'original_message': message,
                'cleaned_message': cleaned_message,
                'intent': intent,
                'entities': entities,
                'issue_type': issue_type,
                'sentiment': sentiment,
                'urgency': urgency,
                'processed_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return {
                'original_message': message,
                'error': str(e)
            }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Convert to lowercase for processing (keep original for display)
        return text
    
    def extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract user intent from text"""
        text_lower = text.lower()
        
        intent_scores = {}
        
        # Check each intent pattern
        for intent_config in self.intent_patterns:
            intent_name = intent_config['intent']
            patterns = intent_config['patterns']
            confidence_boost = intent_config.get('confidence_boost', 0.0)
            
            score = 0.0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += confidence_boost
                    matched_patterns.append(pattern)
            
            if matched_patterns:
                intent_scores[intent_name] = {
                    'score': score,
                    'matched_patterns': matched_patterns
                }
        
        # Get highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
            return {
                'intent': best_intent[0],
                'confidence': min(1.0, best_intent[1]['score']),
                'all_intents': intent_scores
            }
        
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'all_intents': {}
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Handle tuple results from groups
                if isinstance(matches[0], tuple):
                    matches = [''.join(m) for m in matches]
                entities[entity_type] = matches
        
        return entities
    
    def classify_issue_type(self, text: str) -> Dict[str, Any]:
        """Classify the type of issue being reported"""
        text_lower = text.lower()
        
        scores = {}
        
        for issue_type, keywords in self.keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                scores[issue_type] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1]['score'])
            return {
                'type': best_type[0],
                'confidence': min(1.0, best_type[1]['score'] / 5),  # Normalize
                'all_types': scores
            }
        
        return {
            'type': 'general',
            'confidence': 0.0,
            'all_types': {}
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the message"""
        text_lower = text.lower()
        
        # Simple keyword-based sentiment analysis
        positive_keywords = [
            'good', 'great', 'excellent', 'perfect', 'love', 'thanks', 'thank',
            'awesome', 'helpful', 'resolved', 'appreciate'
        ]
        negative_keywords = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'angry', 'frustrated',
            'broken', 'annoying', 'unacceptable', 'disappointed'
        ]
        urgent_keywords = [
            'urgent', 'critical', 'emergency', 'asap', 'immediately', 'now',
            'right away', 'priority', 'production down', 'blocking'
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        urgent_count = sum(1 for kw in urgent_keywords if kw in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_count - negative_count) / max(1, positive_count + negative_count)
        
        if sentiment_score > 0.3:
            sentiment = 'positive'
        elif sentiment_score < -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'is_urgent': urgent_count > 0,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'urgent_count': urgent_count
        }
    
    def calculate_urgency(self, text: str, intent: Dict[str, Any], sentiment: Dict[str, Any]) -> str:
        """Calculate urgency level based on multiple factors"""
        urgency_score = 0
        
        # Sentiment urgency
        if sentiment.get('is_urgent'):
            urgency_score += 3
        
        if sentiment.get('sentiment') == 'negative':
            urgency_score += 1
        
        # Intent urgency
        if intent.get('intent') == 'report_bug':
            urgency_score += 2
        
        # Keyword urgency
        text_lower = text.lower()
        critical_keywords = ['crash', 'down', 'outage', 'security', 'breach', 'data loss', 'production', 'critical']
        for keyword in critical_keywords:
            if keyword in text_lower:
                urgency_score += 2
                break
        
        # Classify urgency
        if urgency_score >= 5:
            return 'critical'
        elif urgency_score >= 3:
            return 'high'
        elif urgency_score >= 1:
            return 'medium'
        else:
            return 'low'
    
    async def generate_response(self, analysis: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Generate appropriate response based on analysis"""
        intent = analysis.get('intent', {}).get('intent', 'unknown')
        issue_type = analysis.get('issue_type', {}).get('type', 'general')
        urgency = analysis.get('urgency', 'low')
        
        # Acknowledge urgency
        if urgency == 'critical':
            prefix = "🔴 I understand this is critical. "
        elif urgency == 'high':
            prefix = "🟠 I'll prioritize this issue. "
        else:
            prefix = ""
        
        # Generate response based on intent
        if intent == 'report_bug':
            return f"{prefix}Thank you for reporting this {issue_type} issue. I'm analyzing the problem and will either fix it automatically or escalate to the development team. I'll keep you updated on the progress."
        
        elif intent == 'ask_question':
            return f"{prefix}I'll help you with your question about {issue_type}. Let me search the knowledge base for relevant information..."
        
        elif intent == 'request_help':
            return f"{prefix}I'm here to help with your {issue_type} concern. Could you provide more details so I can assist you better?"
        
        elif intent == 'provide_feedback':
            return f"{prefix}Thank you for your feedback regarding {issue_type}. I'll add this to our recommendations for the development team."
        
        elif intent == 'request_status':
            return f"{prefix}I'll check the current status of the {issue_type} system for you..."
        
        else:
            return f"{prefix}I've received your message. I'll analyze it and get back to you shortly with the appropriate action."
    
    def extract_technical_details(self, text: str) -> Dict[str, Any]:
        """Extract technical details from error messages"""
        details = {}
        
        # Extract stack trace
        stack_trace_pattern = r'(Traceback|Stack trace|at\s+\w+\.\w+)[^\n]+'
        stack_traces = re.findall(stack_trace_pattern, text, re.MULTILINE)
        if stack_traces:
            details['stack_trace'] = stack_traces
        
        # Extract function/method names
        function_pattern = r'(\w+)\s*\([^\)]*\)'
        functions = re.findall(function_pattern, text)
        if functions:
            details['functions'] = list(set(functions))[:10]  # Top 10 unique
        
        # Extract file names
        file_pattern = r'([a-zA-Z0-9_\-]+\.(py|js|jsx|ts|tsx|java|cpp|c))'
        files = re.findall(file_pattern, text, re.IGNORECASE)
        if files:
            details['files'] = list(set([f[0] for f in files]))
        
        # Extract line numbers
        line_pattern = r'line\s+(\d+)'
        lines = re.findall(line_pattern, text, re.IGNORECASE)
        if lines:
            details['line_numbers'] = lines
        
        return details
