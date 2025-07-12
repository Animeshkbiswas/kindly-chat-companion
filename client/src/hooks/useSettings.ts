import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface TherapySettings {
  voiceEnabled: boolean;
  speechRate: number;
  speechPitch: number;
  language: string;
  therapistPersonality: string;
  audioVisualizationEnabled: boolean;
}

const DEFAULT_SETTINGS: TherapySettings = {
  voiceEnabled: true,
  speechRate: 0.9,
  speechPitch: 1.1,
  language: 'en-US',
  therapistPersonality: 'warm',
  audioVisualizationEnabled: false,
};

export function useSettings() {
  const queryClient = useQueryClient();
  const [localSettings, setLocalSettings] = useState<TherapySettings>(DEFAULT_SETTINGS);

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('therapy-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setLocalSettings({ ...DEFAULT_SETTINGS, ...parsed });
      } catch (error) {
        console.warn('Failed to parse saved settings:', error);
      }
    }
  }, []);

  // Save settings to localStorage whenever they change
  const updateSettings = (newSettings: Partial<TherapySettings>) => {
    const updatedSettings = { ...localSettings, ...newSettings };
    setLocalSettings(updatedSettings);
    localStorage.setItem('therapy-settings', JSON.stringify(updatedSettings));
  };

  // Reset settings to defaults
  const resetSettings = () => {
    setLocalSettings(DEFAULT_SETTINGS);
    localStorage.setItem('therapy-settings', JSON.stringify(DEFAULT_SETTINGS));
  };

  return {
    settings: localSettings,
    updateSettings,
    resetSettings,
  };
}

// Hook for future server-side settings persistence
export function useServerSettings(userId?: number) {
  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings', userId],
    queryFn: async () => {
      if (!userId) return null;
      const response = await fetch(`/api/settings/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch settings');
      return response.json();
    },
    enabled: !!userId,
  });

  const updateSettingsMutation = useMutation({
    mutationFn: async (newSettings: Partial<TherapySettings>) => {
      if (!userId) throw new Error('User ID required');
      const response = await fetch(`/api/settings/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      });
      if (!response.ok) throw new Error('Failed to update settings');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', userId] });
    },
  });

  return {
    settings: settings || DEFAULT_SETTINGS,
    isLoading,
    updateSettings: updateSettingsMutation.mutate,
    isUpdating: updateSettingsMutation.isPending,
  };
}