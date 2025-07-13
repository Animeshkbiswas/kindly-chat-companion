import { useState } from 'react';
import { TherapyChat } from '@/components/TherapyChat';
import { PsychologyInterview } from '@/components/PsychologyInterview';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, MessageCircle } from 'lucide-react';

const Index = () => {
  const [mode, setMode] = useState<'therapy' | 'psychology'>('therapy');

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        {/* Mode Selection */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-center">Choose Your Session Type</CardTitle>
            <CardDescription className="text-center">
              Select between regular therapy chat or structured psychology interview
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                variant={mode === 'therapy' ? 'default' : 'outline'}
                size="lg"
                onClick={() => setMode('therapy')}
                className="h-24 flex flex-col gap-2"
              >
                <MessageCircle className="h-6 w-6" />
                <span>Regular Therapy Chat</span>
                <span className="text-xs opacity-70">Free-form conversation</span>
              </Button>
              <Button
                variant={mode === 'psychology' ? 'default' : 'outline'}
                size="lg"
                onClick={() => setMode('psychology')}
                className="h-24 flex flex-col gap-2"
              >
                <Brain className="h-6 w-6" />
                <span>Psychology Interview</span>
                <span className="text-xs opacity-70">Structured clinical assessment</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Content */}
        {mode === 'therapy' ? <TherapyChat /> : <PsychologyInterview />}
      </div>
    </div>
  );
};

export default Index;
