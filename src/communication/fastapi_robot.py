from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import threading
import time

# --- DATA MODELS ---
class MoveCommand(BaseModel):
    linear_speed: float
    angular_speed: float
    duration: float

class RobotStatus(BaseModel):
    state: str
    battery: float
    current_speed: float

# --- APP SETUP ---
app = FastAPI(title="Robot API", description="Control interface for ATS Token Robot")

# Global Robot State (Mock)
robot_state = {
    "state": "IDLE",
    "battery": 100.0,
    "speed": 0.0
}

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Robot Control API is running. Go to /docs for UI."}

@app.get("/status", response_model=RobotStatus)
def get_status():
    """Returns the current state of the robot."""
    return {
        "state": robot_state["state"],
        "battery": robot_state["battery"],
        "current_speed": robot_state["speed"]
    }

@app.post("/move")
def send_move_command(cmd: MoveCommand):
    """Sends a movement command to the robot."""
    if float(robot_state["battery"]) < 5:
        raise HTTPException(status_code=400, detail="Low battery! Cannot move.")
        
    print(f"Executing Move: Linear={cmd.linear_speed}, Angular={cmd.angular_speed}, Time={cmd.duration}")
    
    # Simulate movement logic
    robot_state["state"] = "MOVING"
    robot_state["speed"] = cmd.linear_speed
    
    # In a real robot, you wouldn't block here, but start a background thread
    # For this example, we just acknowledge receipt
    return {"status": "Command accepted", "executed_command": cmd}

@app.post("/stop")
def emergency_stop():
    """Immediately stops the robot."""
    robot_state["state"] = "IDLE"
    robot_state["speed"] = 0.0
    print("EMERGENCY STOP TRIGGERED")
    return {"status": "Robot stopped"}

# --- RUNNER ---
def start_server():
    """Function to start server programmatically"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # You can run this file directly: python3 fastapi_robot.py
    print("Starting Robot API...")
    # standard way: uvicorn.run("fastapi_robot:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
