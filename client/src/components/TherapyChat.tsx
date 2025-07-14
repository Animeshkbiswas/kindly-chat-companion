import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { TherapistCharacter } from './TherapistCharacter';
import { ChatMessage } from './ChatMessage';
import { EnhancedVoiceInput } from './EnhancedVoiceInput';
import { TherapySettings } from './TherapySettings';
import { AudioVisualizationToggle } from './AudioVisualizationToggle';
import { useSpeechSynthesis } from './SpeechSynthesis';
import { useAudioVisualization } from '@/hooks/useAudioVisualization';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { apiService } from '@/lib/api';
import { useSettings } from '@/hooks/useSettings';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

type CharacterMood = 'idle' | 'listening' | 'speaking' | 'thinking' | 'happy' | 'concerned';

export const TherapyChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm Dr. Sarah, your virtual therapist. I'm here to listen and help you work through whatever is on your mind. How are you feeling today?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [characterMood, setCharacterMood] = useState<CharacterMood>('idle');
  const [isListening, setIsListening] = useState(false);
  const { settings, updateSettings } = useSettings();

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { speak, stop, isSpeaking } = useSpeechSynthesis();
  const { 
    audioData, 
    isEnabled: isAudioVisualizationEnabled, 
    isSupported: isAudioVisualizationSupported,
    startAudioVisualization, 
    stopAudioVisualization 
  } = useAudioVisualization();
  const { toast } = useToast();

  // Update character mood based on real-time audio
  useEffect(() => {
    if (audioData.isUserSpeaking && isAudioVisualizationEnabled) {
      setCharacterMood('listening');
    } else if (isSpeaking) {
      setCharacterMood('speaking');
    } else if (isListening) {
      setCharacterMood('listening');
    } else if (isTyping) {
      setCharacterMood('thinking');
    } else {
      setCharacterMood('idle');
    }
  }, [isSpeaking, isListening, isTyping, audioData.isUserSpeaking, isAudioVisualizationEnabled]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, isTyping]);


  // Generate AI response using backend API
  const generateAIResponse = useCallback(async (userMessage: string): Promise<string> => {
    try {
      // Use backend API for chat responses
      const response = await apiService.sendChatMessage({
        message: userMessage,
        therapist_personality: settings.therapistPersonality,
        language: settings.language,
      });
      
      return response.response;
    } catch (error) {
      console.error('Backend API error:', error);
      
      // Fallback personality-based responses
      const responses = {
        warm: [
          "I hear you, and I want you to know that what you're feeling is completely valid. Can you tell me more about what's been weighing on your mind?",
          "Thank you for sharing that with me. It takes courage to open up. How has this been affecting your daily life?",
          "I'm here with you through this. What do you think might help you feel more supported right now?",
          "Your feelings are important, and I'm grateful you trust me with them. What would you like to explore together?",
          "That sounds really challenging. You're not alone in feeling this way. What resources or support do you have in your life?"
        ],
        professional: [
          "I understand. Let's examine this situation more closely. What specific aspects concern you most?",
          "Can you identify any patterns or triggers related to what you've described?",
          "From a therapeutic perspective, what coping strategies have you tried before?",
          "Let's work together to develop some concrete steps forward. What are your primary goals?",
          "What evidence do you have that supports or challenges these thoughts you're experiencing?"
        ],
        gentle: [
          "Take your time. There's no rush here. How would you like to begin exploring this?",
          "I can sense this is difficult to talk about. We can go at whatever pace feels comfortable for you.",
          "Your experience matters deeply. What feels most important for you to share right now?",
          "It's okay to feel uncertain. What small step forward might feel manageable today?",
          "You're being so brave by being here. What would feel most helpful for you in this moment?"
        ],
        encouraging: [
          "You've already taken an important step by reaching out. What strengths do you see in yourself?",
          "I believe in your ability to work through this. What progress have you made recently?",
          "You have more resilience than you might realize. How have you overcome challenges before?",
          "This conversation shows your commitment to growth. What motivates you to keep moving forward?",
          "You're capable of positive change. What would that change look like for you?"
        ],
        analytical: [
          "Let's break this down systematically. What are the key components of this situation?",
          "I'm noticing some interesting themes in what you've shared. How do these connect for you?",
          "From a cognitive perspective, what thoughts seem to be driving these feelings?",
          "What underlying beliefs might be influencing your current experience?",
          "Let's examine the relationship between your thoughts, feelings, and behaviors here."
        ]
      };

      const personalityResponses = responses[settings.therapistPersonality as keyof typeof responses] || responses.warm;
      return personalityResponses[Math.floor(Math.random() * personalityResponses.length)];
    }
  }, [settings.therapistPersonality, settings.language]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setCharacterMood('thinking');

    try {
      // Generate AI response using enhanced function
      const responseText = await generateAIResponse(text.trim());
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
      setCharacterMood('idle');

      // Speak the response if voice is enabled with user settings
      if (settings.voiceEnabled) {
        setCharacterMood('speaking');
        setTimeout(() => {
          speak(responseText, {
            rate: settings.speechRate,
            pitch: settings.speechPitch,
            language: settings.language,
            voiceEnabled: settings.voiceEnabled,
            useBackend: true // Use backend TTS
          });
        }, 500);
      }
    } catch (error) {
      console.error('Error generating response:', error);
      
      // Fallback response on error
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm here to listen and support you. Could you share a bit more about what's on your mind?",
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, fallbackMessage]);
      setIsTyping(false);
      setCharacterMood('idle');

      toast({
        title: "Connection Issue",
        description: "Having trouble connecting. Using basic responses for now.",
        variant: "destructive",
      });
    }
  }, [generateAIResponse, settings, speak, messages, toast]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  const handleVoiceTranscript = (transcript: string) => {
    setInputText(transcript);
    // Auto-send after a brief pause
    setTimeout(() => {
      if (transcript.trim()) {
        sendMessage(transcript);
      }
    }, 1000);
  };

  const clearChat = () => {
    setMessages([{
      id: '1',
      text: "Hello! I'm Dr. Sarah, your virtual therapist. I'm here to listen and help you work through whatever is on your mind. How are you feeling today?",
      isUser: false,
      timestamp: new Date()
    }]);
    stop(); // Stop any ongoing speech
    toast({
      title: "Chat Cleared",
      description: "Starting fresh with a new conversation."
    });
  };

  // Sync audio visualization with settings
  useEffect(() => {
    if (settings.audioVisualizationEnabled && !isAudioVisualizationEnabled) {
      startAudioVisualization();
    } else if (!settings.audioVisualizationEnabled && isAudioVisualizationEnabled) {
      stopAudioVisualization();
    }
  }, [settings.audioVisualizationEnabled, isAudioVisualizationEnabled, startAudioVisualization, stopAudioVisualization]);

  const handleAudioVisualizationToggle = () => {
    updateSettings({
      audioVisualizationEnabled: !settings.audioVisualizationEnabled
    });
  };

  return (
    <div className="min-h-screen bg-gradient-main flex flex-col lg:flex-row">
      {/* Character Section */}
      <div className="lg:w-1/3 flex flex-col items-center justify-center p-6 bg-gradient-to-b from-therapy-gentle/30 to-transparent">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-primary mb-2">Dr. Sarah</h1>
          <p className="text-muted-foreground">Your Virtual Therapist</p>
          {isAudioVisualizationEnabled && (
            <p className="text-xs text-primary mt-1">Real-time audio enabled</p>
          )}
        </div>
        
        <TherapistCharacter
          mood={characterMood}
          isListening={isListening || (isAudioVisualizationEnabled && audioData.isUserSpeaking)}
          isSpeaking={isSpeaking}
          audioLevel={audioData.audioLevel}
          audioIntensity={audioData.intensity}
          className="mb-6"
        />
        
        <div className="flex gap-2 flex-wrap justify-center">
          <TherapySettings
            settings={settings}
            onSettingsChange={updateSettings}
          />
          <AudioVisualizationToggle
            isEnabled={isAudioVisualizationEnabled}
            isSupported={isAudioVisualizationSupported}
            onToggle={handleAudioVisualizationToggle}
            disabled={isTyping}
          />
          <Button
            variant="outline"
            size="icon"
            onClick={clearChat}
            className="shadow-gentle hover:shadow-soft transition-all duration-300"
            aria-label="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Chat Section */}
      <div className="lg:w-2/3 flex flex-col h-screen lg:h-auto">
        {/* Chat Messages */}
        <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
          <div className="space-y-4 max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
            ))}
            
            {isTyping && (
              <ChatMessage
                message=""
                isUser={false}
                isTyping={true}
              />
            )}
          </div>
        </ScrollArea>

        {/* Input Section */}
        <div className="p-4 bg-card/50 backdrop-blur-sm border-t">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Share what's on your mind..."
                disabled={isTyping}
                className={cn(
                  'flex-1 shadow-gentle focus:shadow-soft transition-all duration-300',
                  'bg-background/80 backdrop-blur-sm'
                )}
                aria-label="Type your message"
              />
              
              <EnhancedVoiceInput
                onTranscript={handleVoiceTranscript}
                onStartListening={() => setIsListening(true)}
                onStopListening={() => setIsListening(false)}
                disabled={isTyping}
                useWhisper={true}
                language={settings.language}
              />
              
              <Button
                type="submit"
                disabled={!inputText.trim() || isTyping}
                className={cn(
                  'shadow-gentle hover:shadow-soft transition-all duration-300',
                  'hover:scale-105'
                )}
                aria-label="Send message"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </form>
          
          <p className="text-xs text-muted-foreground text-center mt-2">
            This is a simulated therapy experience for demonstration purposes.
          </p>
        </div>
      </div>
    </div>
  );
};