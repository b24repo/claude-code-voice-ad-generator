"""
FastAPI application for voice ad generation.
Main entry point with routes and middleware setup.
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import settings
from services.database import init_db, get_db
from models.database import Campaign, Ad, UsageTracking
from models.schemas import (
    CampaignCreate,
    CampaignResponse,
    AdGenerationRequest,
    AdGenerationResponse,
    VoiceSynthesisRequest,
    VoiceSynthesisResponse,
    ErrorResponse,
)
from services.ad_generator import AdGenerator
from services.voice_synthesizer import VoiceSynthesizer

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize services
ad_generator = AdGenerator()
voice_synthesizer = VoiceSynthesizer(api_key=settings.elevenlabs_api_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting voice ad generator API")
    init_db()
    yield
    logger.info("Shutting down voice ad generator API")


app = FastAPI(
    title="Voice Ad Generator API",
    description="AI-powered voice ad generation with cost optimization",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.2f}s"
    )

    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
    }


# Campaign endpoints
@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign_create: CampaignCreate,
    db: Session = Depends(get_db),
):
    """Create a new campaign."""
    try:
        campaign = Campaign(
            name=campaign_create.name,
            product=campaign_create.product,
            description=campaign_create.description,
            tone=campaign_create.tone,
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        logger.info(f"Created campaign: {campaign.id} - {campaign.name}")
        return campaign
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns")
async def list_campaigns(db: Session = Depends(get_db)):
    """List all campaigns."""
    try:
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "product": c.product,
                "tone": c.tone,
                "createdAt": c.created_at.isoformat(),
                "adCount": c.ad_count,
                "totalTokens": c.total_tokens,
            }
            for c in campaigns
        ]
    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Get a specific campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# Ad generation endpoints
@app.post("/api/campaigns/{campaign_id}/ads/generate")
async def generate_ad(
    campaign_id: str,
    request: AdGenerationRequest,
    db: Session = Depends(get_db),
):
    """Generate ad copy for a campaign."""
    try:
        # Verify campaign exists
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Generate ad using Claude
        tone = request.tone or campaign.tone
        result = await ad_generator.generate_ad(
            product=request.product,
            tone=tone,
            duration=request.duration,
            use_cache=True,
        )

        # Store in database
        ad = Ad(
            campaign_id=campaign_id,
            tagline=result.tagline,
            script=result.script,
            cta=result.cta,
            tone_used=result.tone,
            duration_seconds=request.duration,
            tokens_input=result.tokens_input,
            tokens_output=result.tokens_output,
            total_tokens=result.total_tokens,
            estimated_cost=result.estimated_cost,
            model_used=result.model_used,
        )

        db.add(ad)

        # Update campaign stats
        campaign.total_tokens += result.total_tokens
        campaign.total_cost += result.estimated_cost
        campaign.ad_count += 1

        # Track usage
        usage = UsageTracking(
            campaign_id=campaign_id,
            request_type="ad_generation",
            model_used=result.model_used,
            input_tokens=result.tokens_input,
            output_tokens=result.tokens_output,
            total_tokens=result.total_tokens,
            estimated_cost=result.estimated_cost,
            success=True,
        )

        db.add(usage)
        db.commit()
        db.refresh(ad)

        logger.info(
            f"Generated ad for campaign {campaign_id}: "
            f"{result.total_tokens} tokens, ${result.estimated_cost:.3f}"
        )

        return AdGenerationResponse(
            ad_id=ad.id,
            tagline=result.tagline,
            script=result.script,
            cta=result.cta,
            duration_seconds=request.duration,
            tokens_used=result.total_tokens,
            cost=result.estimated_cost,
            model_used=result.model_used,
            cache_hit=result.cache_hit,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate ad: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns/{campaign_id}/ads")
async def list_ads(campaign_id: str, db: Session = Depends(get_db)):
    """List ads for a campaign."""
    try:
        ads = (
            db.query(Ad)
            .filter(Ad.campaign_id == campaign_id)
            .order_by(Ad.created_at.desc())
            .all()
        )

        return [
            {
                "id": ad.id,
                "tagline": ad.tagline,
                "script": ad.script,
                "duration": ad.duration_seconds,
                "tokens": ad.total_tokens,
                "cost": ad.estimated_cost,
                "createdAt": ad.created_at.isoformat(),
            }
            for ad in ads
        ]
    except Exception as e:
        logger.error(f"Failed to list ads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice synthesis endpoints
@app.post("/api/campaigns/{campaign_id}/ads/{ad_id}/voice")
async def synthesize_voice(
    campaign_id: str,
    ad_id: str,
    request: VoiceSynthesisRequest,
    db: Session = Depends(get_db),
):
    """Synthesize voice for an ad."""
    try:
        # Verify ad exists
        ad = (
            db.query(Ad)
            .filter(Ad.id == ad_id, Ad.campaign_id == campaign_id)
            .first()
        )
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        # Synthesize voice
        result = await voice_synthesizer.synthesize(
            script=ad.script,
            voice_id=request.voice_id,
        )

        # Update ad with voice info
        ad.voice_synthesized = True
        ad.voice_id = request.voice_id

        # In production, save audio to S3 and store URL
        # For now, return mock audio URL
        audio_url = f"/api/audio/{ad_id}"
        ad.audio_url = audio_url

        # Track usage
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        usage = UsageTracking(
            campaign_id=campaign_id,
            request_type="voice_synthesis",
            model_used="elevenlabs",
            estimated_cost=result.cost,
            success=True,
        )

        db.add(usage)
        campaign.total_cost += result.cost
        db.commit()

        logger.info(
            f"Synthesized voice for ad {ad_id}: "
            f"voice={request.voice_id}, cost=${result.cost:.3f}"
        )

        return VoiceSynthesisResponse(
            audio_url=audio_url,
            voice_id=request.voice_id,
            duration_seconds=result.duration_seconds,
            cost=result.cost,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to synthesize voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Usage tracking endpoints
@app.get("/api/campaigns/{campaign_id}/usage")
async def get_campaign_usage(campaign_id: str, db: Session = Depends(get_db)):
    """Get usage stats for a campaign."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        usage_records = (
            db.query(UsageTracking)
            .filter(UsageTracking.campaign_id == campaign_id)
            .all()
        )

        return {
            "campaign_id": campaign_id,
            "total_tokens": campaign.total_tokens,
            "total_cost": campaign.total_cost,
            "ad_count": campaign.ad_count,
            "usage_records": [
                {
                    "type": u.request_type,
                    "model": u.model_used,
                    "tokens": u.total_tokens,
                    "cost": u.estimated_cost,
                    "timestamp": u.created_at.isoformat(),
                }
                for u in usage_records
            ],
        }
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail).dict(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=settings.log_level.lower())