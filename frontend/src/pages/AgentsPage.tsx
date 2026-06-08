import { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { motion, AnimatePresence } from 'framer-motion';
import { apiService } from '../services/api';
import { 
  Users, Activity, RefreshCw, Cpu, Database, HardDrive, 
  Terminal, ShieldAlert, CheckCircle, Zap, AlertTriangle,
  Send, ArrowLeft, Shield, Code
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
  { name: "FURY", role: "Coordinator Agent", desc: "Main decision maker, parses queries and synthesizes final reports", model: "llama3:latest", permissions: ["FILE_READ", "FILE_WRITE", "NETWORK_HTTP"], trustLevel: "SYSTEM (Level 4)", avatar: "💀" },
  { name: "VISION", role: "Memory Agent", desc: "Handles SQLite dialogue persistence and semantic vector stores", model: "nomic-embed-text", permissions: ["FILE_READ", "FILE_WRITE"], trustLevel: "HIGH (Level 3)", avatar: "👁️" },
  { name: "CAPTAIN", role: "Planning Agent", desc: "Decomposes complex goals into actionable roadmaps", model: "llama3:latest", permissions: ["FILE_READ"], trustLevel: "HIGH (Level 3)", avatar: "🛡️" },
  { name: "BANNER", role: "Research Agent", desc: "Conducts local RAG scans and summarized research checks", model: "mistral:latest", permissions: ["FILE_READ"], trustLevel: "MEDIUM (Level 2)", avatar: "🧪" },
  { name: "STARK", role: "Execution Agent", desc: "Compiles and executes sandboxed Python automation tasks safely", model: "qwen2.5-coder:7b", permissions: ["FILE_READ", "FILE_WRITE", "CMD_EXEC"], trustLevel: "SYSTEM (Level 4)", avatar: "🦾" },
  { name: "JARVIS", role: "System Monitor Agent", desc: "Monitors machine CPU, RAM, Disk, and Ollama status using PSUtil", model: "llama3:latest", permissions: ["FILE_READ"], trustLevel: "MEDIUM (Level 2)", avatar: "🤖" },
  { name: "SPIDEY", role: "Notification Agent", desc: "Schedules non-blocking async background timers and alerts", model: "llama3:latest", permissions: ["FILE_READ"], trustLevel: "LOW (Level 1)", avatar: "🕸️" },
  { name: "GHOST", role: "Computer Control Agent", desc: "Executes audited shell tasks and native file system commands", model: "llama3:latest", permissions: ["FILE_READ", "FILE_WRITE", "CMD_EXEC"], trustLevel: "SYSTEM (Level 4)", avatar: "👻" },
  { name: "EAGLE", role: "Vision/OCR Agent", desc: "Interfaces local LLaVA/OCR models to translate layouts and read images", model: "llava:latest", permissions: ["FILE_READ"], trustLevel: "MEDIUM (Level 2)", avatar: "🦅" },
  { name: "NAVIGATOR", role: "Browser Automation Agent", desc: "Sandbox Playwright browser scraper that crawls pages and queries DDG", model: "qwen2.5-coder:7b", permissions: ["FILE_READ", "FILE_WRITE", "NETWORK_HTTP"], trustLevel: "HIGH (Level 3)", avatar: "🧭" }
];

export default function AgentsPage() {
  const { 
    agentsTelemetry, 
    agentsLogs, 
    agentsLoading, 
    fetchAgentsData 
  } = useAppStore();

  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<LocalAgent | null>(null);
  
  // Direct CLI command states
  const [commandText, setCommandText] = useState('');
  const [executingCommand, setExecutingCommand] = useState(false);
  const [commandResult, setCommandResult] = useState<string | null>(null);
  const [commandError, setCommandError] = useState<string | null>(null);

  // Poll diagnostic endpoints every 3 seconds for continuous live telemetry
  useEffect(() => {
    fetchAgentsData();
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAgentsData();
    }, 3000);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchAgentsData]);

  // Handle direct command submission to selected agent
  const handleExecuteCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAgent || !commandText.trim()) return;

    setExecutingCommand(true);
    setCommandResult(null);
    setCommandError(null);

    try {
      const response = await apiService.executeAgentCommand(selectedAgent.name, commandText.trim());
      if (response.status === 'success') {
        setCommandResult(response.result);
      } else {
        setCommandError(response.result || "Execution completed with warnings.");
      }
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || err.message || "Failed to execute command.";
      setCommandError(errMsg);
    } finally {
      setExecutingCommand(false);
    }
  };

  // Format hardware meters progress width
  const renderMeter = (val: number, colorClass: string) => {
    return (
      <div className="w-full space-y-1.5 text-left">
        <div className="flex justify-between text-xs font-semibold text-slate-400">
          <span>Usage</span>
          <span className="font-bold text-slate-200">{val.toFixed(1)}%</span>
        </div>
        <div className="h-2 w-full bg-darkBg/80 rounded-full overflow-hidden border border-slate-800/40 relative">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${val}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${colorClass}`}
          />
        </div>
      </div>
    );
  };

  // Get active status dynamically from database logs or mock status
  const getAgentStatus = (name: string) => {
    const dbAgent = agentsTelemetry?.agents?.find(a => a.name === name);
    return dbAgent ? dbAgent.status : "ONLINE";
  };

  return (
    <div className="flex-1 overflow-y-auto px-8 py-6 space-y-8 font-sans select-none text-slate-200">
      {/* Header Panel */}
      <div className="flex items-center justify-between border-b border-slate-800/45 pb-5">
        <div className="space-y-1 text-left">
          <h1 className="text-2xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-brandBlue to-purple-400 flex items-center gap-3">
            <Users className="w-7 h-7 text-brandBlue animate-pulse" />
            AIOS Agent Control Center
          </h1>
          <p className="text-xs text-slate-500">
            Real-time status, diagnostics logs, and direct command execution for all 10 specialized local agents.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Auto Refresh Toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1.5 rounded-xl border text-[11px] font-bold tracking-wider transition-all duration-300 ${
              autoRefresh 
                ? 'bg-brandBlue/10 border-brandBlue/30 text-brandBlue' 
                : 'bg-darkBg border-slate-800/50 text-slate-500'
            }`}
          >
            {autoRefresh ? "● AUTO REFRESH ACTIVE" : "○ MANUAL REFRESH ONLY"}
          </button>

          <button
            onClick={() => fetchAgentsData()}
            disabled={agentsLoading}
            className="p-2.5 bg-darkSurface hover:bg-slate-800/50 border border-slate-800/40 hover:border-slate-700/60 rounded-xl text-slate-400 hover:text-slate-200 hover:scale-105 transition-all active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
            title="Refresh Diagnostic Data"
          >
            <RefreshCw className={`w-4.5 h-4.5 ${agentsLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Grid: Health Metrics Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CPU Panel */}
        <div className="bg-darkSurface/65 backdrop-blur-md border border-slate-800/40 rounded-2xl p-5 hover:border-brandBlue/20 transition-all duration-300 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-brandBlue/10 border border-brandBlue/20 rounded-xl text-brandBlue">
              <Cpu className="w-5 h-5" />
            </div>
            <div className="text-left">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Processor Load</span>
              <h3 className="text-lg font-black text-slate-200 mt-0.5 leading-none">CPU Core Telemetry</h3>
            </div>
          </div>
          {renderMeter(agentsTelemetry?.cpu || 0, 'bg-gradient-to-r from-cyan-500 to-blue-600 shadow-[0_0_12px_rgba(6,182,212,0.4)]')}
        </div>

        {/* RAM Panel */}
        <div className="bg-darkSurface/65 backdrop-blur-md border border-slate-800/40 rounded-2xl p-5 hover:border-purple-400/20 transition-all duration-300 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400">
              <Database className="w-5 h-5" />
            </div>
            <div className="text-left">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Virtual Memory</span>
              <h3 className="text-lg font-black text-slate-200 mt-0.5 leading-none">RAM Usage Ratio</h3>
            </div>
          </div>
          {renderMeter(agentsTelemetry?.ram || 0, 'bg-gradient-to-r from-purple-500 to-pink-600 shadow-[0_0_12px_rgba(168,85,247,0.4)]')}
        </div>

        {/* Disk Panel */}
        <div className="bg-darkSurface/65 backdrop-blur-md border border-slate-800/40 rounded-2xl p-5 hover:border-emerald-400/20 transition-all duration-300 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
              <HardDrive className="w-5 h-5" />
            </div>
            <div className="text-left">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none">Storage Space</span>
              <h3 className="text-lg font-black text-slate-200 mt-0.5 leading-none">Disk Load Ratio</h3>
            </div>
          </div>
          {renderMeter(agentsTelemetry?.disk || 0, 'bg-gradient-to-r from-emerald-500 to-teal-600 shadow-[0_0_12px_rgba(16,185,129,0.4)]')}
        </div>
      </div>

      {/* Main split sections: 10 Agents Grid on left, Selected Agent Deck / Live logs on right */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Left Column: 10 Agent Cards */}
        <div className="xl:col-span-6 space-y-4">
          <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-2 text-left">
            <Activity className="w-4 h-4 text-brandBlue animate-pulse" />
            Select Agent to Control
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {ALL_10_AGENTS.map((agent) => {
              const status = getAgentStatus(agent.name);
              const isSelected = selectedAgent?.name === agent.name;
              
              return (
                <div 
                  key={agent.name}
                  onClick={() => {
                    setSelectedAgent(agent);
                    setCommandText('');
                    setCommandResult(null);
                    setCommandError(null);
                  }}
                  className={`bg-darkSurface/50 backdrop-blur-md border rounded-2xl p-4 text-left cursor-pointer transition-all duration-300 flex flex-col justify-between h-40 ${
                    isSelected 
                      ? 'border-brandBlue shadow-[0_0_15px_rgba(6,182,212,0.15)] bg-darkSurface/80 scale-[1.01]' 
                      : 'border-slate-800/35 hover:border-slate-700/60 hover:bg-darkSurface/70 hover:scale-[1.01]'
                  }`}
                >
                  <div className="flex items-start justify-between w-full">
                    {/* Circle avatar badge */}
                    <div className="w-10 h-10 bg-slate-900 border border-slate-800 rounded-full flex items-center justify-center font-bold text-lg shadow-inner">
                      {agent.avatar}
                    </div>

                    {/* Status Pills */}
                    <div>
                      {status === 'ONLINE' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[8px] font-black tracking-wider bg-emerald-500/10 border border-emerald-500/35 text-emerald-400">
                          <CheckCircle className="w-2 h-2" />
                          ONLINE
                        </span>
                      ) : status === 'BUSY' ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[8px] font-black tracking-wider bg-amber-500/10 border border-amber-500/40 text-amber-400 animate-pulse">
                          <Zap className="w-2 h-2" />
                          BUSY
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[8px] font-black tracking-wider bg-red-500/10 border border-red-500/30 text-red-400">
                          <ShieldAlert className="w-2 h-2" />
                          OFFLINE
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-1 mt-3">
                    <div className="flex items-center gap-1.5">
                      <span className="font-extrabold text-sm text-slate-100">{agent.name}</span>
                      <span className="text-[9px] font-bold text-slate-500 tracking-wider">[{agent.model}]</span>
                    </div>
                    <p className="text-[10px] text-slate-400 leading-snug line-clamp-2">
                      {agent.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Agent Deck / Live Logs Console */}
        <div className="xl:col-span-6 space-y-4">
          <AnimatePresence mode="wait">
            {selectedAgent ? (
              /* Selected Agent Control Panel */
              <motion.div 
                key="agent-deck"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="bg-darkSurface/60 backdrop-blur-md border border-slate-800/40 rounded-2xl p-6 flex flex-col gap-6 text-left"
              >
                {/* Back Link Header */}
                <div className="flex items-center justify-between border-b border-slate-800/40 pb-4">
                  <button 
                    onClick={() => setSelectedAgent(null)}
                    className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-200 transition-all"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Core logs
                  </button>

                  <span className="text-[10px] font-mono tracking-widest text-slate-500 font-bold uppercase flex items-center gap-1.5">
                    <Shield className="w-3.5 h-3.5 text-brandPurple" />
                    Trust: {selectedAgent.trustLevel}
                  </span>
                </div>

                {/* Identity header */}
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-slate-900 border-2 border-brandBlue/35 rounded-2xl flex items-center justify-center text-3xl shadow-glow">
                    {selectedAgent.avatar}
                  </div>
                  <div className="space-y-0.5">
                    <h2 className="text-xl font-black text-slate-100 flex items-center gap-2">
                      {selectedAgent.name}
                      <span className="text-xs font-black px-2 py-0.5 rounded-full bg-brandBlue/10 border border-brandBlue/30 text-brandBlue uppercase tracking-wider">
                        {selectedAgent.role.split(" ")[0]}
                      </span>
                    </h2>
                    <p className="text-xs text-slate-400 leading-relaxed font-medium">
                      {selectedAgent.desc}
                    </p>
                  </div>
                </div>

                {/* Tech specifications details */}
                <div className="grid grid-cols-2 gap-4 bg-slate-900/40 border border-slate-800/30 rounded-xl p-4 text-xs">
                  <div className="space-y-1">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Local Model Target</span>
                    <p className="font-extrabold text-slate-200 font-mono flex items-center gap-1.5">
                      <Code className="w-3.5 h-3.5 text-brandPurple" />
                      {selectedAgent.model}
                    </p>
                  </div>

                  <div className="space-y-1">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-[9px]">Access Privileges</span>
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {selectedAgent.permissions.map(p => (
                        <span key={p} className="px-1.5 py-0.5 bg-darkBg text-slate-400 font-mono text-[8px] font-bold rounded border border-slate-800/50">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Command CLI Console Input Form */}
                <form onSubmit={handleExecuteCommand} className="space-y-3.5">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                    Direct Agent Instruction CLI
                  </label>
                  <div className="relative">
                    <input 
                      type="text"
                      placeholder={`Instruct ${selectedAgent.name}... (e.g., "${selectedAgent.name === 'STARK' ? 'Generate python prime factors code' : selectedAgent.name === 'NAVIGATOR' ? 'Search for latest space launch news' : 'Execute diagnostic check'}")`}
                      value={commandText}
                      onChange={(e) => setCommandText(e.target.value)}
                      disabled={executingCommand}
                      className="w-full bg-[#05070d] border border-slate-800/60 rounded-xl pl-4 pr-12 py-3 text-xs font-mono text-slate-200 placeholder-slate-600 focus:outline-none focus:border-brandBlue/60 focus:shadow-glow transition-all disabled:opacity-40"
                    />
                    <button 
                      type="submit"
                      disabled={executingCommand || !commandText.trim()}
                      className="absolute right-2 top-2 p-1.5 bg-brandBlue hover:bg-cyan-400 text-slate-900 rounded-lg hover:scale-105 active:scale-95 transition-all disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed"
                    >
                      {executingCommand ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </form>

                {/* Output Console Box */}
                {(commandResult || commandError || executingCommand) && (
                  <div className="space-y-2 text-left">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">
                      Execution Response Console
                    </span>
                    <div className="bg-[#030509]/95 border border-slate-800/50 rounded-xl p-4 font-mono text-xs leading-relaxed max-h-56 min-h-24 overflow-y-auto relative shadow-inner">
                      {executingCommand ? (
                        <div className="flex flex-col items-center justify-center h-24 text-brandBlue/80 gap-2">
                          <RefreshCw className="w-6 h-6 animate-spin" />
                          <span className="text-[10px] animate-pulse">Agent is thinking, planning, and executing offline...</span>
                        </div>
                      ) : commandError ? (
                        <p className="text-red-400">{commandError}</p>
                      ) : (
                        <p className="text-emerald-400 whitespace-pre-wrap break-words">{commandResult}</p>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            ) : (
              /* Live Event Logs Console */
              <motion.div 
                key="telemetry-deck"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.2 }}
                className="bg-darkSurface/65 border border-slate-800/40 rounded-2xl p-6 flex flex-col gap-4 text-left"
              >
                <h2 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-1">
                  <Terminal className="w-4 h-4 text-brandBlue animate-pulse" />
                  Central Event Bus Telemetry
                </h2>

                <div className="bg-[#05070d]/90 border border-slate-800/40 rounded-2xl p-5 font-mono text-[10px] leading-relaxed shadow-premium min-h-[415px] max-h-[415px] overflow-y-auto flex flex-col gap-2">
                  {agentsLogs && agentsLogs.length > 0 ? (
                    agentsLogs.map((log, i) => (
                      <div 
                        key={i} 
                        className={`py-2 px-3.5 border rounded-xl flex flex-col gap-0.5 text-left transition-all ${
                          log.status === 'SUCCESS' 
                            ? 'bg-emerald-950/15 border-emerald-900/30 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.02)]' 
                            : log.status === 'FAILED' 
                            ? 'bg-red-950/15 border-red-900/30 text-red-400' 
                            : 'bg-blue-950/10 border-blue-900/30 text-blue-400'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[9px] font-bold">
                          <span className="text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                          <span className={`uppercase font-black tracking-widest ${
                            log.status === 'SUCCESS' ? 'text-emerald-500' : log.status === 'FAILED' ? 'text-red-500' : 'text-brandBlue'
                          }`}>
                            {log.agent_name}
                          </span>
                        </div>
                        <p className="text-slate-300 break-words mt-1 leading-normal font-medium">
                          {log.action_taken}
                        </p>
                      </div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-600 gap-1.5 py-24 select-none">
                      <Terminal className="w-6 h-6 animate-pulse" />
                      <span className="text-[10px] font-medium italic">Listening on bus message queue...</span>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
