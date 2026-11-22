"""
Avatar-video provider.

Turns a topic's explainer script into an avatar video. The real provider path
calls HeyGen's API when HEYGEN_API_KEY is configured; otherwise a deterministic
fallback completes the job with the script so development and tests never
depend on an external render service.
"""

import os

from ai.services.llm import chat_text


def generate_script(topic) -> str:
    """
    Produce a short presenter script for a topic. Uses the LLM when available,
    otherwise a readable deterministic script assembled from the topic fields.
    """
    fallback = (
        f"Today we're learning about {topic.title}. "
        f"{topic.description or 'Here is a short overview of the topic.'}"
    )
    prompt = (
        "Write a short (60-90 second) avatar-presenter script explaining the "
        "topic below to a school student. Two or three natural spoken sentences, "
        "plain and friendly. No stage directions, just the spoken lines.\n\n"
        f"Topic: {topic.title}\nDescription: {topic.description or 'N/A'}"
    )
    try:
        script = chat_text(prompt, temperature=0.6)
        if script and script.strip():
            return script.strip()
    except Exception:  # noqa: BLE001 - fall back to deterministic script
        pass
    return fallback


def _heygen_render(job) -> str:
    """
    Submit the job's script to HeyGen as an async avatar render.

    Renders are asynchronous; HeyGen returns a video_id immediately and the URL
    only after processing. We surface the video_id on the job (as provider
    metadata) and leave job.video_url for the job poller/webhook to fill in.
    """
    import requests  # loaded lazily so the fallback path never needs it

    api_key = os.getenv("HEYGEN_API_KEY")
    avatar_id = os.getenv("HEYGEN_AVATAR_ID") or "S39lCKvGzyry1dPlLIRa"
    voice_id = os.getenv("HEYGEN_VOICE_ID") or ""
    url = "https://api.heygen.com/v2/video/generate"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    voice = {"type": "text", "input_text": job.script}
    if voice_id:
        voice["voice_id"] = voice_id
    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "avatar_id": avatar_id},
                "voice": voice,
            }
        ],
        "dimension": {"width": 1280, "height": 720},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    meta = dict(job.provider_meta or {})
    meta["heygen_video_id"] = (data.get("data") or {}).get("video_id", "")
    job.provider_meta = meta
    return ""


def render_video(job) -> str:
    """
    Hand the job's script to an avatar provider and return the provider name.
    Leaves job.video_url empty when the render is async (real HeyGen); the job
    poller fills it in once the render completes.
    """
    if os.getenv("HEYGEN_API_KEY"):
        job.video_url = _heygen_render(job)
        return "heygen"
    # Fallback: no real provider configured — the job stays complete with the
    # script ready to render when a key is added. Honest: no fake video URL.
    return "fallback"
