import json
import os
from typing import Dict, List
import re
from collections import defaultdict

class SearchIntentClassifier:
    def __init__(self):
        # Define intent patterns
        self.intent_patterns = {
            'navigational': [
                r'^(facebook|twitter|instagram|linkedin|youtube|amazon|google|wikipedia)',
                r'^(www\.|https?://)',
                r'^(login|sign in|account)',
                r'^(my|your) (account|profile|dashboard)'
            ],
            'transactional': [
                r'(buy|purchase|order|shop|cart|checkout|price|cost|deal|offer|sale)',
                r'(download|install|subscribe|sign up|register)',
                r'(book|reserve|schedule|appointment)',
                r'(contact|email|phone|call|message)'
            ],
            'informational': [
                r'(what|how|why|when|where|who|which)',
                r'(guide|tutorial|learn|understand|explain)',
                r'(tips|tricks|best practices|examples)',
                r'(review|comparison|vs|difference)'
            ]
        }

        # Define intent-specific keywords
        self.intent_keywords = {
            'navigational': {
                'brand_terms': ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'amazon', 'google'],
                'action_terms': ['login', 'sign in', 'account', 'profile', 'dashboard']
            },
            'transactional': {
                'purchase_terms': ['buy', 'purchase', 'order', 'shop', 'cart', 'checkout'],
                'price_terms': ['price', 'cost', 'deal', 'offer', 'sale'],
                'action_terms': ['download', 'install', 'subscribe', 'sign up', 'register']
            },
            'informational': {
                'question_terms': ['what', 'how', 'why', 'when', 'where', 'who', 'which'],
                'learning_terms': ['guide', 'tutorial', 'learn', 'understand', 'explain'],
                'research_terms': ['review', 'comparison', 'vs', 'difference']
            }
        }

    def load_queries(self) -> List[str]:
        """Load SEO queries from JSON file."""
        try:
            with open('output/seo_queries.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading queries: {e}")
            return []

    def classify_by_patterns(self, query: str) -> Dict[str, float]:
        """Classify query intent using regex patterns."""
        scores = defaultdict(float)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query.lower()):
                    scores[intent] += 1
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return dict(scores)

    def classify_by_keywords(self, query: str) -> Dict[str, float]:
        """Classify query intent using keyword matching."""
        scores = defaultdict(float)
        query_words = set(query.lower().split())
        
        for intent, keywords in self.intent_keywords.items():
            for category, terms in keywords.items():
                matches = sum(1 for term in terms if term in query_words)
                if matches > 0:
                    scores[intent] += matches
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return dict(scores)

    def classify_query(self, query: str) -> Dict[str, float]:
        """Classify query intent using both patterns and keywords."""
        pattern_scores = self.classify_by_patterns(query)
        keyword_scores = self.classify_by_keywords(query)
        
        # Combine scores with weights
        final_scores = defaultdict(float)
        for intent in set(pattern_scores.keys()) | set(keyword_scores.keys()):
            final_scores[intent] = (
                0.6 * pattern_scores.get(intent, 0) +
                0.4 * keyword_scores.get(intent, 0)
            )
        
        # If no clear intent, default to informational
        if not final_scores:
            final_scores['informational'] = 1.0
        
        return dict(final_scores)

    def analyze_search_intents(self):
        """Analyze search intents for all queries."""
        queries = self.load_queries()
        if not queries:
            return

        results = {}
        for query in queries:
            intent_scores = self.classify_query(query)
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            
            results[query] = {
                'intent_scores': intent_scores,
                'primary_intent': primary_intent,
                'confidence': intent_scores[primary_intent]
            }

        # Save results
        self.save_results(results)
        return results

    def save_results(self, results: Dict):
        """Save search intent analysis results to JSON file."""
        try:
            os.makedirs('output', exist_ok=True)
            with open('output/search_intents.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"✅ Search intent analysis saved to output/search_intents.json")
        except Exception as e:
            print(f"❌ Error saving search intent analysis: {e}")

if __name__ == "__main__":
    classifier = SearchIntentClassifier()
    classifier.analyze_search_intents()
