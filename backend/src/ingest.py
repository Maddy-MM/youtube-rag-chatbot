import os
from requests import Session
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

def get_transcript(video_id: str) -> tuple[str | None, str | None]:

    # Layer 1: direct fetch (no proxy) — works fine until YouTube blocks the cloud IP
    try:
        ytt_api = YouTubeTranscriptApi()
        try:
            transcript = ytt_api.fetch(video_id, languages=["en"])
        except Exception:
            transcript = ytt_api.fetch(video_id)

        text = " ".join(chunk.text for chunk in transcript)
        return text, None

    except Exception as e:
        print("Direct fetch failed, trying proxy:", e)

    # Layer 2: proxy fetch with 3 second timeout to avoid long waits on failure
    try:
        session = Session()
        session.request = lambda method, url, **kwargs: Session.request(
            session, method, url, timeout=3, **kwargs
        )

        ytt_api_proxy = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=os.environ["WEBSHARE_USER"],
                proxy_password=os.environ["WEBSHARE_PASS"],
            ),
            http_client=session
        )

        try:
            transcript = ytt_api_proxy.fetch(video_id, languages=["en"])
        except Exception:
            transcript = ytt_api_proxy.fetch(video_id)

        text = " ".join(chunk.text for chunk in transcript)
        return text, None

    except Exception as e:
        print("Proxy fetch failed, fallback needed:", e)
        return None, "fallback"  # Layer 3 — triggers manual paste UI in frontend