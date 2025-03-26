import re
from collections import Counter

def extract_keywords(text, num_keywords=5):
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = {'the', 'and', 'of', 'to', 'in', 'for', 'with', 'on', 'at', 'by'}
    
    keywords = [word for word in words if word not in stopwords]
    most_common = Counter(keywords).most_common(num_keywords)
    
    return [word for word, _ in most_common]
