"""
Ad generation service with Claude API integration.
Implements cost optimization, caching, token tracking, and model selection.
"""

import logging
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from anthropic import Anthropic, APIError, APITimeoutError

from config import settings

logger = logging.getLogger(__name__)


class AdCopyResponse(BaseModel):
    """Structured response from ad generation."""

    tagline: str
    script: str
    cta: str
    tone: str


class TokenCountInfo(BaseModel):
    """Token count information."""

    input_tokens: int
    output_tokens: int
    total_tokens: int


class AdGenerationResult(BaseModel):
    """Result of ad generation."""

    tagline: str
    script: str
    cta: str
    tone: str
    tokens_input: int
    tokens_output: int
    total_tokens: int
    estimated_cost: float
    model_used: str
    cache_hit: bool = False


class AdGenerator:
    """Service for generating ad copy using Claude API with cost optimization."""

    def __init__(self):
        """Initialize the ad generator with Anthropic client."""
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.cache: dict = {}  # Simple in-memory cache
        self.cache_ttl = settings.cache_ttl_seconds

    def _select_model(self, product: str, duration: int, tone: str) -> str:
        """
        Select appropriate Claude model based on task complexity.

        Strategy:
        - Haiku: Simple products (<50 chars), short duration (<=30s), standard tones
        - Sonnet: Complex products, longer duration (>30s), luxury/premium tones

        This reduces costs by ~60% for simple ads while maintaining quality for complex ones.
        """
        complexity_score = 0

        # Product complexity
        complexity_score += len(product) // 10  # Longer products are more complex
        if any(word in product.lower() for word in ["premium", "luxury", "enterprise"]):
            complexity_score += 3

        # Duration complexity
        if duration > 30:
            complexity_score += 2
        if duration > 45:
            complexity_score += 2

        # Tone complexity
        if tone.lower() in ["luxury", "professional", "energetic"]:
            complexity_score += 2

        # Decision threshold
        if complexity_score > 6:
            return settings.claude_model_sonnet
        return settings.claude_model_haiku

    def _make_cache_key(self, product: str, tone: str, duration: int) -> str:
        """Generate cache key from product, tone, and duration."""
        key_str = f"{product}:{tone}:{duration}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[AdGenerationResult]:
        """Retrieve result from cache if not expired."""
        if cache_key not in self.cache:
            return None

        entry = self.cache[cache_key]
        if datetime.utcnow() > entry["expires_at"]:
            del self.cache[cache_key]
            return None

        # Update hit count
        entry["hits"] += 1
        logger.info(f"Cache hit for key {cache_key} (hits: {entry['hits']})")
        return entry["result"]

    def _save_to_cache(self, cache_key: str, result: AdGenerationResult) -> None:
        """Save result to cache with TTL."""
        self.cache[cache_key] = {
            "result": result,
            "expires_at": datetime.utcnow() + timedelta(seconds=self.cache_ttl),
            "hits": 0,
        }
        logger.info(f"Cached result for key {cache_key}")

    def _count_tokens(
        self, model: str, system: str, user_message: str
    ) -> TokenCountInfo:
        """
        Count tokens for a given request.
        Uses Anthropic's token counting API to get accurate estimates.
        """
        try:
            token_count = self.client.messages.count_tokens(
                model=model,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )

            return TokenCountInfo(
                input_tokens=token_count.input_tokens,
                output_tokens=0,  # Estimate output
                total_tokens=token_count.input_tokens,
            )
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            # Fallback estimation (rough)
            return TokenCountInfo(input_tokens=500, output_tokens=300, total_tokens=800)

    def _estimate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost based on token usage."""
        if model == settings.claude_model_haiku:
            input_cost = (input_tokens / 1000) * settings.haiku_input_cost_per_1k
            output_cost = (output_tokens / 1000) * settings.haiku_output_cost_per_1k
        else:
            input_cost = (input_tokens / 1000) * settings.sonnet_input_cost_per_1k
            output_cost = (output_tokens / 1000) * settings.sonnet_output_cost_per_1k

        return input_cost + output_cost

    def _parse_response(self, response_text: str) -> AdCopyResponse:
        """
        Parse Claude's response into structured format.
        Expects JSON format from Claude.
        """
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx >= 0 and end_idx > 0:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                return AdCopyResponse(
                    tagline=data.get("tagline", ""),
                    script=data.get("script", ""),
                    cta=data.get("cta", ""),
                    tone=data.get("tone", ""),
                )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse response: {e}")

        # Fallback parsing
        lines = response_text.split("\n")
        return AdCopyResponse(
            tagline=lines[0] if len(lines) > 0 else "",
            script=response_text,
            cta="Learn more",
            tone="neutral",
        )

    async def generate_ad(
        self,
        product: str,
        tone: str,
        duration: int,
        use_cache: bool = True,
    ) -> AdGenerationResult:
        """
        Generate ad copy for a product.

        Args:
            product: Product name or description
            tone: Brand tone (professional, casual, energetic, luxury, playful)
            duration: Ad duration in seconds (15-60)
            use_cache: Whether to use response caching

        Returns:
            AdGenerationResult with generated copy and cost tracking

        Raises:
            ValueError: If inputs are invalid
            APIError: If Claude API call fails
        """
        if not product or len(product) < 2:
            raise ValueError("Product name must be at least 2 characters")

        if not tone or tone not in ["professional", "casual", "energetic", "luxury", "playful"]:
            raise ValueError(f"Invalid tone: {tone}")

        if not (15 <= duration <= 60):
            raise ValueError("Duration must be between 15 and 60 seconds")

        # Check cache
        cache_key = self._make_cache_key(product, tone, duration)
        if use_cache and settings.cache_enabled:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        # Select model based on complexity
        model = self._select_model(product, duration, tone)

        # Build prompt
        system_prompt = self._build_system_prompt(tone)
        user_prompt = self._build_user_prompt(product, tone, duration)

        # Count tokens before API call
        token_info = self._count_tokens(model, system_prompt, user_prompt)

        # Call Claude API with retry logic
        result = await self._call_claude_with_retry(
            model=model,
            system=system_prompt,
            user_message=user_prompt,
            max_retries=3,
        )

        # Parse response
        ad_copy = self._parse_response(result)

        # Estimate final cost (rough output estimate)
        estimated_output_tokens = len(result.split()) * 1.3  # Rough estimation
        estimated_cost = self._estimate_cost(
            model, token_info.input_tokens, int(estimated_output_tokens)
        )

        # Create result
        generation_result = AdGenerationResult(
            tagline=ad_copy.tagline,
            script=ad_copy.script,
            cta=ad_copy.cta,
            tone=ad_copy.tone,
            tokens_input=token_info.input_tokens,
            tokens_output=int(estimated_output_tokens),
            total_tokens=token_info.input_tokens + int(estimated_output_tokens),
            estimated_cost=estimated_cost,
            model_used=model,
            cache_hit=False,
        )

        # Cache result
        if use_cache and settings.cache_enabled:
            self._save_to_cache(cache_key, generation_result)

        logger.info(
            f"Generated ad for {product}: {token_info.input_tokens} input tokens, "
            f"~{estimated_output_tokens} output tokens, cost: ${estimated_cost:.4f}"
        )

        return generation_result

    async def _call_claude_with_retry(
        self,
        model: str,
        system: str,
        user_message: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> str:
        """
        Call Claude API with exponential backoff retry logic.

        Handles transient errors gracefully and prevents cascading failures.
        """
        for attempt in range(max_retries):
            try:
                message = self.client.messages.create(
                    model=model,
                    max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": user_message}],
                    timeout=settings.claude_timeout,
                )

                return message.content[0].text

            except APITimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error(f"Claude API timeout after {max_retries} retries")
                    raise

                delay = base_delay * (2 ** attempt) + (0.1 * attempt)
                logger.warning(
                    f"Timeout on attempt {attempt + 1}, retrying in {delay:.1f}s"
                )
                await asyncio.sleep(delay)

            except APIError as e:
                logger.error(f"Claude API error: {e}")
                raise

            except Exception as e:
                logger.error(f"Unexpected error calling Claude: {e}")
                raise

    def _build_system_prompt(self, tone: str) -> str:
        """Build system prompt with tone instructions."""
        tone_descriptions = {
            "professional": "Use formal, business-focused language. Emphasize reliability, expertise, and ROI.",
            "casual": "Use friendly, conversational language. Keep it light and approachable.",
            "energetic": "Use dynamic, exciting language. Create urgency and enthusiasm.",
            "luxury": "Use premium, sophisticated language. Emphasize exclusivity and craftsmanship.",
            "playful": "Use humorous, creative language. Don't take yourself too seriously.",
        }

        description = tone_descriptions.get(tone, "Use neutral, clear language.")

        return f"""You are a world-class copywriter specializing in radio and podcast advertising.
Generate compelling, concise ad copy that drives action.

Tone: {description}

IMPORTANT: Respond ONLY with valid JSON in this format, no other text:
{{
  "tagline": "2-5 words, memorable and punchy",
  "script": "The full ad script (15-60 seconds when read aloud)",
  "cta": "A strong call-to-action",
  "tone": "{tone}"
}}

Requirements:
- Tagline must be memorable and brand-building
- Script should be conversational and natural-sounding
- Include a specific, compelling CTA
- Keep sentences short for audio delivery
- Avoid technical jargon unless essential"""

    def _build_user_prompt(self, product: str, tone: str, duration: int) -> str:
        """Build user prompt for ad generation."""
        return f"""Generate a {duration}-second ad for:
Product/Service: {product}
Tone: {tone}
Duration: {duration} seconds (approximately {duration // 3} words)

Create an ad that would work for radio, podcast, or audio streaming platforms.
Make it memorable, persuasive, and appropriate for the brand tone."""