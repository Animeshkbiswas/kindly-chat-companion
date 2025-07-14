import React from 'react';
import { cn } from '@/lib/utils';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
  isTyping?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  timestamp,
  isTyping = false
}) => {
  return (
    <div className={cn(
      'flex gap-3 p-4 rounded-lg transition-all duration-300',
      'hover:shadow-gentle animate-fade-in',
      isUser ? 'bg-gradient-primary text-primary-foreground ml-8' : 'bg-gradient-card mr-8'
    )}>
      {/* Avatar */}
      <div className={cn(
        'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
        'shadow-soft',
        isUser ? 'bg-primary-foreground/20' : 'bg-primary/10'
      )}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4 text-primary" />
        )}
      </div>

      {/* Message content */}
      <div className="flex-1 space-y-1">
        <div className={cn(
          'text-sm font-medium',
          isUser ? 'text-primary-foreground/90 user-message-name' : 'text-primary'
        )}>
          {isUser ? 'You' : 'Dr. Sarah'}
        </div>
        
        <div className={cn(
          'text-sm leading-relaxed break-words overflow-x-auto',
          isUser ? 'text-primary-foreground user-message-content' : 'text-foreground'
        )}>
          {isTyping ? (
            <div className="flex items-center gap-1">
              <span>Thinking</span>
              <div className="flex gap-1">
                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-1 h-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          ) : (
            message
          )}
        </div>
        
        {timestamp && !isTyping && (
          <div className={cn(
            'text-xs opacity-60',
            isUser ? 'text-primary-foreground' : 'text-muted-foreground'
          )}>
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </div>
  );
};