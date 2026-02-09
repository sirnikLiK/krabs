import requests
import time
import sys

SERVER_URL = "http://localhost:8000"

def get_status():
    try:
        response = requests.get(f"{SERVER_URL}/status")
        if response.status_code == 200:
            print(f"STATUS: {response.json()}")
        else:
            print(f"Error getting status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to robot. Is the server running?")

def move_robot(linear, angular, duration):
    payload = {
        "linear_speed": linear,
        "angular_speed": angular,
        "duration": duration
    }
    try:
        response = requests.post(f"{SERVER_URL}/move", json=payload)
        if response.status_code == 200:
            print(f"MOVE: {response.json()}")
        else:
            print(f"Error sending move: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to robot.")

def stop_robot():
    try:
        response = requests.post(f"{SERVER_URL}/stop")
        print(f"STOP: {response.json()}")
    except:
        print("Error stopping.")

def main():
    print("--- ROBOT CLIENT ---")
    print("1. Get Status")
    print("2. Move Forward")
    print("3. Spin")
    print("4. Stop")
    print("5. Quit")
    
    while True:
        choice = input("Select command (1-5): ")
        
        if choice == '1':
            get_status()
        elif choice == '2':
            move_robot(1.0, 0.0, 2.0)
        elif choice == '3':
            move_robot(0.0, 90.0, 1.0)
        elif choice == '4':
            stop_robot()
        elif choice == '5':
            sys.exit()
        else:
            print("Invalid choice")
        print("-" * 20)

if __name__ == "__main__":
    main()
