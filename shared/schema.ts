import { pgTable, text, serial, integer, boolean, timestamp, json } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const therapySessions = pgTable("therapy_sessions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  title: text("title").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const therapyMessages = pgTable("therapy_messages", {
  id: serial("id").primaryKey(),
  sessionId: integer("session_id").references(() => therapySessions.id).notNull(),
  content: text("content").notNull(),
  isUser: boolean("is_user").notNull(),
  mood: text("mood"), // For therapist messages: 'idle', 'listening', 'speaking', 'thinking', 'happy', 'concerned'
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const userSettings = pgTable("user_settings", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id).notNull().unique(),
  voiceEnabled: boolean("voice_enabled").default(true).notNull(),
  speechRate: integer("speech_rate").default(90).notNull(), // 0-200, stored as integer (90 = 0.9)
  speechPitch: integer("speech_pitch").default(110).notNull(), // 0-200, stored as integer (110 = 1.1)
  language: text("language").default('en-US').notNull(),
  therapistPersonality: text("therapist_personality").default('warm').notNull(),
  audioVisualizationEnabled: boolean("audio_visualization_enabled").default(false).notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Relations
export const usersRelations = relations(users, ({ many, one }) => ({
  sessions: many(therapySessions),
  settings: one(userSettings),
}));

export const therapySessionsRelations = relations(therapySessions, ({ one, many }) => ({
  user: one(users, {
    fields: [therapySessions.userId],
    references: [users.id],
  }),
  messages: many(therapyMessages),
}));

export const therapyMessagesRelations = relations(therapyMessages, ({ one }) => ({
  session: one(therapySessions, {
    fields: [therapyMessages.sessionId],
    references: [therapySessions.id],
  }),
}));

export const userSettingsRelations = relations(userSettings, ({ one }) => ({
  user: one(users, {
    fields: [userSettings.userId],
    references: [users.id],
  }),
}));

// Insert schemas
export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertTherapySessionSchema = createInsertSchema(therapySessions).pick({
  userId: true,
  title: true,
});

export const insertTherapyMessageSchema = createInsertSchema(therapyMessages).pick({
  sessionId: true,
  content: true,
  isUser: true,
  mood: true,
});

export const insertUserSettingsSchema = createInsertSchema(userSettings).omit({
  id: true,
  updatedAt: true,
});

// Types
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type TherapySession = typeof therapySessions.$inferSelect;
export type InsertTherapySession = z.infer<typeof insertTherapySessionSchema>;
export type TherapyMessage = typeof therapyMessages.$inferSelect;
export type InsertTherapyMessage = z.infer<typeof insertTherapyMessageSchema>;
export type UserSettings = typeof userSettings.$inferSelect;
export type InsertUserSettings = z.infer<typeof insertUserSettingsSchema>;
