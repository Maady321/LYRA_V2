import { useRef, useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import MessageItem from './MessageItem';
import { Send, Sparkles, ShieldAlert, Cpu, Compass, AppWindow, ArrowDown } from 'lucide-react';
import VoiceCommandButton from './VoiceCommandButton';
import { motion, AnimatePresence } from 'framer-motion';


interface ChatWindowProps {
  sendPrompt: (content: string) => void;
}

export default function ChatWindow({ sendPrompt }: ChatWindowProps) {
  const {
    messages,
    isStreaming,
    currentConversationId,
    error,
    setError,
    activeModel,
    createConversation,
    selectConversation
  } = useAppStore();

  const [input, setInput] = useState('');
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);



  // Auto-scroll to bottom of conversation
  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior,
      });
    }
  };

  useEffect(() => {
    scrollToBottom('smooth');
  }, [messages.length]);

  // Handle minor streaming updates to scroll
  useEffect(() => {
    if (isStreaming) {
      scrollToBottom('auto');
    }
  }, [messages, isStreaming]);

  // Monitor scrolling to show "Jump to Bottom" button
  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;
      setShowScrollBottom(!isNearBottom && scrollHeight > clientHeight);
    }
  };

  // Adjust textarea heights based on input length
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    sendPrompt(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleQuickSession = async () => {
    try {
      const id = await createConversation('New Conversation');
      await selectConversation(id);
      setTimeout(() => textareaRef.current?.focus(), 100);
    } catch (e) {
      console.error(e);
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    setInput((prev) => {
      const trimmed = prev.trim();
      return trimmed ? `${trimmed} ${transcript.trim()}` : transcript.trim();
    });
    setTimeout(() => textareaRef.current?.focus(), 50);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-darkBg relative font-sans">
      
      {/* Messages list pane */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-6 py-6 space-y-6 scroll-smooth select-text"
      >
        {messages.length === 0 ? (
          /* Empty dashboard intro page */
          <div className="max-w-3xl mx-auto h-full flex flex-col justify-center py-10 select-none">
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center space-y-3 mb-10"
            >
              <div className="inline-flex p-3 bg-brandBlue/5 border border-brandBlue/15 rounded-2xl pulsing-glow mb-2">
                <Sparkles className="w-8 h-8 text-brandBlue animate-pulse" />
              </div>
              <h1 className="text-3xl font-extrabold text-slate-100 tracking-wider">
                Lyra V1 AI Core
              </h1>
              <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
                Your modular, offline-first local AI operating environment. Secure, fast, and extensible.
              </p>
            </motion.div>

            {/* Extensible modules teaser panels */}
            <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
              <div className="p-4 bg-darkSurface/30 border border-slate-800/40 rounded-2xl glass-panel-light flex items-start gap-3">
                <div className="p-2 bg-brandBlue/10 rounded-xl text-brandBlue">
                  <Cpu className="w-4.5 h-4.5" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-300">Local Inference Engine</span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-normal">
                    Powered by Ollama APIs. Runs Llama3, Mistral, and DeepSeek model files privately.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-darkSurface/30 border border-slate-800/40 rounded-2xl glass-panel-light flex items-start gap-3 opacity-60">
                <div className="p-2 bg-brandBlue/10 rounded-xl text-brandBlue">
                  <Compass className="w-4.5 h-4.5" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-300">Autonomous Agents (Planned)</span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-normal">
                    Tool execution pipelines for local bash tools, file managers, and task compilers.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-darkSurface/30 border border-slate-800/40 rounded-2xl glass-panel-light flex items-start gap-3 opacity-60">
                <div className="p-2 bg-brandPurple/10 rounded-xl text-brandPurple">
                  <AppWindow className="w-4.5 h-4.5" />
                </div>
                <div>
                  <span className="text-xs font-bold text-slate-300">Browser Automation (Planned)</span>
                  <p className="text-[10px] text-slate-500 mt-1 leading-normal">
                    Agentic browser controls to surf the web, scrape information, and submit forms automatically.
                  </p>
                </div>
              </div>
            </div>

            {!currentConversationId && (
              <div className="mt-8 text-center animate-bounce">
                <button
                  onClick={handleQuickSession}
                  className="px-5 py-2 rounded-xl bg-slate-800/40 border border-slate-700/30 text-xs font-semibold text-brandBlue hover:border-brandBlue/30 hover:bg-brandBlue/5 transition-all"
                >
                  Spawn Quick Session thread
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Render messages mapping */
          <div className="max-w-3xl mx-auto space-y-5">
            {messages.map((message) => (
              <MessageItem key={message.id} message={message} />
            ))}
          </div>
        )}
      </div>

      {/* Floating Jump to bottom button */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom('smooth')}
          className="absolute bottom-28 right-8 p-2 rounded-full bg-slate-800/70 border border-slate-700/50 text-brandBlue hover:text-cyan-400 hover:scale-105 shadow-glow transition-all duration-300 z-10"
        >
          <ArrowDown className="w-4 h-4" />
        </button>
      )}

      {/* Primary user input drawer */}
      <div className="w-full bg-darkBg border-t border-slate-850/40 px-6 py-5 select-none">
        <div className="max-w-3xl mx-auto space-y-4">
          
          {/* Error notifications with retry */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="flex items-center justify-between p-3.5 bg-red-950/20 border border-red-900/40 rounded-xl text-xs text-red-400 gap-3"
              >
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4.5 h-4.5 flex-shrink-0" />
                  <span className="leading-tight">{error}</span>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="text-[10px] font-bold text-slate-500 hover:text-slate-300 uppercase tracking-widest"
                >
                  Dismiss
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isStreaming && messages[messages.length - 1]?.role === 'user' && (
            <div className="flex items-center gap-2 px-1 text-[11px] text-slate-500 select-none">
              <Cpu className="w-3.5 h-3.5 text-brandBlue animate-spin" />
              <span>Lyra is compiling output...</span>
            </div>
          )}

          {/* Input text form */}
          <form onSubmit={handleSubmit} className="relative flex items-end gap-2.5">
            <div className="flex-1 bg-darkSurface border border-slate-800/50 rounded-2xl px-4 py-3 focus-within:border-brandBlue/40 focus-within:shadow-glow transition-all duration-300 flex items-end">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder={
                  !currentConversationId
                    ? "Select or spawn a session above to begin..."
                    : isStreaming
                    ? "Streaming reply..."
                    : `Command Lyra (${activeModel})...`
                }
                disabled={!currentConversationId || isStreaming}
                className="w-full bg-transparent border-0 outline-none text-slate-200 text-sm placeholder-slate-600 resize-none font-sans focus:ring-0 p-0 leading-normal max-h-40 min-h-[20px]"
              />
            </div>

            <div className="flex items-center gap-2">
              <VoiceCommandButton
                onTranscript={handleVoiceTranscript}
                disabled={!currentConversationId || isStreaming}
              />

              <button
                type="submit"
                disabled={!currentConversationId || isStreaming || !input.trim()}
                className={`p-3.5 rounded-2xl transition-all duration-300 shadow-md ${
                  !input.trim() || isStreaming || !currentConversationId
                    ? 'bg-slate-900/60 text-slate-700 cursor-not-allowed border border-transparent'
                    : 'bg-gradient-to-tr from-brandBlue to-brandPurple text-white hover:shadow-glow hover:scale-105'
                }`}
              >
                <Send className="w-4.5 h-4.5" />
              </button>
            </div>
          </form>

          <div className="flex items-center justify-between text-[10px] text-slate-600 font-medium px-1.5 select-none">
            <span>Lyra processes prompts 100% locally on your computer.</span>
            <span>Enter sends • Shift+Enter new line</span>
          </div>
        </div>
      </div>
    </div>
  );
}
