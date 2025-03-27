import joblib
import numpy as np

def predict_ctr(difficulty):
    ctr_model = joblib.load('models/ctr_model.pkl')
    difficulty = np.array(difficulty).reshape(-1, 1)
    return ctr_model.predict(difficulty)[0]

def estimate_difficulty(ctr):
    difficulty_model = joblib.load('models/keyword_difficulty.pkl')
    ctr = np.array(ctr).reshape(-1, 1)
    return difficulty_model.predict(ctr)[0]
