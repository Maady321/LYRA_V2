import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, Cpu, Lock, Terminal, Globe, Network, AlertTriangle } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export default function LandingPage() {
  const { agentsTelemetry } = useAppStore();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
  };

  return (
    <div className="relative flex-1 flex flex-col items-center overflow-hidden bg-darkBg text-text-primary h-full">
      
      {/* Animated Intelligence Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,215,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,215,0,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      <motion.div 
        animate={{ y: [0, -40] }} 
        transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
        className="absolute inset-0 bg-[linear-gradient(rgba(255,215,0,0.05)_1px,transparent_1px)] bg-[size:40px_40px] opacity-30 pointer-events-none" 
      />

      {/* Gold Particle Field */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: "100%", x: Math.random() * 100 + "%" }}
            animate={{ opacity: [0, 0.5, 0], y: "-10%" }}
            transition={{ duration: 5 + Math.random() * 5, repeat: Infinity, delay: Math.random() * 5, ease: "linear" }}
            className="absolute w-1 h-1 bg-gold-primary rounded-full shadow-gold"
          />
        ))}
      </div>

      {/* Main Content Scrollable Area */}
      <div className="w-full h-full overflow-y-auto px-8 py-10 z-10 custom-scrollbar">
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col w-full max-w-7xl mx-auto gap-8"
        >
          
          {/* Header Section */}
          <motion.div variants={itemVariants} className="flex justify-between items-end mb-4">
            <div>
              <h1 className="text-4xl font-black tracking-widest text-transparent bg-clip-text bg-[linear-gradient(90deg,#FFD700,#FFE082)] mb-1 drop-shadow-lg flex items-center gap-4">
                <Shield className="w-10 h-10 text-gold-primary" />
                COMMAND HUB
              </h1>
              <p className="text-sm text-gold-primary/70 font-mono tracking-[0.2em] uppercase">
                Lyra AIOS Elite Operations
              </p>
            </div>
            <div className="flex gap-4">
               <div className="text-right">
                <div className="text-[10px] text-text-secondary font-mono tracking-widest">THREAT LEVEL</div>
                <div className="text-xl font-black text-gold-primary shadow-gold">ELEVATED</div>
               </div>
               <div className="text-right">
                <div className="text-[10px] text-text-secondary font-mono tracking-widest">GLOBAL STATUS</div>
                <div className="text-xl font-black text-[#00E676] glow-text-success">NOMINAL</div>
               </div>
            </div>
          </motion.div>

          {/* Top Row: Map & Telemetry */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Gold World Map (SVG Placeholder & Stats) */}
            <motion.div variants={itemVariants} className="glass-panel p-6 lg:col-span-2 flex flex-col justify-between shadow-gold relative overflow-hidden group">
              <div className="absolute inset-0 bg-panel-bg opacity-90 z-0" />
              <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none z-0">
                <Globe className="w-96 h-96 text-gold-primary" strokeWidth={0.5} />
              </div>
              <div className="relative z-10 flex items-center justify-between mb-8">
                <h2 className="text-sm font-bold text-text-primary tracking-widest uppercase flex items-center gap-2">
                  <Globe className="w-4 h-4 text-gold-elite" /> Global Operations
                </h2>
                <div className="flex gap-2">
                  <span className="w-2 h-2 rounded-full bg-gold-primary animate-pulse" />
                  <span className="text-[10px] font-mono text-gold-primary">SAT-LINK ACTIVE</span>
                </div>
              </div>
              
              <div className="relative z-10 grid grid-cols-3 gap-4 mt-auto">
                <div className="flex flex-col">
                  <span className="text-[10px] text-text-secondary tracking-widest font-mono">ACTIVE NODES</span>
                  <span className="text-3xl font-black text-text-primary font-mono">1,402</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] text-text-secondary tracking-widest font-mono">THREATS NEUTRALIZED</span>
                  <span className="text-3xl font-black text-gold-primary font-mono">8.4K</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] text-text-secondary tracking-widest font-mono">NETWORK INTEGRITY</span>
                  <span className="text-3xl font-black text-gold-bright font-mono">99.9%</span>
                </div>
              </div>
            </motion.div>

            {/* AI Telemetry */}
            <motion.div variants={itemVariants} className="glass-panel p-6 flex flex-col shadow-gold group">
              <h2 className="text-sm font-bold text-text-primary tracking-widest uppercase flex items-center gap-2 mb-6">
                <Cpu className="w-4 h-4 text-gold-elite" /> AI Core Telemetry
              </h2>
              <div className="space-y-6 flex-1">
                <div>
                  <div className="flex justify-between text-xs font-mono text-text-secondary mb-1">
                    <span>Processing Load</span>
                    <span className="text-gold-primary">42%</span>
                  </div>
                  <div className="h-1 w-full bg-darkBg rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: '42%' }} transition={{ duration: 1 }} className="h-full bg-gold-primary" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-mono text-text-secondary mb-1">
                    <span>Memory Allocation</span>
                    <span className="text-gold-elite">68%</span>
                  </div>
                  <div className="h-1 w-full bg-darkBg rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: '68%' }} transition={{ duration: 1, delay: 0.2 }} className="h-full bg-gold-elite" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-mono text-text-secondary mb-1">
                    <span>Network I/O</span>
                    <span className="text-gold-bright">85%</span>
                  </div>
                  <div className="h-1 w-full bg-darkBg rounded-full overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: '85%' }} transition={{ duration: 1, delay: 0.4 }} className="h-full bg-gold-bright" />
                  </div>
                </div>
              </div>
            </motion.div>

          </div>

          {/* Bottom Row: Feeds & Timeline */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Threat Intelligence Feed */}
            <motion.div variants={itemVariants} className="glass-panel overflow-hidden flex flex-col shadow-gold h-80">
              <div className="p-4 border-b border-border-primary bg-panel-hover/50 flex justify-between items-center">
                <h2 className="text-sm font-bold text-text-primary tracking-widest uppercase flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[#FF5252]" /> Live Threat Feed
                </h2>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {[
                  { time: '14:22:01', desc: 'Unauthorized access attempt blocked', risk: 'HIGH', color: 'text-[#FF5252]' },
                  { time: '14:21:45', desc: 'New malware signature detected', risk: 'MED', color: 'text-[#FFB020]' },
                  { time: '14:18:12', desc: 'Failed login from unknown IP', risk: 'LOW', color: 'text-gold-primary' },
                  { time: '14:15:00', desc: 'Port scan detected on gateway', risk: 'MED', color: 'text-[#FFB020]' },
                  { time: '14:10:33', desc: 'DDoS mitigation active', risk: 'HIGH', color: 'text-[#FF5252]' },
                ].map((log, i) => (
                  <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.1 }} key={i} className="flex flex-col gap-1 border-b border-border-primary/30 pb-2">
                    <div className="flex justify-between text-[10px] font-mono">
                      <span className="text-text-secondary">{log.time}</span>
                      <span className={`${log.color} tracking-widest`}>{log.risk}</span>
                    </div>
                    <span className="text-xs text-text-primary">{log.desc}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Knowledge Graph Snapshot */}
            <motion.div variants={itemVariants} className="glass-panel p-6 flex flex-col shadow-gold h-80 relative overflow-hidden">
               <div className="absolute inset-0 flex items-center justify-center opacity-20 pointer-events-none">
                 <Network className="w-48 h-48 text-gold-primary" />
               </div>
               <h2 className="text-sm font-bold text-text-primary tracking-widest uppercase flex items-center gap-2 mb-2 relative z-10">
                <Network className="w-4 h-4 text-gold-primary" /> Active Knowledge Graph
              </h2>
              <div className="relative z-10 flex-1 flex flex-col justify-end pb-4">
                <div className="text-4xl font-black text-gold-primary shadow-gold">1.2M</div>
                <div className="text-xs text-text-secondary tracking-widest uppercase">Semantic Edges</div>
              </div>
            </motion.div>

            {/* Mission Timeline */}
            <motion.div variants={itemVariants} className="glass-panel overflow-hidden flex flex-col shadow-gold h-80">
               <div className="p-4 border-b border-border-primary bg-panel-hover/50 flex justify-between items-center">
                <h2 className="text-sm font-bold text-text-primary tracking-widest uppercase flex items-center gap-2">
                  <Activity className="w-4 h-4 text-gold-elite" /> Mission Timeline
                </h2>
              </div>
              <div className="flex-1 overflow-y-auto p-4 relative custom-scrollbar">
                 <div className="absolute left-6 top-4 bottom-4 w-px bg-border-primary" />
                 {[
                  { title: 'Initialize System', status: 'DONE', color: 'bg-[#00E676]' },
                  { title: 'Establish Uplink', status: 'DONE', color: 'bg-[#00E676]' },
                  { title: 'Analyze Threat Vectors', status: 'ACTIVE', color: 'bg-gold-primary' },
                  { title: 'Deploy Countermeasures', status: 'PENDING', color: 'bg-text-secondary' },
                  { title: 'Secure Perimeter', status: 'PENDING', color: 'bg-text-secondary' },
                 ].map((step, i) => (
                   <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6 + i * 0.1 }} key={i} className="flex gap-4 mb-4 relative z-10">
                     <div className={`w-3 h-3 rounded-full mt-1 ${step.color} shadow-gold shrink-0 border-2 border-darkBg`} />
                     <div>
                       <div className="text-xs text-text-primary font-bold">{step.title}</div>
                       <div className="text-[10px] text-text-secondary font-mono tracking-widest uppercase">{step.status}</div>
                     </div>
                   </motion.div>
                 ))}
              </div>
            </motion.div>

          </div>

        </motion.div>
      </div>
    </div>
  );
}
