import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, VolumeX, Shield, Radio, Activity, Lock, Hexagon } from 'lucide-react';
import { getVoiceForAgent } from '../utils/speech';

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
  const [activeOrbColor, setActiveOrbColor] = useState('gold-primary');

  const lastAssistantMessage = messages
    .filter(m => m.role === 'assistant')
    .slice(-1)[0]?.content || "Tactical AI Core initialized. Awaiting voice command.";

  // Mock Briefing Script
  useEffect(() => {
    const mockData = [
      { agent: "FURY", color: "gold-primary", text: "Coordinator FURY online. System integrity verified." },
      { agent: "VISION", color: "gold-bright", text: "Memory nodes synchronized. Vector database is stable." },
      { agent: "STARK", color: "gold-elite", text: "Execution environment primed. Waiting for payloads." }
    ];
    setBriefingScript(mockData);
    setBriefingIndex(0);
  }, []);

  // Play Briefing Sequence
  useEffect(() => {
    if (!isBriefing || briefingIndex < 0 || briefingIndex >= briefingScript.length) {
      if (isBriefing && briefingIndex >= briefingScript.length) setIsBriefing(false);
      return;
    }

    const playNext = async () => {
      const item = briefingScript[briefingIndex];
      if (!item) return;
      setActiveOrbColor(item.color);

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const voice = await getVoiceForAgent(item.agent);
        const utterance = new SpeechSynthesisUtterance(item.text);
        if (voice) utterance.voice = voice;
        utterance.rate = 1.05;

        utterance.onend = () => setTimeout(() => setBriefingIndex(prev => prev + 1), 400);
        window.speechSynthesis.speak(utterance);
      } else {
        setTimeout(() => setBriefingIndex(prev => prev + 1), 3000);
      }
    };
    playNext();
    return () => { if ('speechSynthesis' in window) window.speechSynthesis.cancel(); }
  }, [briefingIndex, isBriefing, briefingScript]);

  // Setup Speech Recognition
  useEffect(() => {
    if (isBriefing) return;
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
        else interimTranscript += event.results[i][0].transcript;
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

    return () => { if (recognitionRef.current) try { recognitionRef.current.abort(); } catch(e) {} };
  }, [sendPrompt, isBriefing]);

  const toggleListen = () => {
    if (isBriefing) return;
    if (isListening) recognitionRef.current?.stop();
    else recognitionRef.current?.start();
  };

  useEffect(() => {
    if (isBriefing || !lastAssistantMessage || lastAssistantMessage.includes("initialized")) return;
    const speak = async () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const voice = await getVoiceForAgent("Lyra");
        const utterance = new SpeechSynthesisUtterance(lastAssistantMessage);
        if (voice) utterance.voice = voice;
        utterance.rate = 1.05;
        window.speechSynthesis.speak(utterance);
      }
    };
    speak();
  }, [lastAssistantMessage, isBriefing]);

  const getOrbGlow = () => {
    if (!isBriefing) return isListening ? "#FFD700" : "#171717";
    const c = activeOrbColor;
    if (c === "gold-bright") return "#FFE082";
    if (c === "gold-elite") return "#FFB300";
    return "#FFD700";
  };

  const currentText = isBriefing && briefingScript[briefingIndex] ? briefingScript[briefingIndex].text : lastAssistantMessage;
  const currentAgent = isBriefing && briefingScript[briefingIndex] ? briefingScript[briefingIndex].agent : "Tactical Core";

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-darkBg text-text-primary relative overflow-hidden h-full p-6">
      
      {/* Background ambient grid */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,215,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,215,0,0.03)_1px,transparent_1px)] bg-[size:60px_60px] opacity-30 pointer-events-none" />

      {/* Security Level Ring background */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-5">
         <div className="w-[800px] h-[800px] rounded-full border-[20px] border-solid border-gold-primary" />
      </div>

      {/* Top Telemetry Bar */}
      <div className="absolute top-6 left-6 right-6 flex justify-between items-start pointer-events-none z-20">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2 bg-panel-bg border border-border-primary px-3 py-1.5 text-xs font-mono text-gold-primary shadow-gold">
            <Radio className="w-3 h-3 animate-pulse" /> COMMS: ENCRYPTED SECURE
          </div>
          <div className="flex items-center gap-2 bg-panel-bg border border-border-primary px-3 py-1.5 text-xs font-mono text-socSuccess shadow-gold">
            <Lock className="w-3 h-3 text-[#00E676]" /> <span className="text-[#00E676]">VOICE BIOMETRICS: MATCHED</span>
          </div>
        </div>
        <div className="flex flex-col gap-2 text-right">
          <div className="flex items-center gap-2 justify-end bg-panel-bg border border-border-primary px-3 py-1.5 text-xs font-mono text-gold-primary shadow-gold">
            SIGNAL STRENGTH: 98.4% <Activity className="w-3 h-3" />
          </div>
        </div>
      </div>

      <div className="z-10 flex flex-col items-center justify-center gap-16 max-w-3xl w-full mt-10">
        
        {/* Holographic Waveform Core */}
        <motion.button
          onClick={toggleListen}
          animate={{ scale: (isListening || isBriefing) ? 1.05 : 1 }}
          className="relative w-72 h-72 flex items-center justify-center group outline-none"
        >
          {/* Energy Pulse Background */}
          {(isListening || isBriefing) && (
             <motion.div
               animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
               transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
               className="absolute inset-0 rounded-full bg-gold-primary/20 blur-xl"
             />
          )}

          {/* Rotating Gold Rings */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 20, ease: "linear" }}
            className="absolute inset-0 border border-dashed rounded-full opacity-40"
            style={{ borderColor: getOrbGlow(), borderWidth: '2px' }}
          />
          <motion.div
            animate={{ rotate: -360, scale: isListening ? [1, 1.05, 1] : 1 }}
            transition={{ repeat: Infinity, duration: isListening ? 1.5 : 15, ease: "linear" }}
            className="absolute inset-6 border-2 border-solid rounded-full opacity-60"
            style={{ borderColor: getOrbGlow() }}
          />
          <motion.div
            animate={{ rotate: 180 }}
            transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
            className="absolute inset-10 border border-dotted rounded-full opacity-30"
            style={{ borderColor: getOrbGlow(), borderWidth: '4px' }}
          />
          
          <div className="w-40 h-40 rounded-full bg-panel-bg flex items-center justify-center border-2 border-gold-primary/50 z-10 shadow-[0_0_50px_rgba(255,215,0,0.2)]" style={{ boxShadow: `0 0 50px ${getOrbGlow()}50` }}>
            {isListening ? (
              <div className="flex gap-2 items-center justify-center h-16 w-16">
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{ height: ['20%', '100%', '20%'] }}
                    transition={{ repeat: Infinity, duration: 0.6, delay: i * 0.1, ease: 'easeInOut' }}
                    className="w-1.5 rounded-full"
                    style={{ backgroundColor: getOrbGlow() }}
                  />
                ))}
              </div>
            ) : isBriefing ? (
              <Hexagon className="w-16 h-16 opacity-90" style={{ color: getOrbGlow() }} />
            ) : (
              <MicOff className="w-16 h-16 text-text-secondary group-hover:text-gold-primary transition-colors" />
            )}
          </div>
        </motion.button>

        {/* Audio Stop */}
        <button
          onClick={() => { if ('speechSynthesis' in window) window.speechSynthesis.cancel(); }}
          className="flex items-center gap-2 px-5 py-2 glass-panel hover:bg-[#FF5252]/10 text-[#FF5252] border border-[#FF5252]/30 transition-all font-mono text-xs tracking-widest z-20 shadow-threat"
        >
          <VolumeX className="w-3.5 h-3.5" /> OVERRIDE AUDIO
        </button>

        {/* Tactical Subtitle Panel */}
        <div className="w-full flex flex-col gap-2 relative z-20">
          {/* Agent speaker indicator */}
          <div className="flex items-center gap-3 px-2">
             <div className="w-2 h-2 rounded-full shadow-glow" style={{ backgroundColor: getOrbGlow() }} />
             <span className="text-[10px] font-mono tracking-widest uppercase text-text-secondary">SPEAKER IDENT:</span>
             <span className="text-xs font-mono tracking-widest uppercase font-black" style={{ color: getOrbGlow() }}>{currentAgent}</span>
          </div>
          
          <div className="w-full glass-panel p-6 min-h-[140px] flex items-center justify-center relative border-l-4 shadow-premium" style={{ borderLeftColor: getOrbGlow() }}>
             <AnimatePresence mode="wait">
               {interimText && !isBriefing ? (
                 <motion.p key="interim" className="text-center text-text-secondary font-mono italic text-sm w-full">
                   "{interimText}"
                 </motion.p>
               ) : (
                 <motion.p 
                   key={currentText}
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0, y: -10 }}
                   className="text-center text-text-primary font-sans leading-relaxed text-xl w-full font-medium"
                 >
                   {currentText}
                 </motion.p>
               )}
             </AnimatePresence>
          </div>
        </div>

      </div>
    </div>
  );
}
