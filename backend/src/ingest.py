import os
from requests import Session
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

def _fetch_with_proxy(video_id: str) -> str | None:
    session = Session()
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
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

    return " ".join(chunk.text for chunk in transcript)


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

    # Layer 2: proxy fetch with hard 3 second wall — kills it regardless of library internals
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_with_proxy, video_id)
            text = future.result(timeout=3)  # hard 3 second wall, no exceptions
        return text, None

    except TimeoutError:
        print("Proxy fetch timed out after 3 seconds, fallback needed")
        return None, "fallback"

    except Exception as e:
        print("Proxy fetch failed, fallback needed:", e)
        return None, "fallback"