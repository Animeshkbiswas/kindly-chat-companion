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

  // User Settings API
  app.get("/api/settings/:userId", async (req, res) => {
    try {
      const userId = parseInt(req.params.userId);
      let settings = await storage.getUserSettings(userId);
      
      // Create default settings if none exist
      if (!settings) {
        settings = await storage.createUserSettings({
          userId,
          voiceEnabled: true,
          speechRate: 90,
          speechPitch: 110,
          language: 'en-US',
          therapistPersonality: 'warm',
          audioVisualizationEnabled: false
        });
      }
      
      res.json(settings);
    } catch (error) {
      console.error("Error fetching settings:", error);
      res.status(500).json({ error: "Failed to fetch settings" });
    }
  });

  app.patch("/api/settings/:userId", async (req, res) => {
    try {
      const userId = parseInt(req.params.userId);
      const settingsData = req.body;
      const settings = await storage.updateUserSettings(userId, settingsData);
      res.json(settings);
    } catch (error) {
      console.error("Error updating settings:", error);
      res.status(500).json({ error: "Failed to update settings" });
    }
  });

  // Demo endpoint to create a test user and session
  app.post("/api/demo/init", async (req, res) => {
    try {
      // Create a demo user
      const user = await storage.createUser({
        username: "demo_user",
        password: "demo_password"
      });

      // Create initial therapy session
      const session = await storage.createTherapySession({
        userId: user.id,
        title: "Initial Therapy Session"
      });

      // Create welcome message
      await storage.createTherapyMessage({
        sessionId: session.id,
        content: "Hello! I'm Dr. Sarah, your virtual therapist. I'm here to listen and help you work through whatever is on your mind. How are you feeling today?",
        isUser: false,
        mood: 'idle'
      });

      res.json({ user, session });
    } catch (error) {
      console.error("Error initializing demo:", error);
      res.status(500).json({ error: "Failed to initialize demo" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
