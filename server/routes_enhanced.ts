import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage.js";
import { 
  insertTherapySessionSchema, 
  insertTherapyMessageSchema, 
  insertUserSettingsSchema 
} from "../shared/schema.js";

export async function registerRoutes(app: Express): Promise<Server> {
  // Therapy Sessions API
  app.post("/api/sessions", async (req, res) => {
    try {
      const sessionData = insertTherapySessionSchema.parse(req.body);
      const session = await storage.createTherapySession(sessionData);
      res.json(session);
    } catch (error) {
      console.error("Error creating session:", error);
      res.status(400).json({ error: "Invalid session data" });
    }
  });

  app.get("/api/sessions/:userId", async (req, res) => {
    try {
      const userId = parseInt(req.params.userId);
      const sessions = await storage.getUserSessions(userId);
      res.json(sessions);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      res.status(500).json({ error: "Failed to fetch sessions" });
    }
  });

  app.get("/api/session/:sessionId", async (req, res) => {
    try {
      const sessionId = parseInt(req.params.sessionId);
      const session = await storage.getSession(sessionId);
      if (!session) {
        return res.status(404).json({ error: "Session not found" });
      }
      res.json(session);
    } catch (error) {
      console.error("Error fetching session:", error);
      res.status(500).json({ error: "Failed to fetch session" });
    }
  });

  app.patch("/api/session/:sessionId/title", async (req, res) => {
    try {
      const sessionId = parseInt(req.params.sessionId);
      const { title } = req.body;
      await storage.updateSessionTitle(sessionId, title);
      res.json({ success: true });
    } catch (error) {
      console.error("Error updating session title:", error);
      res.status(500).json({ error: "Failed to update session title" });
    }
  });

  // Therapy Messages API
  app.post("/api/messages", async (req, res) => {
    try {
      const messageData = insertTherapyMessageSchema.parse(req.body);
      const message = await storage.createTherapyMessage(messageData);
      res.json(message);
    } catch (error) {
      console.error("Error creating message:", error);
      res.status(400).json({ error: "Invalid message data" });
    }
  });

  app.get("/api/messages/:sessionId", async (req, res) => {
    try {
      const sessionId = parseInt(req.params.sessionId);
      const messages = await storage.getSessionMessages(sessionId);
      res.json(messages);
    } catch (error) {
      console.error("Error fetching messages:", error);
      res.status(500).json({ error: "Failed to fetch messages" });
    }
  });

  // Enhanced AI Therapy Response with Settings
  app.post("/api/therapy/response", async (req, res) => {
    try {
      const { userMessage, personality, conversationHistory } = req.body;
      
      // Use OpenAI if API key is available, otherwise fallback
      const apiKey = process.env.OPENAI_API_KEY;
      let response;
      
      if (apiKey) {
        try {
          // Enhanced OpenAI integration with personality
          const messages = [
            {
              role: 'system',
              content: `You are Dr. Sarah, a compassionate virtual therapist with a ${personality} personality. 
              
              Provide supportive, empathetic responses that:
              - Show active listening and validation
              - Ask thoughtful follow-up questions
              - Maintain appropriate therapeutic boundaries
              - Keep responses concise but meaningful (2-3 sentences)
              - Match the ${personality} personality style`
            },
            ...(conversationHistory || []).slice(-6),
            {
              role: 'user',
              content: userMessage
            }
          ];

          const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${apiKey}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              model: 'gpt-4o',
              messages,
              max_tokens: 150,
              temperature: 0.7,
              presence_penalty: 0.1,
              frequency_penalty: 0.1
            })
          });

          if (openaiResponse.ok) {
            const data = await openaiResponse.json();
            response = data.choices[0]?.message?.content || 'I hear you. Can you tell me more about what you\'re experiencing?';
          }
        } catch (openaiError) {
          console.log('OpenAI error, using fallback:', openaiError);
        }
      }
      
      // Fallback response if OpenAI fails or no API key
      if (!response) {
        const fallbackResponses = {
          warm: [
            "I hear you, and I want you to know that what you're feeling is completely valid. Can you tell me more about what's been weighing on your mind?",
            "Thank you for sharing that with me. It takes courage to open up. How has this been affecting your daily life?",
            "I'm here with you through this. What do you think might help you feel more supported right now?"
          ],
          professional: [
            "I understand. Let's examine this situation more closely. What specific aspects concern you most?",
            "Can you identify any patterns or triggers related to what you've described?",
            "From a therapeutic perspective, what coping strategies have you tried before?"
          ],
          gentle: [
            "Take your time. There's no rush here. How would you like to begin exploring this?",
            "I can sense this is difficult to talk about. We can go at whatever pace feels comfortable for you.",
            "Your experience matters deeply. What feels most important for you to share right now?"
          ],
          encouraging: [
            "You've already taken an important step by reaching out. What strengths do you see in yourself?",
            "I believe in your ability to work through this. What progress have you made recently?",
            "You have more resilience than you might realize. How have you overcome challenges before?"
          ],
          analytical: [
            "Let's break this down systematically. What are the key components of this situation?",
            "I'm noticing some interesting themes in what you've shared. How do these connect for you?",
            "From a cognitive perspective, what thoughts seem to be driving these feelings?"
          ]
        };
        
        const personalityResponses = fallbackResponses[personality as keyof typeof fallbackResponses] || fallbackResponses.warm;
        response = personalityResponses[Math.floor(Math.random() * personalityResponses.length)];
      }
      
      res.json({ response });
    } catch (error) {
      console.error("Error generating therapy response:", error);
      res.status(500).json({ 
        error: "Failed to generate response",
        response: "I'm here to listen and support you. Could you share a bit more about what's on your mind?"
      });
    }
  });

  // User Settings API
  app.get("/api/settings/:userId", async (req, res) => {
    try {
      const userId = parseInt(req.params.userId);
      const settings = await storage.getUserSettings(userId);
      
      // Return default settings if none exist
      if (!settings) {
        const defaultSettings = {
          userId,
          voiceEnabled: true,
          speechRate: 0.9,
          speechPitch: 1.1,
          language: 'en-US',
          therapistPersonality: 'warm',
          audioVisualizationEnabled: false
        };
        
        const createdSettings = await storage.createUserSettings(defaultSettings);
        return res.json(createdSettings);
      }
      
      res.json(settings);
    } catch (error) {
      console.error("Error fetching settings:", error);
      res.status(500).json({ error: "Failed to fetch settings" });
    }
  });

  app.post("/api/settings", async (req, res) => {
    try {
      const settingsData = insertUserSettingsSchema.parse(req.body);
      const settings = await storage.createUserSettings(settingsData);
      res.json(settings);
    } catch (error) {
      console.error("Error creating settings:", error);
      res.status(400).json({ error: "Invalid settings data" });
    }
  });

  app.patch("/api/settings/:userId", async (req, res) => {
    try {
      const userId = parseInt(req.params.userId);
      const updateData = req.body;
      const settings = await storage.updateUserSettings(userId, updateData);
      res.json(settings);
    } catch (error) {
      console.error("Error updating settings:", error);
      res.status(500).json({ error: "Failed to update settings" });
    }
  });

  // Audio transcription endpoint (for future Whisper integration)
  app.post("/api/audio/transcribe", async (req, res) => {
    try {
      const { audioData, language = 'en' } = req.body;
      
      // For now, return a placeholder - this would integrate with OpenAI Whisper
      res.json({ 
        text: "Audio transcription not yet implemented",
        confidence: 0.5
      });
    } catch (error) {
      console.error("Error transcribing audio:", error);
      res.status(500).json({ error: "Failed to transcribe audio" });
    }
  });

  // Text-to-speech endpoint (for future integration)
  app.post("/api/audio/synthesize", async (req, res) => {
    try {
      const { text, voice = 'alloy', speed = 1.0 } = req.body;
      
      // For now, return a placeholder - this would integrate with OpenAI TTS
      res.json({ 
        audioUrl: null,
        message: "Text-to-speech not yet implemented"
      });
    } catch (error) {
      console.error("Error synthesizing speech:", error);
      res.status(500).json({ error: "Failed to synthesize speech" });
    }
  });

  return createServer(app);
}