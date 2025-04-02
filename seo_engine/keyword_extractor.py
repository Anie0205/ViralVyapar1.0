import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from collections import Counter
import os
from typing import List, Dict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

class KeywordExtractor:
    def __init__(self):
        # Download required NLTK data
        required_nltk_resources = {
            'tokenizers/punkt': 'punkt',
            'tokenizers/punkt_tab': 'punkt_tab',
            'taggers/averaged_perceptron_tagger': 'averaged_perceptron_tagger',
            'taggers/averaged_perceptron_tagger_eng': 'averaged_perceptron_tagger_eng',
            'corpora/stopwords': 'stopwords'
        }
        
        resources_to_download = []
        for resource_path, resource_id in required_nltk_resources.items():
            try:
                nltk.data.find(resource_path)
            except LookupError:
                print(f"NLTK resource '{resource_id}' not found. Adding to download list.")
                resources_to_download.append(resource_id)
                
        if resources_to_download:
            print(f"Downloading missing NLTK resources: {resources_to_download}")
            nltk.download(resources_to_download)
            print("NLTK downloads complete.")

        # Load spaCy model
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Installing spaCy model...")
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

        self.stop_words = set(stopwords.words('english'))
        self.tfidf = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3)
        )

    def load_scraped_data(self) -> List[Dict]:
        """Load scraped SEO data from JSON file."""
        try:
            with open('output/scraped_seo_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading scraped data: {e}")
            return []

    def extract_keywords_nltk(self, text: str) -> List[str]:
        """Extract keywords using NLTK."""
        # Tokenize and tag parts of speech
        tokens = word_tokenize(text.lower())
        tagged = pos_tag(tokens)

        # Extract nouns and important words
        keywords = []
        for word, tag in tagged:
            if (tag.startswith('NN') or tag.startswith('JJ')) and word not in self.stop_words:
                keywords.append(word)

        return keywords

    def extract_keywords_spacy(self, text: str) -> List[str]:
        """Extract keywords using spaCy."""
        doc = self.nlp(text)
        
        # Extract named entities and important nouns
        keywords = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                keywords.append(ent.text.lower())
        
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                keywords.append(token.text.lower())

        return keywords

    def extract_keywords_tfidf(self, texts: List[str]) -> List[str]:
        """Extract keywords using TF-IDF."""
        try:
            tfidf_matrix = self.tfidf.fit_transform(texts)
            feature_names = self.tfidf.get_feature_names_out()
            
            # Get top keywords based on TF-IDF scores
            scores = tfidf_matrix.sum(axis=0).A1
            top_indices = scores.argsort()[-20:][::-1]
            
            return [feature_names[i] for i in top_indices]
        except Exception as e:
            print(f"❌ Error in TF-IDF extraction: {e}")
            return []

    def process_competitor_data(self):
        """Process all competitor data and extract keywords."""
        scraped_data = self.load_scraped_data()
        
        # Validate scraped data
        if not scraped_data:
            print("❌ No scraped data found. Please run the scraper first.")
            return {}
            
        all_keywords = []
        competitor_keywords = {}

        for competitor in scraped_data:
            url = competitor.get('url', '')
            if not url:
                print("⚠️ Skipping competitor with no URL")
                continue
                
            content = competitor.get('main_content', '')
            title = competitor.get('title', '')
            
            # Skip if both content and title are empty
            if not content and not title:
                print(f"⚠️ Skipping {url} - no content found")
                continue
            
            # Combine title and content for better keyword extraction
            full_text = f"{title} {content}".strip()
            
            # Skip if the combined text is too short
            if len(full_text.split()) < 10:
                print(f"⚠️ Skipping {url} - insufficient content")
                continue
            
            try:
                # Extract keywords using different methods
                nltk_keywords = self.extract_keywords_nltk(full_text)
                spacy_keywords = self.extract_keywords_spacy(full_text)
                
                # Only add if we found keywords
                if nltk_keywords or spacy_keywords:
                    competitor_keywords[url] = {
                        'nltk_keywords': nltk_keywords,
                        'spacy_keywords': spacy_keywords
                    }
                    
                    all_keywords.extend(nltk_keywords)
                    all_keywords.extend(spacy_keywords)
                else:
                    print(f"⚠️ No keywords found for {url}")
                    
            except Exception as e:
                print(f"❌ Error processing {url}: {e}")
                continue

        # Only proceed with TF-IDF if we have enough content
        if all_keywords:
            # Extract TF-IDF keywords from all content
            all_texts = [f"{c.get('title', '')} {c.get('main_content', '')}" 
                        for c in scraped_data 
                        if c.get('main_content') or c.get('title')]
            
            if all_texts:
                try:
                    tfidf_keywords = self.extract_keywords_tfidf(all_texts)
                except Exception as e:
                    print(f"❌ Error in TF-IDF extraction: {e}")
                    tfidf_keywords = []
            else:
                print("⚠️ No valid texts for TF-IDF analysis")
                tfidf_keywords = []
        else:
            print("⚠️ No keywords found in any content")
            tfidf_keywords = []

        # Count keyword frequencies
        keyword_frequencies = Counter(all_keywords)

        # Prepare final output
        output = {
            'competitor_keywords': competitor_keywords,
            'tfidf_keywords': tfidf_keywords,
            'keyword_frequencies': dict(keyword_frequencies.most_common(50))
        }

        # Save results
        self.save_keywords(output)
        return output

    def save_keywords(self, data: Dict):
        """Save extracted keywords to JSON file."""
        try:
            os.makedirs('output', exist_ok=True)
            with open('output/extracted_keywords.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Extracted keywords saved to output/extracted_keywords.json")
        except Exception as e:
            print(f"❌ Error saving keywords: {e}")

if __name__ == "__main__":
    extractor = KeywordExtractor()
    extractor.process_competitor_data()
