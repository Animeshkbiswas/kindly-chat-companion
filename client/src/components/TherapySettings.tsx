import React from 'react';
import { Settings, Volume2, VolumeX, Languages } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Separator } from '@/components/ui/separator';

interface TherapySettingsProps {
  settings: {
    voiceEnabled: boolean;
    speechRate: number;
    speechPitch: number;
    language: string;
    therapistPersonality: string;
    audioVisualizationEnabled: boolean;
  };
  onSettingsChange: (settings: any) => void;
}

export const TherapySettings: React.FC<TherapySettingsProps> = ({
  settings,
  onSettingsChange
}) => {
  const handleSettingChange = (key: string, value: any) => {
    onSettingsChange({
      [key]: value
    });
  };

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button 
          variant="outline" 
          size="icon"
          className="shadow-gentle hover:shadow-soft transition-all duration-300"
          aria-label="Open therapy settings"
        >
          <Settings className="w-4 h-4" />
        </Button>
      </SheetTrigger>
      
      <SheetContent className="w-80 bg-gradient-card">
        <SheetHeader>
          <SheetTitle className="text-primary">Therapy Settings</SheetTitle>
          <SheetDescription>
            Customize your therapy session experience
          </SheetDescription>
        </SheetHeader>
        
        <div className="mt-6 space-y-6">
          {/* Voice Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              {settings.voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              Voice Settings
            </h3>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="voice-enabled" className="text-sm">
                Enable voice responses
              </Label>
              <Switch
                id="voice-enabled"
                checked={settings.voiceEnabled}
                onCheckedChange={(checked) => handleSettingChange('voiceEnabled', checked)}
              />
            </div>
            
            {settings.voiceEnabled && (
              <>
                <div className="space-y-2">
                  <Label className="text-sm">Speech Rate</Label>
                  <Slider
                    value={[settings.speechRate]}
                    onValueChange={([value]) => handleSettingChange('speechRate', value)}
                    min={0.5}
                    max={2}
                    step={0.1}
                    className="w-full"
                  />
                  <div className="text-xs text-muted-foreground text-center">
                    {settings.speechRate.toFixed(1)}x
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label className="text-sm">Speech Pitch</Label>
                  <Slider
                    value={[settings.speechPitch]}
                    onValueChange={([value]) => handleSettingChange('speechPitch', value)}
                    min={0.5}
                    max={2}
                    step={0.1}
                    className="w-full"
                  />
                  <div className="text-xs text-muted-foreground text-center">
                    {settings.speechPitch.toFixed(1)}x
                  </div>
                </div>
              </>
            )}
          </div>
          
          <Separator />
          
          {/* Language Settings */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-foreground flex items-center gap-2">
              <Languages className="w-4 h-4" />
              Language
            </h3>
            
            <Select
              value={settings.language}
              onValueChange={(value) => handleSettingChange('language', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en-US">English (US)</SelectItem>
                <SelectItem value="en-GB">English (UK)</SelectItem>
                <SelectItem value="es-ES">Spanish</SelectItem>
                <SelectItem value="fr-FR">French</SelectItem>
                <SelectItem value="de-DE">German</SelectItem>
                <SelectItem value="it-IT">Italian</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <Separator />
          
          {/* Therapist Personality */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-foreground">
              Therapist Personality
            </h3>
            
            <Select
              value={settings.therapistPersonality}
              onValueChange={(value) => handleSettingChange('therapistPersonality', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select personality" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="warm">Warm & Nurturing</SelectItem>
                <SelectItem value="professional">Professional & Direct</SelectItem>
                <SelectItem value="gentle">Gentle & Patient</SelectItem>
                <SelectItem value="encouraging">Encouraging & Motivational</SelectItem>
                <SelectItem value="analytical">Analytical & Thoughtful</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="text-xs text-muted-foreground">
              {settings.therapistPersonality === 'warm' && 
                "Dr. Sarah will be extra warm and nurturing in her responses."}
              {settings.therapistPersonality === 'professional' && 
                "Dr. Sarah will maintain a professional and direct approach."}
              {settings.therapistPersonality === 'gentle' && 
                "Dr. Sarah will be extra gentle and patient with her guidance."}
              {settings.therapistPersonality === 'encouraging' && 
                "Dr. Sarah will focus on encouragement and motivation."}
              {settings.therapistPersonality === 'analytical' && 
                "Dr. Sarah will provide more analytical and thoughtful insights."}
            </div>
          </div>
          
          <Separator />
          
          {/* Audio Visualization */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-foreground">
              Audio Visualization
            </h3>
            
            <div className="flex items-center justify-between">
              <Label htmlFor="audio-viz-enabled" className="text-sm">
                Enable real-time audio visualization
              </Label>
              <Switch
                id="audio-viz-enabled"
                checked={settings.audioVisualizationEnabled}
                onCheckedChange={(checked) => handleSettingChange('audioVisualizationEnabled', checked)}
              />
            </div>
            
            <div className="text-xs text-muted-foreground">
              {settings.audioVisualizationEnabled 
                ? "Shows visual feedback while you speak and listen."
                : "Audio visualization is disabled for better performance."}
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};