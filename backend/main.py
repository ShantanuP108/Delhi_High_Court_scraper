# backend/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from scraper import fetch_cause_lists_for_date

app = FastAPI(title="Delhi High Court Cause List API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOADS_FOLDER = "downloads"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Delhi High Court Cause List API is running!"}

# ✅ CORRECT ENDPOINT NAME — must match frontend
@app.post("/api/download_all_cause_lists")
async def download_all_cause_lists(request: Request):
    data = await request.json()
    user_date = data.get("date")  # e.g., "17-10-2025"

    if not user_date:
        return JSONResponse({"error": "Date (DD-MM-YYYY) is required"}, status_code=400)

    try:
        files = fetch_cause_lists_for_date(user_date, DOWNLOADS_FOLDER)
        if not files:
            return JSONResponse({
                "warning": f"No cause lists found for {user_date}. Try a recent or future date."
            }, status_code=404)

        filenames = [os.path.basename(f) for f in files]
        return JSONResponse({"downloaded_files": filenames})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download/{filename}")
def serve_pdf(filename: str):
    filepath = os.path.join(DOWNLOADS_FOLDER, filename)
    if not os.path.exists(filepath):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(filepath, media_type="application/pdf", filename=filename)