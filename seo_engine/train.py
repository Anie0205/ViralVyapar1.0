import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error
import joblib

DATA_PATH = os.path.join("data", "seo_data.csv")
MODEL_DIR = "models"

# Ensure models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def train_models():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print("Dataset columns:", df.columns)

    # Features and target variables
    X = df[["difficulty", "ctr"]]
    y_ctr = df["ctr"]
    y_difficulty = (df["difficulty"] > 50).astype(int)

    # Split into training and testing sets
    X_train, X_test, y_ctr_train, y_ctr_test = train_test_split(X, y_ctr, test_size=0.2, random_state=42)
    _, _, y_difficulty_train, y_difficulty_test = train_test_split(X, y_difficulty, test_size=0.2, random_state=42)

    # --- CTR Prediction Model ---
    print("Training CTR Prediction Model...")
    ctr_model = LinearRegression()
    ctr_model.fit(X_train, y_ctr_train)
    y_ctr_pred = ctr_model.predict(X_test)
    mse = mean_squared_error(y_ctr_test, y_ctr_pred)
    print(f"CTR Model MSE: {mse:.4f}")

    # Save the CTR model
    joblib.dump(ctr_model, os.path.join(MODEL_DIR, "ctr_model.pkl"))

    # --- Keyword Difficulty Estimation Model ---
    print("Training Keyword Difficulty Estimation Model...")

    if len(set(y_difficulty_train)) > 1:
        difficulty_model = LogisticRegression(max_iter=1000)
        difficulty_model.fit(X_train, y_difficulty_train)

        y_difficulty_pred = difficulty_model.predict(X_test)
        accuracy = (y_difficulty_pred == y_difficulty_test).mean()
        print(f"Difficulty Model Accuracy: {accuracy:.4f}")

        # Save the difficulty model
        joblib.dump(difficulty_model, os.path.join(MODEL_DIR, "keyword_difficulty.pkl"))
    else:
        print("❗ Skipping difficulty model training due to single-class issue.")

    print(" Models trained and saved successfully.")

# Only run if executed directly
if __name__ == "__main__":
    train_models()
