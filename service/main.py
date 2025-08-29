# service/main.py
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi

# Proxy configs from the library
from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig

app = FastAPI(title="YouTube Transcript API (Render wrapper)")

# CORS (adjust allow_origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_api_from_env() -> YouTubeTranscriptApi:
    """
    Build a YouTubeTranscriptApi client using proxy credentials from env vars if present.
    Priority:
      1) Webshare rotating residential proxies (WEBSHARE_USERNAME / WEBSHARE_PASSWORD)
      2) Generic HTTP/HTTPS proxies (GENERIC_HTTP_PROXY / GENERIC_HTTPS_PROXY)
      3) No proxy
    """
    ws_user = os.getenv("WEBSHARE_USERNAME")
    ws_pass = os.getenv("WEBSHARE_PASSWORD")
    if ws_user and ws_pass:
        countries_env = os.getenv("WEBSHARE_COUNTRIES", "")
        countries = [c.strip().lower() for c in countries_env.split(",") if c.strip()]
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=ws_user,
                proxy_password=ws_pass,
                filter_ip_locations=countries or None,
            )
        )

    http_proxy = os.getenv("GENERIC_HTTP_PROXY")
    https_proxy = os.getenv("GENERIC_HTTPS_PROXY")
    if http_proxy or https_proxy:
        return YouTubeTranscriptApi(
            proxy_config=GenericProxyConfig(
                http_url=http_proxy, https_url=https_proxy
            )
        )

    # Fallback: no proxy (likely blocked on cloud IPs)
    return YouTubeTranscriptApi()

@app.get("/")
def home():
    # Friendly root -> docs
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
        api = make_api_from_env()
        fetched = api.fetch(
            video_id,
            languages=languages,
            preserve_formatting=preserve_formatting,
        )
        # Convert to plain JSON
        return JSONResponse(content=[s.__dict__ for s in fetched])
    except Exception as e:
        # Bubble up message from library (e.g., IP blocked, no transcript, etc.)
        raise HTTPException(status_code=400, detail=str(e))
