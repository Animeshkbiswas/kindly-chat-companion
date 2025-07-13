# Psychology Module Integration

This document explains the integration of the PsychologyTest module with the existing therapy chat application.

## Overview

The PsychologyTest module from `backend/hugg/1.PsychologyTest/` has been integrated into the existing FastAPI backend and React frontend, providing:

- **Structured Clinical Interviews**: 25-question clinical psychology interviews
- **RAG-powered Responses**: Uses FAISS vector database with psychological knowledge base
- **Voice Interaction**: Text-to-speech and speech-to-text capabilities
- **Clinical Report Generation**: Automatic PDF report generation
- **Document Analysis**: Upload and analyze TXT, PDF, DOCX files
- **Multiple Interviewers**: Sarah (empathetic) and Aaron (direct) personalities
- **Multi-language Support**: Interviews in multiple languages

## Architecture

### Backend Integration

```
backend/
├── routers/
│   └── psychology.py          # New psychology API endpoints
├── services/
│   └── psychology_service.py  # Psychology service integration
├── models/
│   └── pydantic_models.py     # Updated with psychology models
├── hugg/
│   └── 1.PsychologyTest/      # Original psychology module
└── main.py                    # Updated to include psychology router
```

### Frontend Integration

```
client/src/
├── components/
│   └── PsychologyInterview.tsx  # New psychology interview component
├── pages/
│   └── Index.tsx               # Updated with mode selection
└── App.tsx                     # Main app component
```

## API Endpoints

### Psychology Interview Endpoints

- `POST /api/psychology/start-interview` - Start a new interview session
- `POST /api/psychology/continue-interview` - Continue interview with user response
- `POST /api/psychology/generate-report/{session_id}` - Generate clinical report
- `POST /api/psychology/analyze-document` - Analyze uploaded document
- `GET /api/psychology/download-report/{filename}` - Download PDF report
- `GET /api/psychology/interviewers` - Get available interviewers

### Request/Response Models

```typescript
// Start Interview Request
{
  interviewer: "sarah" | "aaron",
  language: "english" | "spanish" | "french" | "german",
  session_id?: number,
  user_id?: number
}

// Interview Response
{
  session_id: number,
  message: string,
  audio_data?: bytes,
  question_count: number,
  total_questions: number,
  is_complete: boolean
}
```

## Features

### 1. Structured Clinical Interviews

- **25-question format** based on clinical psychology best practices
- **RAG-powered questions** using psychological knowledge base
- **Context-aware follow-ups** based on user responses
- **Progress tracking** with question counter

### 2. Multiple Interviewer Personalities

#### Sarah (Empathetic)
- 30+ years of clinical experience
- Specializes in trauma, anxiety disorders, family therapy
- Warm, compassionate approach
- Voice: "alloy"

#### Aaron (Direct)
- 15+ years of clinical experience
- Military background, high-performance demands
- Tough-minded, direct approach
- Voice: "onyx"

### 3. Voice Integration

- **Text-to-Speech**: AI responses converted to audio
- **Speech-to-Text**: User voice input (planned)
- **Audio Playback**: Browser-based audio controls
- **Voice Selection**: Different voices per interviewer

### 4. Document Analysis

- **Supported Formats**: TXT, PDF, DOCX
- **Content Analysis**: Up to 100K characters
- **Clinical Reports**: Automatic report generation
- **PDF Export**: Downloadable clinical reports

### 5. Clinical Report Generation

- **Interview Reports**: Based on completed interviews
- **Document Reports**: Based on uploaded documents
- **Professional Format**: PDF with proper formatting
- **Multi-language**: Reports in user's preferred language

## Installation & Setup

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../client
npm install
```

### 2. Environment Configuration

Ensure your `.env` file includes:

```env
# OpenAI API Key (required for psychology module)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: DeepSeek API for fallback
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 3. Knowledge Base Setup

The psychology module uses a FAISS vector database with psychological knowledge. The knowledge base should be located at:

```
backend/hugg/1.PsychologyTest/knowledge/faiss_index_all_documents/
```

### 4. Start the Application

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd client
npm run dev
```

## Usage

### Starting a Psychology Interview

1. Open the application in your browser
2. Select "Psychology Interview" mode
3. Choose your preferred interviewer (Sarah or Aaron)
4. Select your preferred language
5. Click "Start Interview"
6. Respond to the structured questions
7. Complete the 25-question interview
8. Download your clinical report

### Document Analysis

1. Switch to "Document Analysis" tab
2. Upload a TXT, PDF, or DOCX file
3. Select your preferred language
4. Click "Choose File" to upload
5. Wait for analysis to complete
6. Download the generated report

### Regular Therapy Chat

1. Select "Regular Therapy Chat" mode
2. Use the existing free-form conversation interface
3. All existing features remain available

## Technical Details

### RAG Implementation

The psychology module uses Retrieval-Augmented Generation (RAG) with:

- **FAISS Vector Database**: For efficient similarity search
- **OpenAI Embeddings**: For text vectorization
- **LangChain**: For chain orchestration
- **Psychological Knowledge Base**: DSM-5, PDM-2, clinical guidelines

### Audio Processing

- **Text-to-Speech**: OpenAI TTS-1-HD model
- **Voice Selection**: Different voices per interviewer personality
- **Audio Streaming**: Browser-based audio playback
- **Format**: MP3 for compatibility

### Report Generation

- **PDF Creation**: ReportLab library
- **Professional Formatting**: Clinical report standards
- **Multi-language Support**: Localized content
- **File Management**: Secure file storage and retrieval

## Troubleshooting

### Common Issues

1. **Knowledge Base Not Found**
   ```
   Error: Knowledge base not connected
   Solution: Ensure FAISS index exists in the correct location
   ```

2. **OpenAI API Errors**
   ```
   Error: OpenAI API key not configured
   Solution: Set OPENAI_API_KEY in environment variables
   ```

3. **Audio Playback Issues**
   ```
   Error: Audio not playing
   Solution: Check browser audio permissions and codec support
   ```

4. **File Upload Errors**
   ```
   Error: Unsupported file format
   Solution: Ensure file is TXT, PDF, or DOCX format
   ```

### Testing Integration

Run the integration test script:

```bash
python test_integration.py
```

This will test:
- Psychology service integration
- API endpoint registration
- Frontend component availability

## Security Considerations

- **File Upload Validation**: Strict file type checking
- **Path Traversal Prevention**: Secure file path handling
- **API Key Protection**: Environment variable storage
- **Session Management**: Secure session handling
- **Data Privacy**: Local processing where possible

## Performance Optimization

- **Caching**: Knowledge base caching for faster responses
- **Async Processing**: Non-blocking interview continuation
- **Audio Streaming**: Efficient audio delivery
- **Database Optimization**: Efficient session storage

## Future Enhancements

- **Real-time Speech Recognition**: Live voice input processing
- **Advanced Analytics**: Interview pattern analysis
- **Multi-modal Support**: Image and video analysis
- **Collaborative Features**: Multi-user interview sessions
- **Advanced Reporting**: Customizable report templates

## Contributing

To contribute to the psychology module integration:

1. Follow the existing code style and patterns
2. Add tests for new features
3. Update documentation for API changes
4. Ensure backward compatibility
5. Test with both interviewers and languages

## License

This integration maintains the original license of the PsychologyTest module while extending the existing therapy chat application. 