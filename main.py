import os
import webbrowser
import threading
import time
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent.resolve()

    return base_path / relative_path

# --- Configuration ---
SCREENSHOTS_DIR = Path(r"C:\Users\User\OneDrive\Pictures\Screenshots")

# Ensure directory exists for safety (though user says it exists)
if not SCREENSHOTS_DIR.exists():
    print(f"Warning: Screenshot directory not found at {SCREENSHOTS_DIR}")

app = FastAPI(title="Screenshot Cleaner API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Logic Layer: ScreenshotManager ---
class ScreenshotManager:
    def __init__(self, directory: Path):
        self.directory = directory

    def list_screenshots(self) -> List[str]:
        """Returns a list of image filenames in the directory."""
        if not self.directory.exists():
            return []
        extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
        return [
            f.name for f in self.directory.iterdir() 
            if f.is_file() and f.suffix.lower() in extensions
        ]

    def get_file_size(self, filename: str) -> int:
        """Returns the size of the file in bytes."""
        file_path = self.directory / filename
        if file_path.exists() and file_path.is_file():
            return file_path.stat().st_size
        return 0

    def delete_screenshot(self, filename: str) -> bool:
        """Deletes the screenshot and returns success status."""
        file_path = self.directory / filename
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")
        return False

# Instantiate the manager
manager = ScreenshotManager(SCREENSHOTS_DIR)

# Global stats (simple in-memory for this app)
class Stats:
    total_saved_space = 0

stats = Stats()

# --- API Layer: APIHandler ---
class ScreenshotInfo(BaseModel):
    filename: str
    size: int

class StatsResponse(BaseModel):
    totalSavedSpace: int

class BatchDeleteRequest(BaseModel):
    filenames: List[str]

@app.get("/screenshots", response_model=List[ScreenshotInfo])
async def get_screenshots():
    """Returns a list of all screenshots with their sizes."""
    files = manager.list_screenshots()
    return [
        ScreenshotInfo(filename=f, size=manager.get_file_size(f)) 
        for f in files
    ]

@app.delete("/screenshots/{filename}")
async def delete_screenshot(filename: str):
    """Deletes a screenshot and updates cumulative stats."""
    size = manager.get_file_size(filename)
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File not found or empty"
        )
    
    success = manager.delete_screenshot(filename)
    if success:
        stats.total_saved_space += size
        return {"success": True, "deletedSize": size}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete file"
        )

@app.post("/screenshots/batch-delete")
async def batch_delete_screenshots(request: BatchDeleteRequest):
    """Deletes multiple screenshots and returns total size deleted."""
    total_deleted_size = 0
    failed_files = []

    for filename in request.filenames:
        size = manager.get_file_size(filename)
        if size > 0:
            if manager.delete_screenshot(filename):
                total_deleted_size += size
            else:
                failed_files.append(filename)
        else:
            failed_files.append(filename)

    stats.total_saved_space += total_deleted_size
    
    return {
        "success": True, 
        "deletedSize": total_deleted_size,
        "failedFiles": failed_files
    }

@app.post("/shutdown")
async def shutdown():
    """Shuts down the application."""
    def kill_process():
        time.sleep(1)
        os._exit(0)
    
    threading.Thread(target=kill_process, daemon=True).start()
    return {"message": "Shutting down..."}

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Returns the total space saved so far."""
    return StatsResponse(totalSavedSpace=stats.total_saved_space)

@app.get("/")
async def read_index():
    index_path = get_resource_path("index.html")
    return FileResponse(index_path)

# Serve the screenshots as static files for previewing
# Access via: http://localhost:8000/images/filename.png
app.mount("/images", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="images")

def open_browser():
    """Opens the browser after a short delay to ensure server is ready."""
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    # Start the browser opening thread
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
