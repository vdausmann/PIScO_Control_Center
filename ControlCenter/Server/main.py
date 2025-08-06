import uvicorn

if __name__ == "__main__":
    # uvicorn.run("Backend.server:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("Backend.server:app", host="localhost", port=8000, reload=True)
