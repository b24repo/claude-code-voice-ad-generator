"""
Voice synthesis service with ElevenLabs integration.
Provides mock implementation for development, ready for live API integration.
"""

import logging
from typing import Optional
import base64
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceSynthesisResult:
    """Result of voice synthesis."""

    def __init__(
        self,
        audio_data: bytes,
        voice_id: str,
        duration_seconds: float,
        cost: float,
    ):
        self.audio_data = audio_data
        self.voice_id = voice_id
        self.duration_seconds = duration_seconds
        self.cost = cost


class VoiceSynthesizer:
    """Service for synthesizing voice audio from ad scripts."""

    # Voice profiles with characteristics
    VOICES = {
        "alloy": {
            "name": "Alloy",
            "description": "Neutral, clear voice - good for technical content",
            "gender": "unspecified",
            "accent": "american",
        },
        "echo": {
            "name": "Echo",
            "description": "Warm, friendly voice - great for consumer products",
            "gender": "male",
            "accent": "american",
        },
        "fable": {
            "name": "Fable",
            "description": "Energetic, young voice - perfect for dynamic brands",
            "gender": "female",
            "accent": "british",
        },
        "onyx": {
            "name": "Onyx",
            "description": "Deep, professional voice - ideal for luxury brands",
            "gender": "male",
            "accent": "american",
        },
        "nova": {
            "name": "Nova",
            "description": "Bright, modern voice - contemporary and engaging",
            "gender": "female",
            "accent": "american",
        },
    }

    # Cost per 1000 characters
    COST_PER_1K_CHARS = 0.10

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice synthesizer.

        Args:
            api_key: ElevenLabs API key (optional for mock mode)
        """
        self.api_key = api_key
        self.use_mock = not api_key

    async def synthesize(
        self,
        script: str,
        voice_id: str = "alloy",
        model: str = "eleven_monolingual_v1",
    ) -> VoiceSynthesisResult:
        """
        Synthesize voice audio from script text.

        Args:
            script: Text to synthesize
            voice_id: Voice to use (alloy, echo, fable, onyx, nova)
            model: Voice model to use

        Returns:
            VoiceSynthesisResult with audio data and cost

        Raises:
            ValueError: If voice_id is invalid
            APIError: If synthesis fails
        """
        if voice_id not in self.VOICES:
            raise ValueError(f"Invalid voice ID: {voice_id}. Valid: {list(self.VOICES.keys())}")

        if not script or len(script.strip()) < 10:
            raise ValueError("Script must be at least 10 characters")

        # Calculate cost
        cost = self._calculate_cost(script)

        # Use mock or real API
        if self.use_mock:
            return self._synthesize_mock(script, voice_id, cost)
        else:
            return await self._synthesize_elevenlabs(script, voice_id, model, cost)

    def _synthesize_mock(
        self, script: str, voice_id: str, cost: float
    ) -> VoiceSynthesisResult:
        """
        Generate mock audio data for development.
        In production, this would call ElevenLabs API.
        """
        logger.info(f"Synthesizing voice (mock): {voice_id}, {len(script)} chars, cost: ${cost:.3f}")

        # Create simple WAV header (mock audio)
        # In production: real audio data from ElevenLabs
        mock_audio = self._create_mock_wav(script, voice_id)

        # Estimate duration (roughly 120 words per minute = 2 chars per second)
        duration_seconds = len(script) / 150

        return VoiceSynthesisResult(
            audio_data=mock_audio,
            voice_id=voice_id,
            duration_seconds=duration_seconds,
            cost=cost,
        )

    async def _synthesize_elevenlabs(
        self,
        script: str,
        voice_id: str,
        model: str,
        cost: float,
    ) -> VoiceSynthesisResult:
        """
        Call ElevenLabs API to synthesize voice.

        Ready for production integration when API key is provided.
        """
        import httpx

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": script,
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()

                audio_data = response.content
                duration_seconds = len(script) / 150

                logger.info(
                    f"Synthesized voice with ElevenLabs: {voice_id}, "
                    f"size: {len(audio_data)} bytes, cost: ${cost:.3f}"
                )

                return VoiceSynthesisResult(
                    audio_data=audio_data,
                    voice_id=voice_id,
                    duration_seconds=duration_seconds,
                    cost=cost,
                )

        except httpx.HTTPError as e:
            logger.error(f"ElevenLabs API error: {e}")
            raise RuntimeError(f"Voice synthesis failed: {e}")

    def _calculate_cost(self, script: str) -> float:
        """Calculate cost based on script length."""
        char_count = len(script)
        return (char_count / 1000) * self.COST_PER_1K_CHARS

    def _create_mock_wav(self, script: str, voice_id: str) -> bytes:
        """
        Create minimal mock WAV file for development.

        In production, this would be replaced with real ElevenLabs audio.
        """
        # Minimal WAV header (44 bytes)
        sample_rate = 24000
        duration_seconds = len(script) / 150
        num_samples = int(sample_rate * duration_seconds)

        # WAV header
        wav_header = bytearray(44)

        # RIFF header
        wav_header[0:4] = b"RIFF"
        file_size = 36 + num_samples * 2
        wav_header[4:8] = file_size.to_bytes(4, "little")
        wav_header[8:12] = b"WAVE"

        # fmt subchunk
        wav_header[12:16] = b"fmt "
        wav_header[16:20] = (16).to_bytes(4, "little")  # Subchunk1Size
        wav_header[20:22] = (1).to_bytes(2, "little")  # AudioFormat (PCM)
        wav_header[22:24] = (1).to_bytes(2, "little")  # NumChannels
        wav_header[24:28] = sample_rate.to_bytes(4, "little")  # SampleRate
        wav_header[28:32] = (sample_rate * 2).to_bytes(4, "little")  # ByteRate
        wav_header[32:34] = (2).to_bytes(2, "little")  # BlockAlign
        wav_header[34:36] = (16).to_bytes(2, "little")  # BitsPerSample

        # data subchunk
        wav_header[36:40] = b"data"
        wav_header[40:44] = (num_samples * 2).to_bytes(4, "little")

        # Add mock audio data (silent)
        mock_audio_data = b"\x00" * (num_samples * 2)

        return bytes(wav_header) + mock_audio_data

    def get_voices(self) -> dict:
        """Get available voices and their characteristics."""
        return self.VOICES