class SpeechToTextService:
    """Modular Speech-To-Text service interface."""

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe raw audio bytes to text string."""
        return "ULTRON Voice command parsed successfully."
