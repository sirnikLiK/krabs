import copy

import uvicorn
import time
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()
frame_count = 0
start_time = time.time()
tasks = []
points = []


class PointsRequest(BaseModel):
    type: str
    number: int
    count: int
    x: int
    y: int


@app.post("/task")
async def post_task(request: List[str]):
    global tasks
    tasks = request
    return {"status": "OK", "detail": None}


@app.post("/points")
async def post_points(request: List[PointsRequest]):
    global points
    points = []
    for point in request:
        points.append({"type": point.type, "number": point.number, "count": point.count, "x": point.x, "y": point.y})
    return {"status": "OK", "detail": None}


@app.get("/task")
async def get_task():
    global tasks
    tasks_copy = copy.deepcopy(tasks)
    tasks = []
    return {"status": "OK", "detail": tasks_copy}


@app.get("/points")
async def get_points():
    print(points)
    return {"status": "OK", "detail": points}


@app.post("/point")
async def visit_point(number: int):
    for i in range(len(points)):
        if points[i]["number"] == number:
            points[i]["count"] += 1
            return {"status": "OK", "detail": None}
    return {"status": "ER", "detail": "Number not found"}


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    global frame_count, start_time
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        fps = frame_count / elapsed_time
    else:
        fps = 0

    return JSONResponse(content={"fps": round(fps, 2)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
