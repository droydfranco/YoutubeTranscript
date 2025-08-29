# service/main.py
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi

# create a FastAPI web app
app = FastAPI()

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
        fetched = api.fetch(video_id, languages=languages, preserve_formatting=preserve_formatting)
        # convert transcript into plain JSON
        return JSONResponse(content=[s.__dict__ for s in fetched])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
