"""
SQLAlchemy models for PostgreSQL persistence.
Defines database schema for campaigns, ads, voice profiles, and usage tracking.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Campaign(Base):
    """Campaign model for organizing ad generation projects."""

    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    product = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tone = Column(String(50), nullable=False)  # professional, casual, energetic, luxury, playful
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Tracking
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    ad_count = Column(Integer, default=0)

    # Relations
    ads = relationship("Ad", back_populates="campaign", cascade="all, delete-orphan")
    usage_records = relationship("UsageTracking", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Campaign id={self.id} name={self.name}>"


class Ad(Base):
    """Generated ad copy with metadata."""

    __tablename__ = "ads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    tagline = Column(String(500), nullable=False)
    script = Column(Text, nullable=False)
    cta = Column(String(500), nullable=True)
    tone_used = Column(String(50), nullable=False)
    duration_seconds = Column(Integer, nullable=False)  # 15, 30, 45, 60

    # Token and Cost Tracking
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    model_used = Column(String(50), nullable=False)  # haiku or sonnet

    # Voice Synthesis
    voice_synthesized = Column(Boolean, default=False)
    voice_id = Column(String(50), nullable=True)
    audio_url = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relations
    campaign = relationship("Campaign", back_populates="ads")

    def __repr__(self) -> str:
        return f"<Ad id={self.id} tagline={self.tagline[:50]}>"


class VoiceProfile(Base):
    """Voice profile for voice synthesis options."""

    __tablename__ = "voice_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    gender = Column(String(50), nullable=True)
    accent = Column(String(100), nullable=True)
    tone_characteristics = Column(Text, nullable=True)  # JSON: energetic, professional, friendly, etc.

    # Pricing
    cost_per_character = Column(Float, default=0.01)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<VoiceProfile id={self.voice_id} name={self.name}>"


class UsageTracking(Base):
    """Detailed tracking of API usage for cost monitoring and analytics."""

    __tablename__ = "usage_tracking"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)

    # Request Details
    request_type = Column(String(50), nullable=False)  # ad_generation, voice_synthesis
    model_used = Column(String(100), nullable=True)  # claude-3-haiku, claude-3-sonnet, elevenlabs

    # Token Usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Cost
    estimated_cost = Column(Float, default=0.0)

    # Performance
    latency_ms = Column(Integer, default=0)

    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relations
    campaign = relationship("Campaign", back_populates="usage_records")

    def __repr__(self) -> str:
        return f"<UsageTracking id={self.id} type={self.request_type}>"


class CacheEntry(Base):
    """Cache for ad generation responses to reduce API calls."""

    __tablename__ = "cache_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String(256), unique=True, nullable=False, index=True)

    # Cached content
    tagline = Column(String(500), nullable=False)
    script = Column(Text, nullable=False)
    cta = Column(String(500), nullable=True)
    tone = Column(String(50), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    hit_count = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<CacheEntry cache_key={self.cache_key}>"