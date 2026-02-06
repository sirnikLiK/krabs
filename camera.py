# Это  на сервере (компе)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio

app = FastAPI()

latest_frame: bytes | None = None
frame_event = asyncio.Event()

@app.post("/upload")
async def upload_frame(request: Request):
    global latest_frame
    latest_frame = await request.body()
    frame_event.set()
    frame_event.clear()
    return {"status": "ok"}

async def mjpeg_generator():
    while True:
        await frame_event.wait()
        if latest_frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n"
            )

@app.get("/video", response_class=HTMLResponse)
async def video_page():
    return """
    <html>
    <body style="margin:0; display:flex; flex-direction:column; align-items:center; padding:20px;">
        <img src="/stream" style="width:100%; max-width:800px; border:1px solid #ccc;">
        <br>
        <button onclick="fetch('/cmd')" style="padding:12px 24px; font-size:18px;">Send Command</button>
    </body>
    </html>
    """

@app.get("/stream")
async def stream():
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/cmd")
async def cmd():
    print("✅ Button pressed – command received!")
    return {"status": "executed"}
