# Therapy Chat Application

## Overview

This is a full-stack therapy chatbot application built with a React frontend, Express.js backend, and PostgreSQL database. The application provides an immersive virtual therapy experience with features like voice interaction, real-time audio visualization, speech synthesis, and a calming, therapy-inspired UI design.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **UI Library**: Shadcn/ui components built on Radix UI primitives
- **Styling**: Tailwind CSS with custom therapy-inspired color palette
- **State Management**: TanStack React Query for server state, React hooks for local state
- **Routing**: React Router for client-side navigation

### Backend Architecture
- **Framework**: Express.js with TypeScript
- **Module System**: ES Modules (type: "module")
- **Development**: tsx for TypeScript execution in development
- **Build**: esbuild for production bundling
- **API Structure**: RESTful endpoints under `/api` prefix

### Database Architecture
- **Database**: PostgreSQL with Neon serverless driver
- **ORM**: Drizzle ORM for type-safe database operations
- **Schema Management**: Drizzle Kit for migrations and schema management
- **Current Schema**: Basic user table with username/password fields

## Key Components

### Therapy Chat Interface
- **TherapyChat**: Main chat component managing conversation state
- **ChatMessage**: Individual message rendering with user/therapist distinction
- **TherapistCharacter**: Animated SVG character with mood states and speech animations

### Voice and Audio Features
- **VoiceInput**: Speech recognition for user input
- **SpeechSynthesis**: Text-to-speech for therapist responses
- **AudioVisualization**: Real-time audio level monitoring and visualization
- **AudioStreamProcessor**: WebAudio API integration for microphone access

### Settings and Controls
- **TherapySettings**: Configurable voice, speech, and personality settings
- **AudioVisualizationToggle**: Enable/disable real-time audio features

### UI Components
- Comprehensive Shadcn/ui component library
- Custom therapy-themed styling with calming colors
- Responsive design for mobile and desktop

## Data Flow

1. **User Input**: Text or voice input through chat interface
2. **Message Processing**: Messages stored in local state, sent to backend API
3. **AI Response**: Backend processes input and returns therapist response
4. **Audio Output**: Optional text-to-speech synthesis of responses
5. **Visual Feedback**: Character animations and audio visualizations enhance experience

### Recent Updates (Migration Complete - January 2025)
- Successfully migrated from Lovable to Replit environment
- Converted routing from React Router to Wouter for Replit compatibility  
- Added enhanced voice input with both browser Speech API and optional OpenAI Whisper support
- Implemented OpenAI integration for intelligent therapy responses with fallback to rule-based responses
- Fixed all import paths and module resolution for Replit environment
- Application now running successfully on port 5000

### Database Integration (January 2025)
- Added PostgreSQL database with comprehensive therapy-focused schema
- Created tables for users, therapy sessions, messages, and user settings
- Implemented database storage layer replacing in-memory storage
- Added API endpoints for session management, message persistence, and settings
- Database schema includes proper relationships and constraints
- Successfully deployed database migrations with `npm run db:push`

### Database Integration (Complete)
- PostgreSQL database with Neon serverless driver
- Comprehensive schema with users, therapy sessions, messages, and user settings tables
- Full database relationships with foreign keys and proper indexing
- Storage layer migrated from in-memory to database persistence
- API endpoints for all therapy-related operations

### Current Features
- Real-time therapy chat with AI responses (OpenAI integration with fallback)
- Voice input with both browser Speech API and optional OpenAI Whisper support
- Text-to-speech for therapist responses
- Audio visualization and character mood animations
- Persistent chat history and user settings
- Database-backed session management
- Enhanced voice input component with error handling

## External Dependencies

### Core Dependencies
- **React Ecosystem**: React, React Router, React Hook Form
- **UI Libraries**: Radix UI primitives, Lucide React icons
- **Database**: Drizzle ORM, Neon PostgreSQL driver
- **Development**: Vite, TypeScript, Tailwind CSS
- **Query Management**: TanStack React Query

### Audio/Speech APIs
- Web Speech API for speech recognition
- Speech Synthesis API for text-to-speech
- Web Audio API for real-time audio processing

### Development Tools
- ESLint and Prettier for code quality
- TypeScript for type safety
- Replit-specific plugins for development environment

## Deployment Strategy

### Development
- Vite dev server with HMR for frontend
- tsx for running TypeScript backend in development
- Replit integration with custom plugins and error handling

### Production Build
- Vite builds frontend to `dist/public`
- esbuild bundles backend to `dist/index.js`
- Single Node.js process serves both frontend and API

### Database
- PostgreSQL database with connection via DATABASE_URL environment variable
- Drizzle migrations in `./migrations` directory
- Schema defined in `shared/schema.ts` for type sharing

### Environment Requirements
- Node.js with ES Modules support
- PostgreSQL database (Neon or compatible)
- Environment variables: DATABASE_URL

The application follows a monorepo structure with shared TypeScript types between frontend and backend, enabling type-safe API development and consistent data models across the stack.

## FastAPI Migration (January 2025)
### Comprehensive Backend Modernization
- **Complete FastAPI Backend**: Full Python FastAPI backend with async/await support
- **Enhanced AI Integration**: OpenAI GPT-4o + DeepSeek-V3 with intelligent fallback system
- **Advanced Audio Processing**: Server-side Whisper transcription and OpenAI TTS
- **SQLAlchemy Database**: Async PostgreSQL with proper migrations and relationships
- **Report Generation**: PDF therapy reports with session analytics and insights
- **Type Safety**: Full Pydantic validation for all API requests and responses
- **Authentication**: JWT-based auth system with password hashing
- **Production Ready**: Docker support, environment configuration, comprehensive error handling

### Migration Benefits
- **Better AI Responses**: Multi-model AI with enhanced personality customization
- **Advanced Analytics**: Session insights, mood tracking, and progress reports
- **Improved Performance**: Async database operations and optimized queries
- **Scalability**: FastAPI's high performance and automatic API documentation
- **Developer Experience**: Type-safe API with automatic OpenAPI/Swagger docs

### API Structure
```
/api/auth          - Authentication (register, login, tokens)
/api/sessions      - Therapy session management
/api/messages      - Chat messages with AI responses
/api/settings      - User preferences and therapy settings
/api/audio         - Transcription and text-to-speech
/api/reports       - Session reports and analytics
```

### Next Steps
1. Install Python dependencies and configure environment
2. Test FastAPI backend alongside current Express server
3. Gradually migrate frontend components to new API endpoints
4. Deploy enhanced backend with improved AI capabilities