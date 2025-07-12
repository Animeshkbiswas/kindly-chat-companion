# FastAPI Backend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values
nano .env
```

Required environment variables:
- `DATABASE_URL`: Your PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate a secure random string)
- `OPENAI_API_KEY`: OpenAI API key for enhanced AI features (optional)

### 3. Database Setup
```bash
# Run database migrations
alembic upgrade head

# Or for development, let SQLAlchemy create tables
python -c "import asyncio; from models.database import init_db; asyncio.run(init_db())"
```

### 4. Start the Server
```bash
# Development server with auto-reload
python run.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API Base: http://localhost:8000/api
- Documentation: http://localhost:8000/api/docs
- Alternative Docs: http://localhost:8000/api/redoc

## API Endpoints Overview

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Therapy Sessions
- `POST /api/sessions/` - Create new session
- `GET /api/sessions/{user_id}` - Get user sessions
- `GET /api/sessions/session/{session_id}` - Get specific session
- `PATCH /api/sessions/session/{session_id}/title` - Update session title

### Chat Messages
- `POST /api/messages/` - Create message
- `GET /api/messages/{session_id}` - Get session messages
- `POST /api/messages/chat` - Main chat endpoint with AI responses

### User Settings
- `GET /api/settings/{user_id}` - Get user settings
- `PATCH /api/settings/{user_id}` - Update user settings

### Audio Processing
- `POST /api/audio/transcribe` - Transcribe audio to text
- `POST /api/audio/synthesize` - Convert text to speech
- `GET /api/audio/voices` - Get available TTS voices

### Reports
- `POST /api/reports/generate` - Generate session report
- `GET /api/reports/session/{session_id}` - Get session reports
- `GET /api/reports/download/{report_id}` - Download report PDF

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Create Demo Session
```bash
curl -X POST http://localhost:8000/api/sessions/demo/init
```

### 3. Test Chat
```bash
curl -X POST http://localhost:8000/api/messages/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I am feeling anxious today",
    "session_id": 1,
    "therapist_personality": "warm"
  }'
```

## Frontend Integration

Update your React frontend to use the new FastAPI endpoints:

```typescript
// Update API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Example API call
const response = await fetch(`${API_BASE_URL}/messages/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userInput,
    session_id: currentSessionId,
    therapist_personality: 'warm'
  })
});
```

## Development Tips

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features
1. Create/update Pydantic models in `models/pydantic_models.py`
2. Update SQLAlchemy models in `models/schemas.py` if needed
3. Create service logic in `services/`
4. Add router endpoints in `routers/`
5. Include router in `main.py`

### Environment Variables
- Development: Uses `.env` file
- Production: Set environment variables directly
- Required: `DATABASE_URL`, `SECRET_KEY`
- Optional: `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`

## Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t therapy-chat-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="your-production-db-url" \
  -e SECRET_KEY="your-production-secret" \
  -e OPENAI_API_KEY="your-openai-key" \
  therapy-chat-api
```

### Environment Setup
- Set `ENVIRONMENT=production`
- Use a strong `SECRET_KEY`
- Configure proper `DATABASE_URL`
- Set up SSL/TLS certificates
- Configure reverse proxy (nginx/Apache)

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL is running
   - Verify database exists

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

3. **JWT Token Issues**
   - Verify `SECRET_KEY` is set
   - Check token expiration settings

4. **AI Service Errors**
   - Verify `OPENAI_API_KEY` if using OpenAI features
   - Check API key permissions and quota

### Logs
```bash
# View application logs
tail -f logs/app.log

# Check database logs
tail -f logs/db.log
```

## Migration from Express Backend

The FastAPI backend maintains API compatibility with the existing Express backend. Key changes:

1. **Enhanced AI Integration**: Better OpenAI integration with DeepSeek-V3 support
2. **Advanced Analytics**: Session analytics and report generation
3. **Improved Audio**: Server-side audio processing with Whisper support
4. **Better Performance**: Async/await throughout, improved database queries
5. **Type Safety**: Full Pydantic validation for all requests/responses

The frontend can gradually migrate to use new features while maintaining existing functionality.