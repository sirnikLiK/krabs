import copy
import uvicorn
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import base64

app = FastAPI()

class PointsRequest(BaseModel):
   type: str
   number: int
   count: int
   x: int
   y: int

points = []
copter_task = None

@app.post("/points")
async def post_points(request: List[PointsRequest]):
   global points
   points = []
   for point in request:
       points.append({"type": point.type, "number": point.number, "count": point.count, "x": point.x, "y": point.y})
   return {"status": "OK", "detail": None}

@app.get("/points")
async def get_points():
   print(points)
   return {"status": "OK", "detail": points}

@app.post("/copter_task")
async def post_copter_task(request: PointsRequest):
   global copter_task
   copter_task = request
   return {"status": "OK", "detail": None}

@app.get("/copter_task")
async def get_copter_task():
   global copter_task
   return {"status": "OK", "detail": copter_task}

class ImageRequest(BaseModel):
   original: str
   processed: str

last_images = None

@app.post("/images")
async def post_images(request: ImageRequest):
   global last_images
   last_images = request
   return {"status": "OK", "detail": None}

@app.get("/images")
async def get_images():
   global last_images
   return {"status": "OK", "detail": last_images}

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)