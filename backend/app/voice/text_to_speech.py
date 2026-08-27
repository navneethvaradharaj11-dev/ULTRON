class TextToSpeechService:
    """Modular Text-To-Speech service interface."""

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text string into audio bytes."""
        return b"MOCK_ULTRON_AUDIO_STREAM"
