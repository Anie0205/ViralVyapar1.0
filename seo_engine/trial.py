import pandas as pd

# Load and display the first few rows of the CSV
df = pd.read_csv("data/seo_data.csv")
print(df.head())
print(df.columns)
