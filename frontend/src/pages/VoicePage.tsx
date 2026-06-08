import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, UserCircle } from 'lucide-react';
import { getFemaleVoice, getVoiceForAgent } from '../utils/speech';

interface BriefingItem {
  agent: string;
  color: string;
  text: string;
}

export default function VoicePage() {
  const { messages } = useAppStore();
  const { sendPrompt } = useWebSocket();
  const [isListening, setIsListening] = useState(false);
  const [interimText, setInterimText] = useState('');
  const recognitionRef = useRef<any>(null);

  // Briefing States
  const [isBriefing, setIsBriefing] = useState(true);
  const [briefingScript, setBriefingScript] = useState<BriefingItem[]>([]);
  const [briefingIndex, setBriefingIndex] = useState(-1);
  const [activeOrbColor, setActiveOrbColor] = useState('brandBlue');

  const lastAssistantMessage = messages
    .filter(m => m.role === 'assistant')
    .slice(-1)[0]?.content || "I am ready for your command.";

  // Fetch Briefing Script on Mount
  useEffect(() => {
    fetch('http://127.0.0.1:8001/api/briefing')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setBriefingScript(data);
          setBriefingIndex(0); // start briefing
        } else {
          setIsBriefing(false);
        }
      })
      .catch(err => {
        console.error("Failed to load briefing:", err);
        setIsBriefing(false); // Skip if failed
      });
  }, []);

  // Play Briefing Sequence
  useEffect(() => {
    if (!isBriefing || briefingIndex < 0 || briefingIndex >= briefingScript.length) {
      if (isBriefing && briefingIndex >= briefingScript.length) {
        setIsBriefing(false);
      }
      return;
    }

    const playNext = async () => {
      const item = briefingScript[briefingIndex];
      if (!item) return; // Prevent undefined errors
      setActiveOrbColor(item.color);

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const voice = await getVoiceForAgent(item.agent);
        const utterance = new SpeechSynthesisUtterance(item.text);
        if (voice) utterance.voice = voice;
        utterance.rate = 1.05;

        utterance.onend = () => {
          setTimeout(() => {
            setBriefingIndex(prev => prev + 1);
          }, 400); // short pause between agents
        };

        window.speechSynthesis.speak(utterance);
      } else {
        // Fallback if no TTS
        setTimeout(() => setBriefingIndex(prev => prev + 1), 3000);
      }
    };

    playNext();

    return () => {
      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    }
  }, [briefingIndex, isBriefing, briefingScript]);

  // Setup Speech Recognition
  useEffect(() => {
    // Don't setup mic while briefing
    if (isBriefing) return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error("Speech Recognition not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      setInterimText(interimTranscript);

      if (finalTranscript.trim()) {
        sendPrompt(finalTranscript.trim());
        setInterimText(''); 
      }
    };

    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch(e) {}
      }
    };
  }, [sendPrompt, isBriefing]);

  const toggleListen = () => {
    if (isBriefing) return;
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
    }
  };

  // Speak when lastAssistantMessage changes (Standard Mode)
  useEffect(() => {
    if (isBriefing || !lastAssistantMessage || lastAssistantMessage === "I am ready for your command.") return;
    
    const speak = async () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        // Since standard mode goes to Lyra, we use getVoiceForAgent("Lyra")
        const voice = await getVoiceForAgent("Lyra");
        const utterance = new SpeechSynthesisUtterance(lastAssistantMessage);
        if (voice) utterance.voice = voice;
        utterance.rate = 1.05;
        window.speechSynthesis.speak(utterance);
      }
    };
    speak();
  }, [lastAssistantMessage, isBriefing]);

  // Color mapping logic
  const getOrbGlow = () => {
    if (!isBriefing) return isListening ? "rgba(6,182,212,0.6)" : "rgba(6,182,212,0.2)";
    
    const c = activeOrbColor;
    if (c === "cyan" || c === "brandBlue") return "rgba(6,182,212,0.6)";
    if (c === "emerald") return "rgba(16,185,129,0.6)";
    if (c === "orange") return "rgba(249,115,22,0.6)";
    if (c === "purple") return "rgba(168,85,247,0.6)";
    return "rgba(6,182,212,0.6)";
  };

  const currentText = isBriefing && briefingScript[briefingIndex] 
    ? briefingScript[briefingIndex].text 
    : lastAssistantMessage;

  const currentAgent = isBriefing && briefingScript[briefingIndex]
    ? briefingScript[briefingIndex].agent
    : "Lyra";

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-darkBg text-slate-100 relative overflow-hidden">
      
      {/* Background ambient glow */}
      <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
        <motion.div
          animate={{
            scale: (isListening || isBriefing) ? [1, 1.2, 1] : 1,
            opacity: (isListening || isBriefing) ? [0.3, 0.6, 0.3] : 0.2,
            backgroundColor: getOrbGlow().replace("0.6)", "1)").replace("0.2)", "1)")
          }}
          transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          className="w-[400px] h-[400px] rounded-full blur-[140px]"
        />
      </div>

      <div className="z-10 flex flex-col items-center justify-center gap-10 max-w-2xl w-full px-6">
        
        {/* Main Voice Orb */}
        <motion.button
          onClick={toggleListen}
          animate={{
            scale: (isListening || isBriefing) ? 1.05 : 1,
            boxShadow: `0 0 80px ${getOrbGlow()}, inset 0 0 30px ${getOrbGlow().replace("0.6", "0.8")}`,
            borderColor: getOrbGlow().replace("0.6", "1").replace("0.2", "0.5")
          }}
          transition={{ duration: 0.3 }}
          className="relative w-48 h-48 rounded-full bg-gradient-to-tr from-[#050B14] to-[#0A192F] border-2 flex items-center justify-center group overflow-hidden"
        >
          {isBriefing ? (
            <UserCircle className="w-16 h-16 opacity-80" style={{ color: getOrbGlow().replace("0.6", "1") }} />
          ) : isListening ? (
            <Mic className="w-16 h-16 text-brandBlue animate-pulse" />
          ) : (
            <MicOff className="w-16 h-16 text-slate-500 group-hover:text-slate-300 transition-colors" />
          )}

          {/* Internal ripple ring */}
          {(isListening || isBriefing) && (
            <motion.div
              initial={{ scale: 0.8, opacity: 0.5 }}
              animate={{ scale: 1.5, opacity: 0 }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut" }}
              className="absolute inset-0 border-2 rounded-full"
              style={{ borderColor: getOrbGlow().replace("0.6", "1") }}
            />
          )}
        </motion.button>

        {/* Status Text */}
        <div className="text-center space-y-4 w-full h-24">
          <AnimatePresence mode="wait">
            <motion.div
              key={isBriefing ? "brief" : "listen"}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {isBriefing ? (
                <div className="space-y-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-500">Morning Briefing</span>
                  <h2 className="text-2xl font-bold tracking-widest uppercase" style={{ color: getOrbGlow().replace("0.6", "1") }}>
                    {currentAgent}
                  </h2>
                </div>
              ) : (
                <div className="space-y-1">
                  <h2 className="text-2xl font-bold tracking-widest uppercase bg-clip-text text-transparent bg-gradient-to-r from-brandBlue to-cyan-200">
                    {isListening ? "Listening..." : "Tap to Speak"}
                  </h2>
                  <div className="h-6">
                    {interimText ? (
                      <p className="text-base text-slate-400 italic">"{interimText}"</p>
                    ) : (
                      <p className="text-sm text-slate-600">Give Lyra a command using your voice</p>
                    )}
                  </div>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* AI Response Subtitle Area */}
        <div className="w-full bg-darkSurface/60 backdrop-blur-md border border-slate-800/60 rounded-2xl p-6 min-h-[120px] flex items-center justify-center shadow-premium relative overflow-hidden">
           
           {/* Subtle glow border indicating who is speaking */}
           {isBriefing && (
             <div className="absolute left-0 top-0 bottom-0 w-1" style={{ backgroundColor: getOrbGlow().replace("0.6", "1") }} />
           )}
           
           <AnimatePresence mode="wait">
             <motion.p 
               key={currentText}
               initial={{ opacity: 0, y: 5 }}
               animate={{ opacity: 1, y: 0 }}
               exit={{ opacity: 0, y: -5 }}
               className="text-center text-slate-200 font-medium leading-relaxed text-lg"
             >
               {currentText}
             </motion.p>
           </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
