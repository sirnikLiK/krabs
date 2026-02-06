# это на машинке, чтоб кидать на сервер, uvicorn camera:app --host 0.0.0.0 --port 8000 чтоб сервер запустить camera.py

import cv2
import asyncio
import httpx

cap = cv2.VideoCapture("/dev/video0")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

last_state = None

async def send_video(client: httpx.AsyncClient):
    global last_state
    while True:
        ret, frame = cap.read()
        if last_state:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, jpeg = cv2.imencode('.jpg', gray_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        else:
            _, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        try:
            await client.post("http://192.168.161.72:8000/upload", content=jpeg.tobytes())
        except Exception as e:
            print("Fail:", e)
        await asyncio.sleep(1/30)

async def poll_motor_state(client: httpx.AsyncClient):
    global last_state
    last_state = None
    while True:
        resp = await client.get("http://192.168.161.72:8000/get_state")
        data = resp.json()
        motor_on = data.get("motor_on", False)
        if motor_on != last_state:
            print("button")
            last_state = motor_on
        await asyncio.sleep(0.2)

async def main():
    async with httpx.AsyncClient(timeout=2.0) as client:
        await asyncio.gather(
            send_video(client),
            poll_motor_state(client)
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        cap.release()
