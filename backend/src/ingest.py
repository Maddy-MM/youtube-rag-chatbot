from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def get_transcript(video_id: str) -> str:
    try:
        ytt_api = YouTubeTranscriptApi()

        # Try English first
        try:
            transcript = ytt_api.fetch(video_id, languages=["en"])
        except Exception:
            # Fallback: get best available transcript
            transcript = ytt_api.fetch(video_id)

        return " ".join(chunk.text for chunk in transcript)

    except TranscriptsDisabled:
        return ""
    except Exception as e:
        print("Transcript error:", e)
        return ""