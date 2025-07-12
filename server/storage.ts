import { 
  users, 
  therapySessions, 
  therapyMessages, 
  userSettings,
  type User, 
  type InsertUser,
  type TherapySession,
  type InsertTherapySession,
  type TherapyMessage,
  type InsertTherapyMessage,
  type UserSettings,
  type InsertUserSettings
} from "../shared/schema.js";
import { db } from "./db.js";
import { eq, desc, and } from "drizzle-orm";

export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Therapy session methods
  createTherapySession(session: InsertTherapySession): Promise<TherapySession>;
  getUserSessions(userId: number): Promise<TherapySession[]>;
  getSession(sessionId: number): Promise<TherapySession | undefined>;
  updateSessionTitle(sessionId: number, title: string): Promise<void>;
  
  // Therapy message methods
  createTherapyMessage(message: InsertTherapyMessage): Promise<TherapyMessage>;
  getSessionMessages(sessionId: number): Promise<TherapyMessage[]>;
  
  // User settings methods
  getUserSettings(userId: number): Promise<UserSettings | undefined>;
  createUserSettings(settings: InsertUserSettings): Promise<UserSettings>;
  updateUserSettings(userId: number, settings: Partial<InsertUserSettings>): Promise<UserSettings>;
}

export class DatabaseStorage implements IStorage {
  // User methods
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(insertUser)
      .returning();
    return user;
  }

  // Therapy session methods
  async createTherapySession(insertSession: InsertTherapySession): Promise<TherapySession> {
    const [session] = await db
      .insert(therapySessions)
      .values(insertSession)
      .returning();
    return session;
  }

  async getUserSessions(userId: number): Promise<TherapySession[]> {
    return await db
      .select()
      .from(therapySessions)
      .where(eq(therapySessions.userId, userId))
      .orderBy(desc(therapySessions.updatedAt));
  }

  async getSession(sessionId: number): Promise<TherapySession | undefined> {
    const [session] = await db
      .select()
      .from(therapySessions)
      .where(eq(therapySessions.id, sessionId));
    return session || undefined;
  }

  async updateSessionTitle(sessionId: number, title: string): Promise<void> {
    await db
      .update(therapySessions)
      .set({ title, updatedAt: new Date() })
      .where(eq(therapySessions.id, sessionId));
  }

  // Therapy message methods
  async createTherapyMessage(insertMessage: InsertTherapyMessage): Promise<TherapyMessage> {
    const [message] = await db
      .insert(therapyMessages)
      .values(insertMessage)
      .returning();
    return message;
  }

  async getSessionMessages(sessionId: number): Promise<TherapyMessage[]> {
    return await db
      .select()
      .from(therapyMessages)
      .where(eq(therapyMessages.sessionId, sessionId))
      .orderBy(therapyMessages.createdAt);
  }

  // User settings methods
  async getUserSettings(userId: number): Promise<UserSettings | undefined> {
    const [settings] = await db
      .select()
      .from(userSettings)
      .where(eq(userSettings.userId, userId));
    return settings || undefined;
  }

  async createUserSettings(insertSettings: InsertUserSettings): Promise<UserSettings> {
    const [settings] = await db
      .insert(userSettings)
      .values(insertSettings)
      .returning();
    return settings;
  }

  async updateUserSettings(userId: number, updateSettings: Partial<InsertUserSettings>): Promise<UserSettings> {
    const [settings] = await db
      .update(userSettings)
      .set({ ...updateSettings, updatedAt: new Date() })
      .where(eq(userSettings.userId, userId))
      .returning();
    return settings;
  }
}

export const storage = new DatabaseStorage();
