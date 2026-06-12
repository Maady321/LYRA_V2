import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { ChevronDown, Cpu, RefreshCw, AlertCircle } from 'lucide-react';

export default function ModelSelector() {
  const { models, activeModel, setActiveModel, fetchModels, isConnected } = useAppStore();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <div
        onClick={() => isConnected && setIsOpen(!isOpen)}
        className={`flex items-center gap-2.5 px-3 py-1.5 rounded-lg border text-sm font-medium cursor-pointer transition-all duration-300 ${
          isConnected
            ? 'bg-panel-bg/90 border-gold-primary/20 text-text-primary hover:border-gold-primary/40 hover:shadow-glow'
            : 'bg-red-950/20 border-red-800/30 text-red-400 cursor-not-allowed'
        }`}
      >
        <Cpu className={`w-4 h-4 ${isConnected ? 'text-gold-primary animate-pulse' : 'text-red-500'}`} />
        
        <div className="flex flex-col items-start leading-tight">
          <span className="text-xs text-text-secondary font-semibold uppercase tracking-wider">Active Core</span>
          <span className="font-medium max-w-[140px] truncate">
            {isConnected ? activeModel : 'Ollama Offline'}
          </span>
        </div>

        <ChevronDown className="w-4 h-4 text-text-secondary ml-1.5" />
      </div>

      {isOpen && isConnected && (
        <>
          {/* Backdrop click interceptor */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          
          <div className="absolute right-0 mt-2 w-72 rounded-xl glass-panel shadow-premium z-50 py-1.5 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border-primary/40 mb-1">
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Available Engines</span>
              <button
                onClick={() => {
                  fetchModels();
                  setIsOpen(false);
                }}
                className="p-1 hover:bg-panel-bg/50 rounded text-text-secondary hover:text-gold-primary transition-all"
                title="Refresh list"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="max-h-60 overflow-y-auto">
              {models.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-5 text-center gap-2">
                  <AlertCircle className="w-8 h-8 text-socWarning/80" />
                  <span className="text-xs text-text-secondary">No active models detected.</span>
                  <span className="text-[10px] text-text-secondary">Run <code className="text-text-primary">ollama run llama3</code> in your terminal</span>
                </div>
              ) : (
                models.map((model) => (
                  <div
                    key={model.name}
                    onClick={() => {
                      setActiveModel(model.name);
                      setIsOpen(false);
                    }}
                    className={`flex flex-col px-4 py-2 hover:bg-panel-bg/30 cursor-pointer border-l-2 transition-all ${
                      activeModel === model.name
                        ? 'border-gold-primary bg-gold-primary/5 text-text-primary'
                        : 'border-transparent text-text-secondary hover:text-text-primary'
                    }`}
                  >
                    <span className="text-sm font-semibold truncate">{model.name}</span>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] text-text-secondary">
                      {model.parameter_size && (
                        <span className="bg-panel-bg/50 px-1.5 py-0.5 rounded border border-border-hover/20">
                          {model.parameter_size} parameters
                        </span>
                      )}
                      {model.context_size && (
                        <span>Ctx: {model.context_size}</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
