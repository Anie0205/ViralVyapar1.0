from sklearn.preprocessing import StandardScaler

def preprocess_content(content):
    return content.lower()

def calculate_seo_score(ctr, difficulty):
    score = (ctr * 100) - (difficulty * 2)
    return max(0, min(score, 100))
