import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train():
    print("Step 1: Imports finished") # Moved print to after imports implicitly ifcalled in __main__
    
    # Load dataset
    print("Step 2: Loading data...")
    data_path = 'Missions_log.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    df = pd.read_csv(data_path, sep=';')
    print(f"Step 3: Data loaded, shape: {df.shape}")
    
    if len(df) > 2000:
        print("Sampling 2,000 rows for faster training...")
        df = df.sample(2000, random_state=42)
    
    # Preprocess
    print("Step 4: Preprocessing...")
    df['Success'] = (df['Mission status'] == 'Completed').astype(int)
    
    X = df[['Evacuees', 'Number of debris', 'Level of destruction', 'HP Tire']]
    y = df['Success']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Step 5: Training model...")
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression()
    model.fit(X_train, y_train)
    print("Step 6: Training finished")
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    
    # Save Model
    print("Step 7: Saving model...")
    joblib.dump(model, 'model.joblib')
    print("Done!")

if __name__ == "__main__":
    train()
