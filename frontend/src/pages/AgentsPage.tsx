import { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { apiService } from '../services/api';
import { 
  Users, Activity, RefreshCw, Cpu, Database, HardDrive, 
  Terminal, ShieldAlert, CheckCircle, Zap, Send, ArrowLeft, Shield, Code, Network
} from 'lucide-react';

interface LocalAgent {
  name: string;
  role: string;
  desc: string;
  model: string;
  permissions: string[];
  trustLevel: string;
  avatar: string;
}

const ALL_10_AGENTS: LocalAgent[] = [
  { name: "FURY", role: "Coordinator Agent", desc: "Main decision maker, parses queries and synthesizes reports", model: "llama3", permissions: ["FILE", "NETWORK"], trustLevel: "SYSTEM", avatar: "💀" },
  { name: "VISION", role: "Memory Agent", desc: "Handles SQLite dialogue persistence and semantic vector stores", model: "nomic-embed", permissions: ["FILE"], trustLevel: "HIGH", avatar: "👁️" },
  { name: "CAPTAIN", role: "Planning Agent", desc: "Decomposes complex goals into actionable roadmaps", model: "llama3", permissions: ["READ_ONLY"], trustLevel: "HIGH", avatar: "🛡️" },
  { name: "BANNER", role: "Research Agent", desc: "Conducts local RAG scans and summarized research checks", model: "mistral", permissions: ["READ_ONLY"], trustLevel: "MEDIUM", avatar: "🧪" },
  { name: "STARK", role: "Execution Agent", desc: "Compiles and executes sandboxed Python automation tasks", model: "qwen2.5", permissions: ["FILE", "EXEC"], trustLevel: "SYSTEM", avatar: "🦾" },
  { name: "JARVIS", role: "System Monitor Agent", desc: "Monitors machine CPU, RAM, Disk, and Ollama status", model: "llama3", permissions: ["READ_ONLY"], trustLevel: "MEDIUM", avatar: "🤖" },
  { name: "SPIDEY", role: "Notification Agent", desc: "Schedules non-blocking async timers and alerts", model: "llama3", permissions: ["READ_ONLY"], trustLevel: "LOW", avatar: "🕸️" },
  { name: "GHOST", role: "Computer Control Agent", desc: "Executes audited shell tasks and file system commands", model: "llama3", permissions: ["FILE", "EXEC"], trustLevel: "SYSTEM", avatar: "👻" },
  { name: "EAGLE", role: "Vision/OCR Agent", desc: "Interfaces local LLaVA/OCR models to translate images", model: "llava", permissions: ["READ_ONLY"], trustLevel: "MEDIUM", avatar: "🦅" },
  { name: "NAVIGATOR", role: "Browser Scraper Agent", desc: "Sandbox Playwright browser crawler and web querying", model: "qwen2.5", permissions: ["NETWORK", "FILE"], trustLevel: "HIGH", avatar: "🧭" }
];

  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<LocalAgent | null>(null);
  const agentsLoading = false;

  // Mock telemetry data for the UI
  const agentsTelemetry = { cpu: 42.5, ram: 68.2, disk: 34.1, agents: [] };
  const agentsLogs = [
    { timestamp: new Date().toISOString(), agent_name: 'FURY', action_taken: 'Analyzed user intent successfully.', status: 'SUCCESS' },
    { timestamp: new Date(Date.now() - 5000).toISOString(), agent_name: 'VISION', action_taken: 'Stored vector embeddings in DB.', status: 'SUCCESS' },
    { timestamp: new Date(Date.now() - 15000).toISOString(), agent_name: 'STARK', action_taken: 'Execution payload rejected due to sandbox limits.', status: 'FAILED' }
  ];
  
  const [commandText, setCommandText] = useState('');
  const [executingCommand, setExecutingCommand] = useState(false);
  const [commandResult, setCommandResult] = useState<string | null>(null);
  const [commandError, setCommandError] = useState<string | null>(null);

  useEffect(() => {
    // Polling removed to fix CORS spam since backend endpoints are not ready yet
  }, [autoRefresh]);

  const handleExecuteCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !commandText.trim()) return;
    setExecutingCommand(true);
    setCommandResult(null);
    setCommandError(null);
    try {
      const response = await apiService.executeAgentCommand(selectedAgent.name, commandText.trim());
      if (response.status === 'success') setCommandResult(response.result);
      else setCommandError(response.result || "Execution completed with warnings.");
    } catch (err: any) {
      setCommandError(err.response?.data?.detail || err.message || "Failed to execute command.");
    } finally {
      setExecutingCommand(false);
    }
  };

  const renderMeter = (val: number, colorClass: string) => (
    <div className="w-full space-y-1.5 text-left">
      <div className="flex justify-between text-[10px] font-mono text-text-secondary">
        <span>USAGE LOAD</span>
        <span className="font-bold text-text-primary">{val.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 w-full bg-darkBg rounded-full overflow-hidden border border-border-primary">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${val}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${colorClass}`}
        />
      </div>
    </div>
  );

  const getAgentStatus = (name: string) => {
    const dbAgent = agentsTelemetry?.agents?.find(a => a.name === name);
    return dbAgent ? dbAgent.status : "ONLINE";
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-text-primary">
      
      {/* Header Panel */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between p-6 border-b border-border-primary bg-panel-bg/50"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gold-primary/10 text-gold-primary rounded-xl border border-gold-primary/30 shadow-glow">
            <Network className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
              Autonomous Agent Operations
              <span className="text-xs px-3 py-1 rounded-full border font-bold tracking-widest text-gold-primary bg-gold-primary/10 border-gold-primary/30 uppercase">
                NODE TOPOLOGY ACTIVE
              </span>
            </h1>
            <p className="text-text-secondary text-sm mt-1 font-mono">Consensus Engine & Multi-Agent Swarm Control</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg border text-xs font-mono font-bold tracking-wider transition-all duration-300 ${
              autoRefresh 
                ? 'bg-socSuccess/10 border-socSuccess/30 text-socSuccess' 
                : 'bg-darkBg border-border-primary text-text-secondary'
            }`}
          >
            {autoRefresh ? "LIVE SYNC ON" : "LIVE SYNC OFF"}
          </button>
          <button
            disabled={agentsLoading}
            className="p-2 glass-panel-light text-text-secondary hover:text-gold-primary transition-all"
          >
            <RefreshCw className={`w-5 h-5 ${agentsLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Hardware Telemetry Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'CPU Inference Load', value: agentsTelemetry?.cpu || 0, icon: Cpu, color: 'bg-socWarning shadow-glow' },
            { label: 'Agent Memory Space', value: agentsTelemetry?.ram || 0, icon: Database, color: 'bg-gold-primary shadow-glow' },
            { label: 'Vector Storage I/O', value: agentsTelemetry?.disk || 0, icon: HardDrive, color: 'bg-socSuccess shadow-glow' },
          ].map((metric, idx) => (
            <motion.div 
              key={idx}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-panel p-5 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <metric.icon className="w-4 h-4 text-text-secondary" />
                  <span className="text-text-primary text-xs font-bold uppercase tracking-wider">{metric.label}</span>
                </div>
              </div>
              {renderMeter(metric.value, metric.color)}
            </motion.div>
          ))}
        </div>

        {/* 10 Agent Cards & Console */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
          
          <div className="xl:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {ALL_10_AGENTS.map((agent, i) => {
              const status = getAgentStatus(agent.name);
              const isSelected = selectedAgent?.name === agent.name;
              
              return (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * i }}
                  key={agent.name}
                  onClick={() => { setSelectedAgent(agent); setCommandText(''); setCommandResult(null); setCommandError(null); }}
                  className={`glass-panel p-4 cursor-pointer transition-all duration-300 flex flex-col justify-between h-36 ${
                    isSelected ? 'border-gold-primary/60 shadow-glow bg-panel-bg' : 'hover:border-gold-bright/40 hover:bg-panel-bg/70'
                  }`}
                >
                  <div className="flex items-start justify-between w-full relative overflow-hidden">
                    {/* Animated Gold Sweep Border Effect for active/hover states */}
                    <motion.div 
                      className="absolute inset-0 border-b-2 border-gold-primary opacity-0 group-hover:opacity-100"
                      initial={{ x: '-100%' }}
                      animate={{ x: '100%' }}
                      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                    />
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-darkBg border border-border-primary rounded-lg flex items-center justify-center font-bold text-lg">
                        {agent.avatar}
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-text-primary">{agent.name}</h3>
                        <span className="text-[9px] font-mono text-gold-bright uppercase tracking-widest">{agent.role}</span>
                      </div>
                    </div>
                    <div>
                      {status === 'ONLINE' ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-black tracking-wider bg-socSuccess/10 border border-socSuccess/30 text-socSuccess">
                          <CheckCircle className="w-3 h-3" /> ONLINE
                        </span>
                      ) : status === 'BUSY' ? (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-black tracking-wider bg-socWarning/10 border border-socWarning/30 text-socWarning animate-pulse">
                          <Zap className="w-3 h-3" /> BUSY
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[9px] font-black tracking-wider bg-socCritical/10 border border-socCritical/30 text-socCritical">
                          <ShieldAlert className="w-3 h-3" /> OFFLINE
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 mt-4">
                    {agent.permissions.map(p => (
                      <span key={p} className="px-1.5 py-0.5 bg-darkBg text-text-secondary font-mono text-[8px] font-bold rounded border border-border-primary">
                        {p}
                      </span>
                    ))}
                    <span className={`px-1.5 py-0.5 font-mono text-[8px] font-bold rounded border ${
                      agent.trustLevel === 'SYSTEM' ? 'bg-socCritical/10 text-socCritical border-socCritical/30' : 'bg-gold-primary/10 text-gold-primary border-gold-primary/30'
                    }`}>
                      {agent.trustLevel}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>

          <div className="xl:col-span-5 space-y-4">
            <AnimatePresence mode="wait">
              {selectedAgent ? (
                <motion.div 
                  key="agent-deck"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="glass-panel p-6 flex flex-col gap-6"
                >
                  <div className="flex items-center justify-between border-b border-border-primary pb-4">
                    <button 
                      onClick={() => setSelectedAgent(null)}
                      className="flex items-center gap-2 text-xs font-mono font-bold text-text-secondary hover:text-gold-primary transition-all"
                    >
                      <ArrowLeft className="w-4 h-4" /> SWARM TELEMETRY
                    </button>
                    <span className="text-[10px] font-mono tracking-widest text-text-secondary font-bold uppercase flex items-center gap-1.5">
                      <Code className="w-3.5 h-3.5 text-gold-bright" /> MODEL: {selectedAgent.model}
                    </span>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-darkBg border border-gold-primary/30 rounded-xl flex items-center justify-center text-3xl shadow-glow">
                      {selectedAgent.avatar}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white tracking-wider">{selectedAgent.name} NODE</h2>
                      <p className="text-xs text-text-secondary mt-1 leading-relaxed">{selectedAgent.desc}</p>
                    </div>
                  </div>

                  <form onSubmit={handleExecuteCommand} className="space-y-3">
                    <label className="text-[10px] font-bold text-socInfo font-mono uppercase tracking-widest block">
                      DIRECT AGENT OVERRIDE
                    </label>
                    <div className="relative">
                      <input 
                        type="text"
                        placeholder="Inject instruction payload..."
                        value={commandText}
                        onChange={(e) => setCommandText(e.target.value)}
                        disabled={executingCommand}
                        className="w-full bg-darkBg border border-border-primary rounded-lg pl-4 pr-12 py-3 text-xs font-mono text-text-primary placeholder-[#888] focus:outline-none focus:border-gold-primary/50 transition-all"
                      />
                      <button 
                        type="submit"
                        disabled={executingCommand || !commandText.trim()}
                        className="absolute right-2 top-2 p-1.5 bg-gold-primary/10 border border-gold-primary/30 text-gold-primary rounded-md hover:bg-gold-primary hover:text-darkBg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        {executingCommand ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                      </button>
                    </div>
                  </form>

                  {(commandResult || commandError || executingCommand) && (
                    <div className="space-y-2 text-left">
                      <span className="text-[10px] font-bold text-text-secondary font-mono uppercase tracking-widest block">EXECUTION TRACE</span>
                      <div className="bg-darkBg border border-border-primary rounded-lg p-4 font-mono text-xs max-h-48 overflow-y-auto">
                        {executingCommand ? (
                          <span className="text-socWarning animate-pulse">Running audited payload...</span>
                        ) : commandError ? (
                          <p className="text-socCritical">{commandError}</p>
                        ) : (
                          <p className="text-socSuccess whitespace-pre-wrap">{commandResult}</p>
                        )}
                      </div>
                    </div>
                  )}
                </motion.div>
              ) : (
                <motion.div 
                  key="telemetry-deck"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="glass-panel p-6 flex flex-col gap-4"
                >
                  <h2 className="text-xs font-bold text-text-secondary font-mono uppercase tracking-widest flex items-center gap-2 mb-1">
                    <Terminal className="w-4 h-4 text-gold-bright animate-pulse" />
                    SWARM EVENT BUS
                  </h2>

                  <div className="bg-darkBg border border-border-primary rounded-xl p-4 font-mono text-[10px] leading-relaxed min-h-[460px] max-h-[460px] overflow-y-auto flex flex-col gap-2">
                    {agentsLogs && agentsLogs.length > 0 ? (
                      agentsLogs.map((log, i) => (
                        <div key={i} className={`p-3 border rounded-lg flex flex-col gap-1 transition-all ${
                          log.status === 'SUCCESS' ? 'bg-socSuccess/5 border-socSuccess/20 text-socSuccess' : 
                          log.status === 'FAILED' ? 'bg-socCritical/5 border-socCritical/20 text-socCritical' : 
                          'bg-gold-primary/5 border-gold-primary/20 text-gold-primary'
                        }`}>
                          <div className="flex items-center justify-between text-[9px] font-bold">
                            <span className="text-text-secondary">{new Date(log.timestamp).toLocaleTimeString()}</span>
                            <span className="uppercase tracking-widest">{log.agent_name}</span>
                          </div>
                          <p className="text-text-primary break-words mt-1 font-sans text-xs">{log.action_taken}</p>
                        </div>
                      ))
                    ) : (
                      <div className="flex flex-col items-center justify-center h-full text-text-secondary gap-2 py-24 select-none">
                        <Terminal className="w-6 h-6 animate-pulse" />
                        <span className="font-mono">LISTENING ON EVENT BUS...</span>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

        </div>
      </div>
    </div>
  );
}
