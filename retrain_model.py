
import pandas as pd
import pickle
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

def retrain():
    print("Loading dataset...")
    df = pd.read_csv("model/phishing.csv")
    
    # Columns 1 to 30 are features (Index is 0), class is 31 (last)
    # Check if 'Index' is present
    if "Index" in df.columns:
        X = df.iloc[:, 1:-1] # features
        y = df.iloc[:, -1]   # class
    else:
        # Fallback if index column is missing
        X = df.iloc[:, 0:-1]
        y = df.iloc[:, -1]

    print(f"Training with {X.shape[1]} features on {X.shape[0]} samples.")
    
    gbc = GradientBoostingClassifier()
    gbc.fit(X, y)
    
    print("Saving model to model.pkl...")
    with open("model.pkl", "wb") as f:
        pickle.dump(gbc, f)
    
    print("Done.")

if __name__ == "__main__":
    retrain()
