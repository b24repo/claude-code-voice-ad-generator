# Claude Code Voice Ad Generator

An AI-powered voice ad generation platform that combines the best of AI with practical engineering. Built with **Next.js**, **FastAPI**, and **Claude API** to demonstrate modern full-stack development with Claude Code.

## Overview

The Claude Code Voice Ad Generator enables marketing teams to create professional voice ads in minutes, not days. Using advanced AI to generate compelling ad copy and synthesize natural-sounding voice talent, it streamlines the entire ad creation workflow.

**Built with Claude Code** - This entire project was developed using Anthropic's Claude Code CLI, showcasing a collaborative AI-assisted development workflow that balances productivity with code quality.

## Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend - Next.js 14"]
        A["Landing Page"]
        B["Campaign Manager"]
        C["Ad Generator UI"]
        D["Voice Preview"]
    end

    subgraph Backend["Backend - FastAPI"]
        E["API Routes"]
        F["Ad Generator Service"]
        G["Voice Synthesizer"]
        H["Database Models"]
    end

    subgraph External["External Services"]
        I["Claude API<br/>Haiku/Sonnet"]
        J["ElevenLabs API"]
        K["PostgreSQL"]
    end

    A --> E
    B --> E
    C --> E
    D --> E
    E --> F
    E --> G
    E --> H
    F --> I
    G --> J
    H --> K
    F -.Token Counting.-> I
    F -.Caching.-> E
```

## Features

- **Intelligent Ad Generation**: Claude API generates ad copy tailored to brand voice and product type
- **Cost-Optimized AI Calls**: Dynamic model selection (Haiku for simple content, Sonnet for complex scripts)
- **Token Usage Tracking**: Real-time monitoring of API costs and usage patterns
- **Response Caching**: Smart caching layer to reduce redundant API calls
- **Voice Synthesis**: Integration with ElevenLabs for natural-sounding voice over
- **Campaign Management**: Organize multiple ad campaigns with version history
- **PostgreSQL Persistence**: Durable storage for campaigns, ads, and voice profiles
- **Docker Deployment**: Complete containerized setup for local and cloud deployment

## Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **React 18**
- **TypeScript**
- **TailwindCSS**
- **Fetch API** for client-server communication

### Backend
- **FastAPI** (Python 3.11+)
- **SQLAlchemy** (ORM)
- **Pydantic** (Data validation)
- **Anthropic SDK** (Claude API)
- **Pytest** (Testing)

### Infrastructure
- **PostgreSQL 15** (Database)
- **Docker & Docker Compose** (Containerization)
- **GitHub Actions** (CI/CD)

### External APIs
- **Anthropic Claude API** (Text generation)
- **ElevenLabs API** (Voice synthesis)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- API Keys: Claude API, ElevenLabs

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/b24repo/claude-code-voice-ad-generator.git
   cd claude-code-voice-ad-generator
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Add your API keys:
   # ANTHROPIC_API_KEY=your_key_here
   # ELEVENLABS_API_KEY=your_key_here
   # DATABASE_URL=postgresql://user:password@localhost:5432/voice_ads

   # Frontend
   cp frontend/.env.example frontend/.env
   # Add backend API endpoint:
   # NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**
   ```bash
   docker-compose exec backend python -m alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

### Without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
claude-code-voice-ad-generator/
├── frontend/                      # Next.js application
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── campaigns/
│   │   │   ├── page.tsx          # Campaign list
│   │   │   └── [id]/
│   │   │       └── page.tsx      # Individual campaign
│   │   └── layout.tsx
│   ├── components/
│   │   ├── AdGenerator.tsx
│   │   ├── VoicePreview.tsx
│   │   └── CampaignForm.tsx
│   ├── lib/
│   │   └── api.ts
│   ├── styles/
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                       # FastAPI application
│   ├── main.py
│   ├── services/
│   │   ├── ad_generator.py
│   │   ├── voice_synthesizer.py
│   │   └── cache_service.py
│   ├── models/
│   │   ├── database.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── campaigns.py
│   │   ├── ads.py
│   │   └── health.py
│   ├── tests/
│   │   ├── test_ad_generator.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── CLAUDE_CODE_WORKFLOW.md
├── .gitignore
└── README.md
```

## API Endpoints

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `POST /api/campaigns` - Create new campaign
- `GET /api/campaigns/{id}` - Get campaign details
- `PATCH /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign

### Ads
- `POST /api/campaigns/{id}/ads/generate` - Generate ad copy
- `POST /api/campaigns/{id}/ads/{ad_id}/voice` - Synthesize voice
- `GET /api/campaigns/{id}/ads` - List campaign ads

### Health & Monitoring
- `GET /health` - Health check
- `GET /api/usage/tokens` - Token usage stats
- `GET /api/cache/stats` - Cache statistics

## Cost Optimization

This project implements several patterns for cost-effective AI API usage:

### 1. Dynamic Model Selection
The ad_generator service automatically selects between Haiku and Sonnet based on task complexity:
- **Haiku**: Simple taglines, product descriptions
- **Sonnet**: Complex scripts, multi-product campaigns, brand storytelling

### 2. Response Caching
Common requests are cached with a TTL, reducing redundant API calls:
```python
# Same product + brand voice = cached response
generate_ad(product="Coffee", brand_voice="premium", use_cache=True)
```

### 3. Token Usage Tracking
Every API call is logged with token counts for monitoring:
```
Campaign: "Q1 Coffee Campaign"
Total tokens: 12,450
Cost: $0.18
Avg per ad: $0.045
```

### 4. Batch Processing
Generate multiple ad variations in a single API call when possible.

## Development with Claude Code

This project demonstrates the Claude Code development workflow:

1. **Prompt-Driven Development**: Feature PRDs translated directly to implementation
2. **Iterative Refinement**: Claude Code provided rapid iteration cycles
3. **Testing-First Approach**: Test cases written alongside implementation
4. **Code Quality**: Type hints, docstrings, and comprehensive error handling

See [CLAUDE_CODE_WORKFLOW.md](./CLAUDE_CODE_WORKFLOW.md) for detailed insights.

## Testing

### Backend Tests
```bash
cd backend
pytest -v --cov=services tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
docker-compose exec backend pytest tests/test_integration.py -v
```

## Monitoring & Logging

The application includes structured logging for:
- API request/response times
- Token usage per campaign
- Voice synthesis latency
- Cache hit/miss rates
- Database query performance

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Deployment

### Docker Build
```bash
docker-compose build
docker-compose push  # Push to your registry
```

### Cloud Deployment (AWS Example)
```bash
# Using ECS
aws ecs update-service --cluster voice-ads --service api --force-new-deployment
```

## Contributing

When contributing, please:
1. Follow TypeScript/Python style guides
2. Add tests for new features
3. Update documentation
4. Submit pull requests with clear descriptions

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open GitHub Issues
- Email: support@voiceadgenerator.app
- Docs: https://docs.voiceadgenerator.app

---

**Built with Claude Code** - An AI-assisted development experience that demonstrates how modern AI tools can accelerate software development while maintaining code quality and engineering best practices.