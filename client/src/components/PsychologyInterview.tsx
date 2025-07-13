import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Upload, Download, Mic, MicOff, Play, Pause } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  audioData?: string;
}

interface Interviewer {
  id: string;
  name: string;
  description: string;
  voice: string;
  personality: string;
}

interface InterviewState {
  sessionId?: number;
  questionCount: number;
  totalQuestions: number;
  isComplete: boolean;
  isRecording: boolean;
  isPlaying: boolean;
  currentAudio?: HTMLAudioElement;
}

export const PsychologyInterview: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [interviewState, setInterviewState] = useState<InterviewState>({
    questionCount: 0,
    totalQuestions: 25,
    isComplete: false,
    isRecording: false,
    isPlaying: false
  });
  const [selectedInterviewer, setSelectedInterviewer] = useState<string>('sarah');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('english');
  const [interviewers, setInterviewers] = useState<Interviewer[]>([]);
  const [reportContent, setReportContent] = useState<string>('');
  const [reportPdfPath, setReportPdfPath] = useState<string>('');

  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const { toast } = useToast();

  // Load available interviewers
  useEffect(() => {
    const fetchInterviewers = async () => {
      try {
        const response = await fetch('/api/psychology/interviewers');
        if (!response.ok) throw new Error('Failed to fetch interviewers');
        const data = await response.json();
        console.log('Fetched interviewers:', data);
        if (Array.isArray(data.interviewers) && data.interviewers.length > 0) {
          setInterviewers(data.interviewers);
          // If the current selectedInterviewer is not in the list, set to the first one
          if (!data.interviewers.some(i => i.id === selectedInterviewer)) {
            setSelectedInterviewer(data.interviewers[0].id);
          }
        } else {
          setInterviewers([]);
        }
      } catch (error) {
        console.error('Error fetching interviewers:', error);
        setInterviewers([]);
      }
    };
    fetchInterviewers();
  }, []);

  // Debug logging
  console.log('selectedInterviewer:', selectedInterviewer);
  console.log('interviewers state:', interviewers);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const startInterview = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/psychology/start-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interviewer: selectedInterviewer,
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start interview');
      }

      const data = await response.json();
      
      setInterviewState(prev => ({
        ...prev,
        sessionId: data.session_id,
        questionCount: data.question_count,
      }));

      const initialMessage: Message = {
        id: Date.now().toString(),
        text: data.message,
        isUser: false,
        timestamp: new Date(),
        audioData: data.audio_data ? `data:audio/mp3;base64,${btoa(String.fromCharCode(...new Uint8Array(data.audio_data)))}` : undefined
      };

      setMessages([initialMessage]);

      // Play audio if available
      if (data.audio_data) {
        playAudio(data.audio_data);
      }

      toast({
        title: "Interview Started",
        description: `Welcome to your session with ${interviewers.find(i => i.id === selectedInterviewer)?.name || 'your interviewer'}`,
      });

    } catch (error) {
      console.error('Error starting interview:', error);
      toast({
        title: "Error",
        description: "Failed to start interview",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const continueInterview = async (userMessage: string) => {
    if (!interviewState.sessionId) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/psychology/continue-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: interviewState.sessionId,
          user_message: userMessage,
          interviewer: selectedInterviewer,
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to continue interview');
      }

      const data = await response.json();

      // Add user message
      const userMsg: Message = {
        id: Date.now().toString(),
        text: userMessage,
        isUser: true,
        timestamp: new Date(),
      };

      // Add AI response
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: data.message,
        isUser: false,
        timestamp: new Date(),
        audioData: data.audio_data ? `data:audio/mp3;base64,${btoa(String.fromCharCode(...new Uint8Array(data.audio_data)))}` : undefined
      };

      setMessages(prev => [...prev, userMsg, aiMsg]);

      setInterviewState(prev => ({
        ...prev,
        questionCount: data.question_count,
        isComplete: data.is_complete,
      }));

      // Play audio if available
      if (data.audio_data) {
        playAudio(data.audio_data);
      }

      // Generate report if interview is complete
      if (data.is_complete) {
        generateReport();
      }

    } catch (error) {
      console.error('Error continuing interview:', error);
      toast({
        title: "Error",
        description: "Failed to continue interview",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async () => {
    if (!interviewState.sessionId) return;

    try {
      const response = await fetch(`/api/psychology/generate-report/${interviewState.sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: selectedLanguage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const data = await response.json();
      setReportContent(data.report_content);
      setReportPdfPath(data.pdf_path);

      toast({
        title: "Report Generated",
        description: "Your clinical report is ready for download",
      });

    } catch (error) {
      console.error('Error generating report:', error);
      toast({
        title: "Error",
        description: "Failed to generate report",
        variant: "destructive",
      });
    }
  };

  const analyzeDocument = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', selectedLanguage);

    try {
      const response = await fetch('/api/psychology/analyze-document', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze document');
      }

      const data = await response.json();
      setReportContent(data.report_content);
      setReportPdfPath(data.pdf_path);

      toast({
        title: "Document Analyzed",
        description: "Analysis complete. Report ready for download.",
      });

    } catch (error) {
      console.error('Error analyzing document:', error);
      toast({
        title: "Error",
        description: "Failed to analyze document",
        variant: "destructive",
      });
    }
  };

  const playAudio = (audioData: any) => {
    try {
      const audioBlob = new Blob([new Uint8Array(audioData)], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      setInterviewState(prev => ({ ...prev, isPlaying: true, currentAudio: audio }));
      
      audio.onended = () => {
        setInterviewState(prev => ({ ...prev, isPlaying: false, currentAudio: undefined }));
        URL.revokeObjectURL(audioUrl);
      };
      
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        // Here you would typically send the audio to the backend for transcription
        // For now, we'll just show a placeholder
        toast({
          title: "Audio Recorded",
          description: "Audio recording completed. Please type your response.",
        });
      };

      mediaRecorder.start();
      setInterviewState(prev => ({ ...prev, isRecording: true }));

    } catch (error) {
      console.error('Error starting recording:', error);
      toast({
        title: "Error",
        description: "Failed to start recording",
        variant: "destructive",
      });
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && interviewState.isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setInterviewState(prev => ({ ...prev, isRecording: false }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    continueInterview(inputText.trim());
    setInputText('');
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      analyzeDocument(file);
    }
  };

  const downloadReport = () => {
    if (reportPdfPath) {
      window.open(`/api/psychology/download-report/${reportPdfPath.split('/').pop()}`, '_blank');
    }
  };

  const resetInterview = () => {
    setMessages([]);
    setInterviewState({
      questionCount: 0,
      totalQuestions: 25,
      isComplete: false,
      isRecording: false,
      isPlaying: false
    });
    setReportContent('');
    setReportPdfPath('');
  };

  const selectedInterviewerData = interviewers.find(i => i.id === selectedInterviewer);

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🧠 Psychology Interview
            <Badge variant={interviewState.isComplete ? "default" : "secondary"}>
              {interviewState.isComplete ? "Complete" : "Active"}
            </Badge>
          </CardTitle>
          <CardDescription>
            Clinical psychology interview with AI-powered analysis and report generation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-sm font-medium">Interviewer</label>
              <Select value={selectedInterviewer} onValueChange={setSelectedInterviewer}>
                <SelectTrigger>
                  <SelectValue placeholder="Select interviewer" />
                </SelectTrigger>
                <SelectContent>
                  {interviewers.length === 0 && (
                    <div className="p-2 text-muted-foreground">No interviewers available</div>
                  )}
                  {interviewers.map((interviewer) => (
                    <SelectItem key={interviewer.id} value={interviewer.id}>
                      {interviewer.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {selectedInterviewerData && (
                <p className="text-xs text-muted-foreground mt-1">
                  {selectedInterviewerData.description}
                </p>
              )}
            </div>
            <div>
              <label className="text-sm font-medium">Language</label>
              <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="english">English</SelectItem>
                  <SelectItem value="spanish">Spanish</SelectItem>
                  <SelectItem value="french">French</SelectItem>
                  <SelectItem value="german">German</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {interviewState.questionCount === 0 && (
            <Button 
              onClick={startInterview} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? "Starting..." : "Start Interview"}
            </Button>
          )}

          {interviewState.questionCount > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Progress 
                  value={(interviewState.questionCount / interviewState.totalQuestions) * 100} 
                  className="flex-1"
                />
                <span className="text-sm text-muted-foreground">
                  {interviewState.questionCount}/{interviewState.totalQuestions}
                </span>
              </div>
              <Button 
                onClick={resetInterview} 
                variant="outline" 
                size="sm"
              >
                Reset Interview
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="interview" className="flex-1">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="interview">Interview</TabsTrigger>
          <TabsTrigger value="document">Document Analysis</TabsTrigger>
          <TabsTrigger value="report">Report</TabsTrigger>
        </TabsList>

        <TabsContent value="interview" className="flex-1">
          <Card className="flex-1">
            <CardContent className="p-4">
              <ScrollArea ref={scrollAreaRef} className="h-96 mb-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-3",
                        message.isUser ? "justify-end" : "justify-start"
                      )}
                    >
                      <div
                        className={cn(
                          "max-w-[80%] rounded-lg p-3",
                          message.isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        )}
                      >
                        <p className="text-sm">{message.text}</p>
                        {message.audioData && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-2"
                            onClick={() => {
                              const audio = new Audio(message.audioData);
                              audio.play();
                            }}
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted rounded-lg p-3">
                        <p className="text-sm">Thinking...</p>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {interviewState.questionCount > 0 && !interviewState.isComplete && (
                <form onSubmit={handleSubmit} className="flex gap-2">
                  <Input
                    ref={inputRef}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Type your response..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={interviewState.isRecording ? stopRecording : startRecording}
                    disabled={isLoading}
                  >
                    {interviewState.isRecording ? (
                      <MicOff className="h-4 w-4" />
                    ) : (
                      <Mic className="h-4 w-4" />
                    )}
                  </Button>
                  <Button type="submit" disabled={!inputText.trim() || isLoading}>
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="document" className="flex-1">
          <Card className="flex-1">
            <CardHeader>
              <CardTitle>Document Analysis</CardTitle>
              <CardDescription>
                Upload a document (TXT, PDF, DOCX) for clinical analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                <Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground mb-4">
                  Upload a document to generate a clinical report
                </p>
                <input
                  type="file"
                  accept=".txt,.pdf,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="document-upload"
                />
                <label htmlFor="document-upload">
                  <Button asChild>
                    <span>Choose File</span>
                  </Button>
                </label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="report" className="flex-1">
          <Card className="flex-1">
            <CardHeader>
              <CardTitle>Clinical Report</CardTitle>
              <CardDescription>
                Generated clinical analysis and recommendations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reportContent ? (
                <div className="space-y-4">
                  <div className="bg-muted rounded-lg p-4 max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm">{reportContent}</pre>
                  </div>
                  {reportPdfPath && (
                    <Button onClick={downloadReport} className="w-full">
                      <Download className="h-4 w-4 mr-2" />
                      Download PDF Report
                    </Button>
                  )}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  <p>No report generated yet.</p>
                  <p className="text-sm">Complete an interview or upload a document to generate a report.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 