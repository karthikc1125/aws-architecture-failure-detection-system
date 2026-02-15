from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router

app = FastAPI(title="Failure-Driven AWS Architect", version="1.0")

app.include_router(router)

# Serve Frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')

@app.get("/analyze")
def read_analyze():
    return FileResponse('frontend/analyze.html')

@app.get("/methodology")
def read_methodology():
    return FileResponse('frontend/methodology.html')

@app.get("/settings")
def read_settings():
    return FileResponse('frontend/settings.html')

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    import sys

    def open_browser():
        """Opens the browser after a short delay to ensure server is up."""
        time.sleep(1.5)
        print("🌍 Opening browser at http://localhost:8000")
        webbrowser.open("http://localhost:8000")

    # Start browser launch in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n🛑 SafeCloud Server Stopped by User.")
        sys.exit(0)
