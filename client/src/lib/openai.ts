// OpenAI integration for therapy chat responses
// the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface TherapyResponse {
  text: string;
  mood: 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned';
}

export async function generateTherapyResponse(
  userMessage: string,
  conversationHistory: { text: string; isUser: boolean }[] = [],
  personality: string = 'warm'
): Promise<string> {
  // Check if OpenAI API key is available
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
  
  if (!apiKey) {
    // Fallback to rule-based responses when no API key
    return generateFallbackResponse(userMessage, personality);
  }

  try {
    // Build conversation context
    const messages: ChatMessage[] = [
      {
        role: 'system',
        content: `You are Dr. Sarah, a compassionate and professional virtual therapist. Your personality is ${personality}. 
        
Guidelines:
- Provide supportive, empathetic responses
- Ask thoughtful follow-up questions
- Use active listening techniques
- Keep responses concise but meaningful (2-3 sentences max)
- Maintain professional therapeutic boundaries
- Show genuine care and understanding
- Use a warm, calming tone
- If someone expresses serious mental health concerns, gently suggest professional help

Remember: You are not a replacement for professional therapy, but a supportive companion for emotional wellness.`
      }
    ];

    // Add conversation history (last 6 messages for context)
    const recentHistory = conversationHistory.slice(-6);
    recentHistory.forEach(msg => {
      messages.push({
        role: msg.isUser ? 'user' : 'assistant',
        content: msg.text
      });
    });

    // Add current user message
    messages.push({
      role: 'user',
      content: userMessage
    });

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
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

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const responseText = data.choices[0]?.message?.content || '';

    return responseText;

  } catch (error) {
    console.error('OpenAI API error:', error);
    // Fallback to rule-based response on error
    return generateFallbackResponse(userMessage, personality);
  }
}

function generateFallbackResponse(userMessage: string, personality: string): string {
  const message = userMessage.toLowerCase();
  
  // Emotion detection patterns
  const emotions = {
    sad: ['sad', 'depressed', 'down', 'upset', 'cry', 'hurt', 'pain'],
    anxious: ['anxious', 'worry', 'nervous', 'stress', 'panic', 'afraid', 'scared'],
    angry: ['angry', 'mad', 'furious', 'frustrated', 'annoyed', 'rage'],
    happy: ['happy', 'good', 'great', 'excited', 'joy', 'wonderful', 'amazing'],
    confused: ['confused', 'lost', 'don\'t know', 'unsure', 'unclear']
  };

  let detectedEmotion = 'neutral';
  let mood: 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned' = 'idle';

  // Detect primary emotion
  for (const [emotion, keywords] of Object.entries(emotions)) {
    if (keywords.some(keyword => message.includes(keyword))) {
      detectedEmotion = emotion;
      break;
    }
  }

  // Response templates based on personality and emotion
  const responses = {
    warm: {
      sad: [
        "I can hear the pain in your words, and I want you to know that your feelings are completely valid. What do you think might help you feel a little lighter today?",
        "It sounds like you're going through a really difficult time. Remember that it's okay to not be okay. What's one small thing that usually brings you comfort?",
        "Thank you for sharing something so personal with me. Your courage to open up shows real strength. How long have you been feeling this way?"
      ],
      anxious: [
        "It sounds like anxiety is really weighing on you right now. Let's take a moment to breathe together. What specific thoughts are making you feel most worried?",
        "Anxiety can feel so overwhelming, but you're not alone in this. Have you noticed any particular triggers that make these feelings stronger?",
        "I can sense the tension you're carrying. Sometimes naming our fears can help reduce their power. What's the worst-case scenario you're imagining?"
      ],
      angry: [
        "Your anger makes complete sense given what you're dealing with. It's actually a sign that something important to you has been affected. What do you think is at the core of these feelings?",
        "I can feel the intensity of your emotions, and that's okay. Anger often protects other feelings underneath. What might those feelings be?",
        "It takes courage to express anger constructively. What would it look like if this situation were resolved in a way that felt right to you?"
      ],
      happy: [
        "I love hearing the joy in your words! It's wonderful that you're experiencing happiness. What's contributing most to these positive feelings?",
        "Your happiness is contagious, even through our conversation. I'm curious - what made this moment special for you?",
        "It's beautiful to witness someone in a good place. How can you nurture and sustain these positive feelings?"
      ],
      confused: [
        "Feeling uncertain can be really uncomfortable, but it often means you're on the verge of important growth. What aspects of the situation feel clearest to you?",
        "Confusion is a natural part of processing complex experiences. Let's explore this together - what questions are coming up for you most strongly?",
        "Sometimes sitting with uncertainty teaches us valuable things about ourselves. What would help you feel more grounded right now?"
      ],
      neutral: [
        "I'm here to listen to whatever you'd like to share. What's been on your mind lately?",
        "Thank you for being here with me today. How are you feeling in this moment?",
        "I appreciate you taking this time for yourself. What would be most helpful to talk about right now?"
      ]
    }
  };

  // Set mood based on detected emotion
  switch (detectedEmotion) {
    case 'sad':
    case 'anxious':
    case 'angry':
      mood = 'concerned';
      break;
    case 'happy':
      mood = 'happy';
      break;
    case 'confused':
      mood = 'thinking';
      break;
    default:
      mood = 'idle';
  }

  // Get random response from appropriate category
  const responseCategory = responses[personality as keyof typeof responses] || responses.warm;
  const categoryResponses = responseCategory[detectedEmotion as keyof typeof responseCategory] || responseCategory.neutral;
  const randomResponse = categoryResponses[Math.floor(Math.random() * categoryResponses.length)];

  return randomResponse;
}

function determineMoodFromResponse(responseText: string, userMessage: string): 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned' {
  const response = responseText.toLowerCase();
  const user = userMessage.toLowerCase();
  
  // Analyze user's emotional state and therapist's response
  if (user.includes('happy') || user.includes('great') || user.includes('wonderful') || 
      response.includes('wonderful') || response.includes('glad')) {
    return 'happy';
  }
  
  if (user.includes('sad') || user.includes('depressed') || user.includes('anxious') || 
      user.includes('worry') || user.includes('scared') || user.includes('hurt') ||
      response.includes('sorry') || response.includes('difficult') || response.includes('understand')) {
    return 'concerned';
  }
  
  if (response.includes('?') || response.includes('tell me more') || response.includes('explore')) {
    return 'thinking';
  }
  
  return 'idle';
}