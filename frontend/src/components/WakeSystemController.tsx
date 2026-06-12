import { useEffect, useState, useRef } from 'react';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Sparkles } from 'lucide-react';
import { getFemaleVoice } from '../utils/speech';

export default function WakeSystemController() {
  const { settings } = useAppStore();
  const { wake_system_enabled } = settings;

  // States: 'disabled', 'listening_speech', 'waking'
  const [systemState, setSystemState] = useState<'disabled' | 'listening_speech' | 'waking'>('disabled');
  const systemStateRef = useRef(systemState);
  systemStateRef.current = systemState;
  
  const [speechTranscript, setSpeechTranscript] = useState('');

  const recognitionRef = useRef<any>(null);
  const restartTimerRef = useRef<any>(null);

  // Sound synthesis utility
  const playSynthesizedChime = (type: 'success' | 'chirp') => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      
      const now = ctx.currentTime;
      
      if (type === 'success') {
        // Futuristic rising multi-note cyber chime
        osc.type = 'triangle';
        
        // Note 1
        osc.frequency.setValueAtTime(523.25, now); // C5
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.exponentialRampToValueAtTime(0.12, now + 0.06);
        gain.gain.exponentialRampToValueAtTime(0.02, now + 0.15);
        
        // Note 2
        osc.frequency.setValueAtTime(659.25, now + 0.15); // E5
        gain.gain.exponentialRampToValueAtTime(0.15, now + 0.2);
        gain.gain.exponentialRampToValueAtTime(0.03, now + 0.3);
        
        // Note 3
        osc.frequency.setValueAtTime(783.99, now + 0.3); // G5
        gain.gain.setValueAtTime(0.001, now + 0.3);
        gain.gain.exponentialRampToValueAtTime(0.2, now + 0.35);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
        
        osc.start(now);
        osc.stop(now + 0.7);
      } else if (type === 'chirp') {
        // Subtle soft start chirp
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.05);
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.exponentialRampToValueAtTime(0.04, now + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        
        osc.start(now);
        osc.stop(now + 0.06);
      }
    } catch (e) {
      console.warn("Audio chime synthesis blocked or failed:", e);
    }
  };

  // TTS utility
  const speakVoiceGreeting = async () => {
    try {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // cancel playing items
        const selectedVoice = await getFemaleVoice();
        const utterance = new SpeechSynthesisUtterance("Hello! I am ready. How can I help you?");
        utterance.rate = 1.05;
        utterance.pitch = 1.0;
        utterance.volume = 0.85;
        
        if (selectedVoice) {
          utterance.voice = selectedVoice;
          utterance.lang = selectedVoice.lang; // CRITICAL: match voice locale to prevent Windows male fallback
        }
        
        window.speechSynthesis.speak(utterance);
      }
    } catch (e) {
      console.warn("Voice speech synthesis blocked or failed:", e);
    }
  };

  // Main wake actions
  const triggerSystemWake = () => {
    setSystemState('waking');
    playSynthesizedChime('success');
    
    // Stop recognition to prevent it hearing itself speak
    stopSpeechWakeWordListener();

    // 1. Electron IPC Wake call
    try {
      if ((window as any).wakeElectronApp) {
        console.log("Wake System: Invoking injected wakeElectronApp helper.");
        (window as any).wakeElectronApp();
      } else {
        const electron = (window as any).require ? (window as any).require('electron') : null;
        if (electron) {
          electron.ipcRenderer.send('wake-app');
        } else {
          console.log("Wake System: Electron IPC endpoints not detected in context.");
        }
      }
    } catch (err) {
      console.error("Failed to transmit Electron IPC wake signal:", err);
    }

    // 2. TTS Voice Welcome
    setTimeout(() => {
      speakVoiceGreeting();
    }, 450);

    // 3. UI Actions - Auto-focus textarea in ChatWindow
    setTimeout(() => {
      const textarea = document.querySelector('textarea');
      if (textarea) {
        textarea.focus();
        textarea.classList.add('border-gold-primary');
        setTimeout(() => textarea.classList.remove('border-gold-primary'), 1500);
      }
      
      // Auto-trigger voice button microphone if available
      const voiceBtn = document.querySelector('button[title^="Use Voice Command"]') as HTMLButtonElement;
      if (voiceBtn) {
        voiceBtn.click();
      }

      // Resume continuous listening
      setSystemState('listening_speech');
    }, 1200);
  };

  // Stop recognition and clean up
  const stopSpeechWakeWordListener = () => {
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }
    
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.abort();
      } catch (e) {}
      recognitionRef.current = null;
    }
  };

  // Start direct continuous Speech Recognition
  const startSpeechWakeWordListener = () => {
    stopSpeechWakeWordListener(); // Ensure clean slate
    setSystemState('listening_speech');

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Speech recognition is not supported in this environment.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      console.log("Wake System: Direct Speech Recognition started. Listening for 'Hai Lyra'...");
    };

    recognition.onresult = (event: any) => {
      let phrase = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        phrase += event.results[i][0].transcript;
      }
      
      const cleanPhrase = phrase.toLowerCase().trim();
      setSpeechTranscript(phrase);
      console.log("Wake System interim speech:", cleanPhrase);

      // Robust matches for "Hai Lyra" phonetic variants
      const matchTargets = [
        'hai lyra', 'hi lyra', 'hey lyra', 'hello lyra', 'hey lara', 'hi lara',
        'lyra', 'highly', 'hi leora', 'high lyra', 'hi lira', 'hey lira',
        'hi layer', 'hello lara', 'hi lion', 'hey lion', 'hi client', 'hello lyra'
      ];

      const isMatched = matchTargets.some(target => cleanPhrase.includes(target));
      if (isMatched) {
        recognition.onend = null;
        recognition.abort();
        triggerSystemWake();
      }
    };

    recognition.onerror = (e: any) => {
      if (e.error !== 'no-speech' && e.error !== 'aborted') {
        console.error("Speech recognition error in Wake mode:", e.error);
      }
    };

    recognition.onend = () => {
      // Auto-restart recognition loop continuously in background
      if (wake_system_enabled && systemStateRef.current !== 'waking') {
        restartTimerRef.current = setTimeout(() => {
          try {
            if (wake_system_enabled && systemStateRef.current !== 'waking') {
              recognition.start();
            }
          } catch (err) {
            console.warn("Recognition auto-restart failed:", err);
          }
        }, 150);
      }
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition engine:", err);
    }
  };

  // Main settings toggle trigger
  useEffect(() => {
    if (wake_system_enabled) {
      playSynthesizedChime('chirp');
      startSpeechWakeWordListener();
    } else {
      stopSpeechWakeWordListener();
      setSystemState('disabled');
      setSpeechTranscript('');
    }

    return () => {
      stopSpeechWakeWordListener();
    };
  }, [wake_system_enabled]);

  // Handle active states and restarts
  useEffect(() => {
    if (systemState === 'listening_speech' && wake_system_enabled && !recognitionRef.current) {
      startSpeechWakeWordListener();
    }
  }, [systemState, wake_system_enabled]);

  return (
    <>
      {/* Visual background indicator showing that Lyra is listening for voice */}
      <AnimatePresence>
        {systemState === 'listening_speech' && (
          <motion.div
            initial={{ opacity: 0, y: -40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -40, scale: 0.95 }}
            className="fixed top-20 left-1/2 transform -translate-x-1/2 z-[100] w-full max-w-sm px-4 pointer-events-none select-none font-sans"
          >
            <div className="bg-[#0b0f19]/90 backdrop-blur-md border border-gold-primary/20 rounded-2xl p-4 shadow-[0_0_25px_rgba(255,215,0,0.1)] flex flex-col items-center gap-2">
              <div className="flex items-center gap-3 w-full">
                <div className="p-2 bg-gold-primary/10 border border-gold-primary/20 rounded-xl text-gold-primary animate-pulse flex items-center justify-center">
                  <Mic className="w-4 h-4" />
                </div>
                
                <div className="flex-1 text-left">
                  <span className="text-[11px] font-bold text-text-primary flex items-center gap-1.5 leading-none">
                    <Sparkles className="w-3 h-3 text-gold-primary animate-spin-slow" />
                    Voice Wake Active
                  </span>
                  <p className="text-[9px] text-text-secondary mt-1 leading-tight">
                    Say <b className="text-gold-primary font-semibold">"Hai Lyra"</b> to wake up
                  </p>
                </div>
                
                {/* Visual pulse status */}
                <div className="relative flex h-2 w-2 items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-gold-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-gold-primary"></span>
                </div>
              </div>

              {/* Interim transcription feedback */}
              <div className="w-full bg-[#05070d] border border-border-primary rounded-lg py-1 px-3 min-h-[22px] flex items-center justify-center">
                <span className="text-[9px] font-mono text-text-secondary italic text-center truncate max-w-xs">
                  {speechTranscript ? `"${speechTranscript}"` : "Listening..."}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Futuristic Splash Overlay when waking up */}
      <AnimatePresence>
        {systemState === 'waking' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-[#050811]/95 backdrop-blur-lg flex flex-col items-center justify-center gap-4 select-none pointer-events-none"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: 'spring', damping: 15 }}
              className="p-5 bg-gold-primary/5 border border-gold-primary/20 rounded-full flex items-center justify-center text-gold-primary shadow-[0_0_60px_rgba(255,215,0,0.15)]"
            >
              <Sparkles className="w-12 h-12 animate-spin-slow text-gold-primary" />
            </motion.div>
            
            <motion.h2
              initial={{ y: 15, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="text-lg font-extrabold text-text-primary uppercase tracking-widest text-center"
            >
              Lyra Waking Up
            </motion.h2>
            <p className="text-[10px] text-text-secondary -mt-2">Connecting voice environment...</p>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
