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

### Recent Updates (Migration Complete)
- Successfully migrated from Lovable to Replit environment
- Converted routing from React Router to Wouter for Replit compatibility  
- Added enhanced voice input with both browser Speech API and optional OpenAI Whisper support
- Implemented OpenAI integration for intelligent therapy responses with fallback to rule-based responses
- Fixed all import paths and module resolution for Replit environment
- Application now running successfully on port 5000

### Current Limitations
- Backend currently uses in-memory storage (MemStorage class)
- OpenAI API integration requires user to provide OPENAI_API_KEY for enhanced responses
- Authentication system defined but not implemented

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