import sys
import urllib.request
import joblib
import pandas as pd
import os

def get_mission_details():
    url = "http://172.16.65.123:5200/"
    try:
        print(f"Fetching mission details from {url}...")
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read().decode('utf-8').strip()
            # Expected response: "evacuees;debris;destruction"
            # The task says: "количество человек от 1 до 10... количество завалов от 1 до 4... уровень разрушенности от 0.0 до 1.0"
            parts = data.split(';')
            if len(parts) == 3:
                evacuees = int(parts[0])
                debris = int(parts[1])
                destruction = float(parts[2])
                print(f"Data received: Evacuees={evacuees}, Debris={debris}, Destruction={destruction}")
                return evacuees, debris, destruction
            else:
                print("Unexpected data format from server.")
    except Exception as e:
        print(f"Error fetching mission details: {e}")
    
    # Fallback to manual input
    print("\nPlease enter mission details manually:")
    evacuees = int(input("Evacuees (1-10): "))
    debris = int(input("Number of debris (1-4): "))
    destruction = float(input("Level of destruction (0.0-1.0): "))
    return evacuees, debris, destruction

def run_decision():
    # Load Model
    model_path = 'model.joblib'
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found. Please run train_model.py first.")
        # Minimal heuristic if model is missing (based on general trends observed)
        print("Using simplified heuristic since model.joblib is missing...")
        model = None
    else:
        model = joblib.load(model_path)

    # 1. Get current wheel state
    try:
        current_hp = float(input("Enter current tire condition (0-200): "))
    except ValueError:
        print("Invalid input. Using 0.")
        current_hp = 0

    # 2. Get mission details
    evacuees, debris, destruction = get_mission_details()

    def predict_success(hp):
        if model:
            # Features: ['Evacuees', 'Number of debris', 'Level of destruction', 'HP Tire']
            input_data = pd.DataFrame([[evacuees, debris, destruction, hp]], 
                                     columns=['Evacuees', 'Number of debris', 'Level of destruction', 'HP Tire'])
            prediction = model.predict(input_data)[0]
            return prediction == 1
        else:
            # Heuristic: missions usually fail if HP < (Evacuees * Debris * Destruction * Constant)
            # This is just a fallback to make the script functional without the model file.
            threshold = (evacuees * 5) + (debris * 10) + (destruction * 50)
            return hp >= threshold

    # 3. Decision logic
    success_current = predict_success(current_hp)
    success_ordinary = predict_success(100)
    success_reinforced = predict_success(200)

    print("\n--- Mission Forecast ---")
    print(f"Current HP ({current_hp}): {'Completed' if success_current else 'Failed'}")
    
    # "сколько он простоит еще" - estimate how many HP are above the fail threshold
    # We can check a range of HP to find the threshold
    threshold_hp = 0
    for test_hp in range(0, 201, 5):
        if predict_success(test_hp):
            threshold_hp = test_hp
            break
    
    durability = current_hp - threshold_hp
    if durability > 0:
        print(f"Remaining durability: {durability:.1f} HP above success threshold.")
    else:
        print(f"Insufficient durability: Need {-durability:.1f} more HP for success.")

    # Final Recommendation
    if success_current:
        print("\nRecommendation: Оставить текущие")
    elif success_ordinary:
        print("\nRecommendation: Обычные")
    else:
        print("\nRecommendation: Усиленные")

if __name__ == "__main__":
    run_decision()
