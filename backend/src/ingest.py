import os
from requests import Session
from requests.adapters import HTTPAdapter
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

def get_transcript(video_id: str) -> tuple[str | None, str | None]:

    # Layer 1: direct fetch (no proxy)
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

    # Layer 2: proxy fetch — no retries, 3 second timeout, fail fast
    try:
        session = Session()

        # Disable all retries so it fails immediately instead of retrying multiple times
        adapter = HTTPAdapter(max_retries=0)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Hard timeout of 3 seconds per request
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
        return None, "fallback"