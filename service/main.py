# service/main.py
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI(title="YouTube Transcript API (wrapper)")

# (Optional) CORS so you can call this from a browser/app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # replace "*" with your domain(s) for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    # Friendly root: send users to interactive docs
    return RedirectResponse(url="/docs")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/transcript")
def transcript(
    video_id: str = Query(..., description="YouTube video ID (not full URL)"),
    languages: Optional[List[str]] = Query(default=["en"]),
    preserve_formatting: bool = False,
):
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(
            video_id,
            languages=languages,
            preserve_formatting=preserve_formatting,
        )
        # Convert to plain JSON
        return JSONResponse(content=[s.__dict__ for s in fetched])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
