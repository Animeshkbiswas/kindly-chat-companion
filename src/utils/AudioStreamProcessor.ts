class AudioStreamProcessor {
  private audioContext: AudioContext | null;
  private analyser: AnalyserNode | null;
  private dataArray: Uint8Array | null;
  private source: MediaStreamAudioSourceNode | null;
  private stream: MediaStream | null;
  private isActive: boolean;

  constructor() {
    this.audioContext = null;
    this.analyser = null;
    this.dataArray = null;
    this.source = null;
    this.stream = null;
    this.isActive = false;
  }

  async setupAudioStream(): Promise<boolean> {
    try {
      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

      // Get user media
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      this.source = this.audioContext.createMediaStreamSource(this.stream);
      this.source.connect(this.analyser);
      this.isActive = true;
      this.startVisualization();
      
      return true;
    } catch (error) {
      console.error('Error setting up audio stream:', error);
      return false;
    }
  }

  private startVisualization(): void {
    if (!this.isActive) return;

    const updateVisualization = () => {
      if (!this.isActive || !this.analyser || !this.dataArray) return;

      this.analyser.getByteFrequencyData(this.dataArray);
      const average = this.dataArray.reduce((sum, value) => sum + value, 0) / this.dataArray.length;
      
      // Calculate volume level (0-100)
      const volumeLevel = Math.min(100, (average / 255) * 100);
      
      // Update character animation based on audio levels
      this.updateCharacterResponse(volumeLevel);
      
      if (this.isActive) {
        requestAnimationFrame(updateVisualization);
      }
    };
    updateVisualization();
  }

  private updateCharacterResponse(audioLevel: number): void {
    // Dispatch different events based on audio level intensity
    if (audioLevel > 15) {
      document.dispatchEvent(new CustomEvent('user-speaking', {
        detail: { 
          level: audioLevel,
          intensity: this.getIntensity(audioLevel)
        }
      }));
    } else {
      document.dispatchEvent(new CustomEvent('user-quiet', {
        detail: { level: audioLevel }
      }));
    }
  }

  private getIntensity(audioLevel: number): string {
    if (audioLevel > 60) return 'high';
    if (audioLevel > 30) return 'medium';
    return 'low';
  }

  stop(): void {
    this.isActive = false;
    
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  resume(): void {
    if (this.audioContext && this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }
  }
}

export default AudioStreamProcessor;