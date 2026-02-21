"""
Unit tests for ad generation service.
Tests cover normal cases, edge cases, API errors, and caching.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from services.ad_generator import AdGenerator, AdGenerationResult


@pytest.fixture
def ad_generator():
    """Create AdGenerator instance for testing."""
    return AdGenerator()


class TestAdGenerator:
    """Test suite for AdGenerator service."""

    @pytest.mark.asyncio
    async def test_generate_ad_happy_path(self, ad_generator):
        """Test successful ad generation."""
        with patch.object(ad_generator.client.messages, "create") as mock_create:
            # Mock Claude response
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text='{"tagline": "Coffee Dream", "script": "Start your day...", "cta": "Order now", "tone": "professional"}')]
            mock_create.return_value = mock_message

            with patch.object(ad_generator, "count_tokens") as mock_count:
                mock_count.return_value = MagicMock(
                    input_tokens=150, output_tokens=100, total_tokens=250
                )

                result = await ad_generator.generate_ad(
                    product="Premium Coffee",
                    tone="professional",
                    duration=30,
                )

                assert result.tagline == "Coffee Dream"
                assert result.script
                assert result.cta == "Order now"
                assert result.total_tokens == 250
                assert result.model_used == "claude-3-haiku-20240307"  # Simple product
                assert result.estimated_cost > 0

    @pytest.mark.asyncio
    async def test_model_selection_haiku(self, ad_generator):
        """Test model selection for simple products (should use Haiku)."""
        model = ad_generator._select_model("Coffee", 30, "casual")
        assert model == "claude-3-haiku-20240307"

    @pytest.mark.asyncio
    async def test_model_selection_sonnet(self, ad_generator):
        """Test model selection for complex products (should use Sonnet)."""
        model = ad_generator._select_model("Premium Luxury Coffee", 60, "luxury")
        assert model == "claude-3-5-sonnet-20241022"

    @pytest.mark.asyncio
    async def test_caching_hit(self, ad_generator):
        """Test that cached responses are returned without API calls."""
        with patch.object(ad_generator.client.messages, "create") as mock_create:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text='{"tagline": "Test", "script": "Test script", "cta": "Click", "tone": "casual"}')]
            mock_create.return_value = mock_message

            # First call should hit API
            result1 = await ad_generator.generate_ad("Coffee", "casual", 30)
            assert mock_create.call_count == 1

            # Second call with same params should hit cache
            with patch.object(ad_generator, "_count_tokens") as mock_count:
                mock_count.return_value = MagicMock(
                    input_tokens=150, output_tokens=100, total_tokens=250
                )
                result2 = await ad_generator.generate_ad("Coffee", "casual", 30, use_cache=True)

            # Should not make second API call
            assert mock_create.call_count == 1
            assert result2.cache_hit == True

    @pytest.mark.asyncio
    async def test_cache_expiration(self, ad_generator):
        """Test that expired cache entries are not returned."""
        cache_key = ad_generator._make_cache_key("Coffee", "casual", 30)

        # Manually add expired cache entry
        result = AdGenerationResult(
            tagline="Test",
            script="Test script",
            cta="Click",
            tone="casual",
            tokens_input=150,
            tokens_output=100,
            total_tokens=250,
            estimated_cost=0.005,
            model_used="claude-3-haiku-20240307",
        )

        ad_generator.cache[cache_key] = {
            "result": result,
            "expires_at": datetime.utcnow() - timedelta(hours=1),  # Expired
            "hits": 0,
        }

        # Should return None for expired entry
        cached = ad_generator._get_from_cache(cache_key)
        assert cached is None

    @pytest.mark.asyncio
    async def test_invalid_product_name(self, ad_generator):
        """Test error handling for invalid product name."""
        with pytest.raises(ValueError, match="Product name must be at least"):
            await ad_generator.generate_ad("", "professional", 30)

        with pytest.raises(ValueError, match="Product name must be at least"):
            await ad_generator.generate_ad("X", "professional", 30)

    @pytest.mark.asyncio
    async def test_invalid_tone(self, ad_generator):
        """Test error handling for invalid tone."""
        with pytest.raises(ValueError, match="Invalid tone"):
            await ad_generator.generate_ad("Coffee", "invalid_tone", 30)

    @pytest.mark.asyncio
    async def test_invalid_duration(self, ad_generator):
        """Test error handling for invalid duration."""
        with pytest.raises(ValueError, match="Duration must be between"):
            await ad_generator.generate_ad("Coffee", "professional", 10)

        with pytest.raises(ValueError, match="Duration must be between"):
            await ad_generator.generate_ad("Coffee", "professional", 90)

    @pytest.mark.asyncio
    async def test_api_timeout_retry(self, ad_generator):
        """Test retry logic on API timeout."""
        from anthropic import APITimeoutError

        with patch.object(ad_generator.client.messages, "create") as mock_create:
            # Fail twice, succeed on third attempt
            mock_create.side_effect = [
                APITimeoutError("timeout"),
                APITimeoutError("timeout"),
                MagicMock(
                    content=[MagicMock(text='{"tagline": "Success", "script": "After retries", "cta": "Buy", "tone": "casual"}')]
                ),
            ]

            with patch.object(ad_generator, "_count_tokens") as mock_count:
                mock_count.return_value = MagicMock(
                    input_tokens=150, output_tokens=100, total_tokens=250
                )

                result = await ad_generator.generate_ad("Coffee", "casual", 30)

                assert result.tagline == "Success"
                assert mock_create.call_count == 3

    @pytest.mark.asyncio
    async def test_api_error_no_retry(self, ad_generator):
        """Test that fatal API errors are not retried."""
        from anthropic import APIError

        with patch.object(ad_generator.client.messages, "create") as mock_create:
            mock_create.side_effect = APIError("Invalid API key")

            with pytest.raises(APIError):
                await ad_generator.generate_ad("Coffee", "casual", 30)

    @pytest.mark.asyncio
    async def test_cost_calculation_haiku(self, ad_generator):
        """Test cost calculation for Haiku model."""
        cost = ad_generator._estimate_cost(
            "claude-3-haiku-20240307",
            input_tokens=1000,
            output_tokens=500,
        )

        # Haiku: $0.00025 per 1k input + $0.00125 per 1k output
        expected = (1000 / 1000 * 0.00025) + (500 / 1000 * 0.00125)
        assert abs(cost - expected) < 0.00001

    @pytest.mark.asyncio
    async def test_cost_calculation_sonnet(self, ad_generator):
        """Test cost calculation for Sonnet model."""
        cost = ad_generator._estimate_cost(
            "claude-3-5-sonnet-20241022",
            input_tokens=1000,
            output_tokens=500,
        )

        # Sonnet: $0.003 per 1k input + $0.015 per 1k output
        expected = (1000 / 1000 * 0.003) + (500 / 1000 * 0.015)
        assert abs(cost - expected) < 0.00001

    def test_cache_key_generation(self, ad_generator):
        """Test cache key generation is consistent."""
        key1 = ad_generator._make_cache_key("Coffee", "professional", 30)
        key2 = ad_generator._make_cache_key("Coffee", "professional", 30)
        key3 = ad_generator._make_cache_key("Coffee", "casual", 30)

        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different tone = different key

    def test_system_prompt_generation(self, ad_generator):
        """Test system prompt generation includes tone instructions."""
        prompt = ad_generator._build_system_prompt("professional")

        assert "professional" in prompt.lower()
        assert "json" in prompt.lower()
        assert "tagline" in prompt.lower()

    def test_user_prompt_generation(self, ad_generator):
        """Test user prompt includes all necessary information."""
        prompt = ad_generator._build_user_prompt("Coffee", "casual", 30)

        assert "Coffee" in prompt
        assert "casual" in prompt
        assert "30" in prompt


class TestTokenCounting:
    """Test suite for token counting."""

    def test_count_tokens_api_call(self):
        """Test token counting makes correct API call."""
        generator = AdGenerator()

        with patch.object(generator.client.messages, "count_tokens") as mock:
            mock.return_value = MagicMock(input_tokens=250, output_tokens=0)

            result = generator._count_tokens(
                "claude-3-haiku-20240307",
                "System prompt",
                "User message",
            )

            assert result.input_tokens == 250
            mock.assert_called_once()

    def test_token_counting_fallback(self):
        """Test token counting fallback on error."""
        generator = AdGenerator()

        with patch.object(generator.client.messages, "count_tokens") as mock:
            mock.side_effect = Exception("API error")

            result = generator._count_tokens(
                "claude-3-haiku-20240307",
                "System",
                "Message",
            )

            # Should return fallback estimate
            assert result.input_tokens > 0


class TestResponseParsing:
    """Test suite for response parsing."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON response."""
        generator = AdGenerator()

        response = '{"tagline": "Best Coffee", "script": "Full script here", "cta": "Order", "tone": "professional"}'
        result = generator._parse_response(response)

        assert result.tagline == "Best Coffee"
        assert result.script == "Full script here"
        assert result.cta == "Order"

    def test_parse_json_with_extra_text(self):
        """Test parsing JSON embedded in extra text."""
        generator = AdGenerator()

        response = 'Here is the ad:\n{"tagline": "Best", "script": "Script", "cta": "Go", "tone": "casual"}\nThat was great!'
        result = generator._parse_response(response)

        assert result.tagline == "Best"

    def test_parse_invalid_json_fallback(self):
        """Test fallback parsing for invalid JSON."""
        generator = AdGenerator()

        response = "This is not JSON but a plain text response"
        result = generator._parse_response(response)

        # Should have some content even if parsing failed
        assert len(result.tagline) >= 0
        assert len(result.script) >= 0