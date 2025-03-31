import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

# ✅ Constants
DATA_PATH = "data/seo_data.csv"
MODEL_PATH = "models/seo_model.pkl"

def train_models():
    """Trains the model using SEO data."""
    print("\n🔍 Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # ✅ Validate required columns
    required_columns = ["difficulty", "ctr"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        print("💡 Run SEO analysis to generate the required fields.")
        return

    # ✅ Model Training
    print(f"Dataset columns: {df.columns}")

    # ✅ Prepare features and target
    X = df[["difficulty", "ctr"]]
    y = df["position"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # ✅ Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_models()
