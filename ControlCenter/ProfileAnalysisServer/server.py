# server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import os
import cv2 as cv

app = FastAPI(title="Local Image Server")

# Allow access only from localhost (you can change later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_DIR = "../../../HDF5Test/SO298_298-10-1_PISCO2_20230422-2334_Results/Images/"

@app.get("/image/{index}")
async def get_image(index: int):
    """Serve an image file by filename."""
    file_path = os.path.join(IMAGE_DIR, os.listdir(IMAGE_DIR)[index])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    img = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
    img = cv.resize(img, None, fx=0.5, fy=0.5)

    # Encode back to PNG for sending
    success, encoded = cv.imencode(".png", img)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode image")

    return Response(content=encoded.tobytes(), media_type="image/png")

@app.get("/")
async def root():
    return {"message": "Image server is running", "available_images": os.listdir(IMAGE_DIR)}

# Run with: uvicorn server:app --host 127.0.0.1 --port 8000

