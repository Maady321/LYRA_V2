import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sliders, MessageSquare, Compass, Terminal, ShieldAlert, Volume2 } from 'lucide-react';

export default function SettingsDrawer() {
  const { settings, updateSetting, settingsOpen, toggleSettings, isConnected } = useAppStore();

  return (
    <AnimatePresence>
      {settingsOpen && (
        <>
          {/* Backdrop blur overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleSettings}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 cursor-pointer"
          />

          {/* Settings pane */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-[400px] bg-panel-bg border-l border-border-primary/40 shadow-premium z-50 flex flex-col font-sans select-none"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-border-primary/40">
              <div className="flex items-center gap-2.5">
                <Sliders className="w-5 h-5 text-gold-primary animate-pulse" />
                <span className="font-semibold text-lg text-text-primary">Lyra Preferences</span>
              </div>
              <button
                onClick={toggleSettings}
                className="p-1.5 hover:bg-panel-bg/60 rounded-lg text-text-secondary hover:text-text-primary transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable contents */}
            <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
              {/* Status warning if offline */}
              {!isConnected && (
                <div className="flex gap-3 bg-red-950/20 border border-red-900/40 rounded-xl p-3.5 text-xs text-red-400">
                  <ShieldAlert className="w-5 h-5 flex-shrink-0" />
                  <div className="leading-tight space-y-1">
                    <span className="font-bold">Ollama Offline Detected</span>
                    <p className="text-[11px] text-red-500/80 leading-normal">
                      Configuration edits will save locally, but local inference will not generate tokens until Ollama service is running.
                    </p>
                  </div>
                </div>
              )}

              {/* System prompt Customizer */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                  <MessageSquare className="w-3.5 h-3.5 text-gold-primary/80" />
                  <span>System core directive</span>
                </div>
                <textarea
                  value={settings.system_prompt}
                  onChange={(e) => updateSetting('system_prompt', e.target.value)}
                  className="w-full h-32 bg-darkBg border border-border-primary/60 rounded-xl px-3 py-2.5 text-sm text-text-primary placeholder-[#888] focus:outline-none focus:border-gold-primary/50 focus:shadow-glow resize-none font-sans transition-all duration-300"
                  placeholder="Set AI instructions..."
                />
              </div>

              {/* Temperature Slider */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                    <Compass className="w-3.5 h-3.5 text-gold-primary/80" />
                    <span>Inference Temperature</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-gold-primary">{settings.temperature.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.5"
                  step="0.05"
                  value={settings.temperature}
                  onChange={(e) => updateSetting('temperature', parseFloat(e.target.value))}
                  className="w-full accent-gold-primary bg-darkBg h-1 rounded-lg cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-text-secondary font-medium">
                  <span>Deterministic (0.0)</span>
                  <span>Creative (1.5)</span>
                </div>
              </div>

              {/* Max Tokens */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                    <Terminal className="w-3.5 h-3.5 text-gold-primary/80" />
                    <span>Max tokens to predict</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-text-primary">{settings.max_tokens}</span>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {[512, 1024, 2048, 4096].map((tokens) => (
                    <button
                      key={tokens}
                      onClick={() => updateSetting('max_tokens', tokens)}
                      className={`py-1.5 rounded-lg border text-xs font-mono transition-all duration-300 ${
                        settings.max_tokens === tokens
                          ? 'bg-gold-primary/10 border-gold-primary/40 text-gold-primary'
                          : 'bg-darkBg/60 border-border-primary/40 text-text-secondary hover:border-border-hover/60'
                      }`}
                    >
                      {tokens}
                    </button>
                  ))}
                </div>
              </div>

              {/* Context window */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                    <Sliders className="w-3.5 h-3.5 text-gold-primary/80" />
                    <span>Context Window size</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-text-primary">{settings.context_window}</span>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {[2048, 4096, 8192, 16384].map((ctx) => (
                    <button
                      key={ctx}
                      onClick={() => updateSetting('context_window', ctx)}
                      className={`py-1.5 rounded-lg border text-xs font-mono transition-all duration-300 ${
                        settings.context_window === ctx
                          ? 'bg-gold-primary/10 border-gold-primary/40 text-gold-primary'
                          : 'bg-darkBg/60 border-border-primary/40 text-text-secondary hover:border-border-hover/60'
                      }`}
                    >
                      {ctx >= 1024 ? `${ctx / 1024}k` : ctx}
                    </button>
                  ))}
                </div>
              </div>

              {/* Wake System (Voice Wake Word) */}
              <div className="space-y-2.5 pt-2 border-t border-border-primary/40">
                <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                  <Volume2 className="w-3.5 h-3.5 text-gold-primary/80" />
                  <span>Voice Wake Word System</span>
                </div>
                
                <div className="flex items-center justify-between p-3.5 bg-darkBg/60 border border-border-primary/40 rounded-2xl hover:border-border-primary/80 transition-all duration-300">
                  <div className="space-y-0.5 max-w-[240px]">
                    <span className="text-xs font-bold text-text-primary">"Hai Lyra" Voice Wake</span>
                    <p className="text-[10px] text-text-secondary leading-normal">
                      Say "Hai Lyra" to bring the assistant to the front instantly.
                    </p>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => updateSetting('wake_system_enabled', !settings.wake_system_enabled)}
                    className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      settings.wake_system_enabled ? 'bg-gold-primary shadow-glow' : 'bg-panel-bg'
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        settings.wake_system_enabled ? 'translate-x-4' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Response Readout (TTS Voice) */}
              <div className="space-y-2.5 pt-2 border-t border-border-primary/40">
                <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                  <Volume2 className="w-3.5 h-3.5 text-gold-primary/80" />
                  <span>Assistant Voicing System</span>
                </div>
                
                <div className="flex items-center justify-between p-3.5 bg-darkBg/60 border border-border-primary/40 rounded-2xl hover:border-border-primary/80 transition-all duration-300">
                  <div className="space-y-0.5 max-w-[240px]">
                    <span className="text-xs font-bold text-text-primary">Response Readout (TTS)</span>
                    <p className="text-[10px] text-text-secondary leading-normal">
                      Automatically read replies aloud using a warm, natural voice.
                    </p>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => updateSetting('tts_enabled', !settings.tts_enabled)}
                    className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      settings.tts_enabled ? 'bg-gold-primary shadow-glow' : 'bg-panel-bg'
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        settings.tts_enabled ? 'translate-x-4' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Text Chat Toggle */}
              <div className="space-y-2.5 pt-2 border-t border-border-primary/40">
                <div className="flex items-center gap-2 text-xs font-semibold text-text-secondary uppercase tracking-widest">
                  <MessageSquare className="w-3.5 h-3.5 text-gold-primary/80" />
                  <span>Text Chat Interface</span>
                </div>
                
                <div className="flex items-center justify-between p-3.5 bg-darkBg/60 border border-border-primary/40 rounded-2xl hover:border-border-primary/80 transition-all duration-300">
                  <div className="space-y-0.5 max-w-[240px]">
                    <span className="text-xs font-bold text-text-primary">Enable Text Chat</span>
                    <p className="text-[10px] text-text-secondary leading-normal">
                      Toggle the classic text chat. If disabled, Lyra operates in full Voice-First mode.
                    </p>
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => updateSetting('chat_enabled', !settings.chat_enabled)}
                    className={`relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      settings.chat_enabled ? 'bg-gold-primary shadow-glow' : 'bg-panel-bg'
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                        settings.chat_enabled ? 'translate-x-4' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-darkBg/80 border-t border-border-primary/40 text-center">
              <span className="text-[10px] text-text-secondary font-medium">
                Lyra Operating System Platform • V1.0.0
              </span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
