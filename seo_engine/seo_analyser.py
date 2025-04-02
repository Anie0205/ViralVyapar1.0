import json
import os
from typing import Dict, List
import numpy as np
from collections import defaultdict

class SEOAnalyzer:
    def __init__(self):
        self.weights = {
            'content_quality': 0.25,
            'technical_seo': 0.20,
            'keyword_optimization': 0.20,
            'backlink_profile': 0.20,
            'user_experience': 0.15
        }

    def load_data(self) -> Dict:
        """Load all required data for analysis."""
        try:
            # Load competitor domains
            with open('output/competitor_domains.json', 'r') as f:
                competitor_domains = json.load(f)

            # Load scraped SEO data
            with open('output/scraped_seo_data.json', 'r') as f:
                scraped_data = json.load(f)

            # Load extracted keywords
            with open('output/extracted_keywords.json', 'r') as f:
                keyword_data = json.load(f)

            # Load PageRank scores
            with open('output/pagerank_scores.json', 'r') as f:
                pagerank_data = json.load(f)

            # Load backlink data
            with open('output/high_authority_backlinks.json', 'r') as f:
                backlink_data = json.load(f)

            return {
                'competitor_domains': competitor_domains,
                'scraped_data': scraped_data,
                'keyword_data': keyword_data,
                'pagerank_data': pagerank_data,
                'backlink_data': backlink_data
            }
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return {}

    def analyze_content_quality(self, scraped_data: List[Dict]) -> Dict[str, float]:
        """Analyze content quality metrics."""
        scores = {}
        
        for data in scraped_data:
            url = data['url']
            content = data.get('main_content', '')
            title = data.get('title', '')
            
            # Content length score
            content_length = len(content.split())
            length_score = min(content_length / 1000, 1.0)  # Normalize to 0-1
            
            # Title optimization score
            title_length = len(title)
            title_score = 1.0 if 50 <= title_length <= 60 else 0.5
            
            # Heading structure score
            h1_count = len(data.get('h1_tags', []))
            h2_count = len(data.get('h2_tags', []))
            heading_score = min((h1_count + h2_count) / 5, 1.0)  # Normalize to 0-1
            
            # Image optimization score
            images = data.get('images', [])
            image_score = min(len(images) / 5, 1.0)  # Normalize to 0-1
            
            # Calculate weighted average
            scores[url] = (
                0.4 * length_score +
                0.3 * title_score +
                0.2 * heading_score +
                0.1 * image_score
            )
        
        return scores

    def analyze_technical_seo(self, scraped_data: List[Dict]) -> Dict[str, float]:
        """Analyze technical SEO metrics."""
        scores = {}
        
        for data in scraped_data:
            url = data['url']
            meta_tags = data.get('meta_tags', {})
            schema_data = data.get('schema_data', [])
            
            # Meta description score
            meta_desc = meta_tags.get('description', '')
            meta_desc_score = 1.0 if 150 <= len(meta_desc) <= 160 else 0.5
            
            # Schema markup score
            schema_score = min(len(schema_data) / 3, 1.0)  # Normalize to 0-1
            
            # Mobile responsiveness (simplified)
            mobile_score = 0.8  # This should be enhanced with actual mobile testing
            
            # Calculate weighted average
            scores[url] = (
                0.4 * meta_desc_score +
                0.4 * schema_score +
                0.2 * mobile_score
            )
        
        return scores

    def analyze_keyword_optimization(self, scraped_data: List[Dict], keyword_data: Dict) -> Dict[str, float]:
        """Analyze keyword optimization metrics."""
        scores = {}
        
        for data in scraped_data:
            url = data['url']
            content = data.get('main_content', '').lower()
            title = data.get('title', '').lower()
            
            # Get competitor keywords
            competitor_keywords = keyword_data.get('competitor_keywords', {}).get(url, {})
            nltk_keywords = set(competitor_keywords.get('nltk_keywords', []))
            spacy_keywords = set(competitor_keywords.get('spacy_keywords', []))
            
            # Keyword density score
            all_keywords = nltk_keywords.union(spacy_keywords)
            keyword_count = sum(content.count(kw) for kw in all_keywords)
            density_score = min(keyword_count / 10, 1.0)  # Normalize to 0-1
            
            # Title keyword score
            title_keyword_score = sum(1 for kw in all_keywords if kw in title) / max(len(all_keywords), 1)
            
            # Calculate weighted average
            scores[url] = (
                0.6 * density_score +
                0.4 * title_keyword_score
            )
        
        return scores

    def analyze_backlink_profile(self, backlink_data: Dict, pagerank_data: Dict) -> Dict[str, float]:
        """Analyze backlink profile metrics."""
        scores = {}
        
        for domain, backlinks in backlink_data.items():
            # Backlink count score
            backlink_count = len(backlinks)
            count_score = min(backlink_count / 100, 1.0)  # Normalize to 0-1
            
            # PageRank score
            pagerank = pagerank_data.get(domain, 0)
            pagerank_score = min(pagerank / 10, 1.0)  # Normalize to 0-1
            
            # Calculate weighted average
            scores[domain] = (
                0.5 * count_score +
                0.5 * pagerank_score
            )
        
        return scores

    def analyze_user_experience(self, scraped_data: List[Dict]) -> Dict[str, float]:
        """Analyze user experience metrics."""
        scores = {}
        
        for data in scraped_data:
            url = data['url']
            
            # Content readability (simplified)
            readability_score = 0.8  # This should be enhanced with actual readability analysis
            
            # Mobile responsiveness (simplified)
            mobile_score = 0.8  # This should be enhanced with actual mobile testing
            
            # Page load speed (simplified)
            speed_score = 0.8  # This should be enhanced with actual speed testing
            
            # Calculate weighted average
            scores[url] = (
                0.4 * readability_score +
                0.3 * mobile_score +
                0.3 * speed_score
            )
        
        return scores

    def generate_seo_analysis(self):
        """Generate comprehensive SEO analysis."""
        print("\n📊 Generating comprehensive SEO analysis scores...")
        # Load all required data
        data = self.load_data()
        if not data:
            print("❌ Failed to load necessary data for SEO analysis.")
            return {}

        # Perform individual analyses
        try:
            content_scores = self.analyze_content_quality(data.get('scraped_data', []))
            technical_scores = self.analyze_technical_seo(data.get('scraped_data', []))
            keyword_scores = self.analyze_keyword_optimization(data.get('scraped_data', []), data.get('keyword_data', {}))
            backlink_scores = self.analyze_backlink_profile(data.get('backlink_data', {}), data.get('pagerank_data', {}))
            ux_scores = self.analyze_user_experience(data.get('scraped_data', []))
        except Exception as e:
            print(f"❌ Error during individual analysis component calculation: {e}")
            return {}

        # Combine scores
        overall_analysis = {}
        all_domains = set(content_scores.keys()) | set(technical_scores.keys()) | set(keyword_scores.keys()) | set(backlink_scores.keys()) | set(ux_scores.keys())
        
        if not all_domains:
            print("⚠️ No domains found across analysis components.")
            return {}

        for domain in all_domains:
            # Get individual component scores, defaulting to 0 if missing
            c_score = content_scores.get(domain, 0)
            t_score = technical_scores.get(domain, 0)
            k_score = keyword_scores.get(domain, 0)
            b_score = backlink_scores.get(domain, 0)
            u_score = ux_scores.get(domain, 0)
            
            # Calculate overall score using weighted average
            overall_score = (
                c_score * self.weights['content_quality'] +
                t_score * self.weights['technical_seo'] +
                k_score * self.weights['keyword_optimization'] +
                b_score * self.weights['backlink_profile'] +
                u_score * self.weights['user_experience']
            )
            
            overall_analysis[domain] = {
                'overall_score': overall_score,
                'component_scores': {
                    'content_quality': c_score,
                    'technical_seo': t_score,
                    'keyword_optimization': k_score,
                    'backlink_profile': b_score,
                    'user_experience': u_score
                }
            }

        # Save results to JSON
        self.save_analysis(overall_analysis)
        return overall_analysis

    def generate_recommendations(self, content_score: float, technical_score: float,
                               keyword_score: float, backlink_score: float, ux_score: float) -> List[str]:
        """Generate SEO recommendations based on scores."""
        recommendations = []
        
        if content_score < 0.7:
            recommendations.append("Improve content quality by adding more detailed, valuable content")
        if technical_score < 0.7:
            recommendations.append("Enhance technical SEO by optimizing meta tags and implementing schema markup")
        if keyword_score < 0.7:
            recommendations.append("Strengthen keyword optimization by improving keyword density and placement")
        if backlink_score < 0.7:
            recommendations.append("Build more high-quality backlinks to improve domain authority")
        if ux_score < 0.7:
            recommendations.append("Enhance user experience by improving page load speed and mobile responsiveness")
        
        return recommendations

    def save_analysis(self, analysis: Dict):
        """Save SEO analysis results to JSON file."""
        try:
            os.makedirs('output', exist_ok=True)
            with open('output/seo_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=4, ensure_ascii=False)
            print(f"✅ SEO analysis saved to output/seo_analysis.json")
        except Exception as e:
            print(f"❌ Error saving SEO analysis: {e}")

if __name__ == "__main__":
    analyzer = SEOAnalyzer()
    analyzer.generate_seo_analysis()
