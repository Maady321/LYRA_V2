import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, Lock, Terminal, ShieldAlert, Cpu, Eye, Radio, XOctagon, Network } from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// Mock Data for SOC Visualizations
const threatTimelineData = [
  { time: '00:00', threats: 12, blocks: 10 },
  { time: '04:00', threats: 19, blocks: 15 },
  { time: '08:00', threats: 45, blocks: 45 },
  { time: '12:00', threats: 80, blocks: 78 },
  { time: '16:00', threats: 55, blocks: 50 },
  { time: '20:00', threats: 30, blocks: 30 },
  { time: '24:00', threats: 15, blocks: 15 },
];

const rbacData = [
  { category: 'Privilege Escalation', count: 120 },
  { category: 'Unauthorized Access', count: 45 },
  { category: 'Token Hijacking', count: 18 },
  { category: 'Policy Violation', count: 25 },
];

const guardianCoverageData = [
  { name: 'Covered', value: 92 },
  { name: 'Exposed', value: 8 },
];
const guardianColors = ['#FFD700', '#FF5252'];

const mockLogs = [
  { id: 1, time: '10:45:02', source: 'EXT_API', target: 'SYS.DB', risk: 'CRITICAL', action: 'DROP_TABLE', status: 'BLOCKED' },
  { id: 2, time: '10:44:15', source: 'AGENT_FURY', target: 'KERNEL', risk: 'HIGH', action: 'ELEVATE_PRIV', status: 'BLOCKED' },
  { id: 3, time: '10:42:01', source: 'USER_PROMPT', target: 'LLM_CORE', risk: 'HIGH', action: 'JAILBREAK_ATTEMPT', status: 'MITIGATED' },
  { id: 4, time: '10:40:55', source: 'VOICE_MOD', target: 'AUTH', risk: 'MEDIUM', action: 'VOICE_SPOOF', status: 'DENIED' },
  { id: 5, time: '10:35:10', source: 'AGENT_VISION', target: 'FS.READ', risk: 'LOW', action: 'SCAN_DIR', status: 'ALLOWED' },
];

export default function SecurityCenterPage() {
  const [score, setScore] = useState(98);

  useEffect(() => {
    // Simulate real-time score fluctuation
    const int = setInterval(() => {
      setScore(prev => Math.min(100, Math.max(85, prev + (Math.random() > 0.5 ? 1 : -1))));
    }, 3000);
    return () => clearInterval(int);
  }, []);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-text-secondary">
      
      {/* Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between p-6 border-b border-border-primary bg-panel-bg/50"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gold-primary/10 text-gold-primary rounded-xl border border-border-primary shadow-gold">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary flex items-center gap-3">
              Security Command Center
              <span className="text-xs px-3 py-1 rounded-full border font-bold tracking-widest text-gold-bright bg-gold-primary/10 border-border-primary uppercase shadow-gold">
                DEFCON 5
              </span>
            </h1>
            <p className="text-text-secondary text-sm mt-1 font-mono">Zero-Trust Telemetry & Intrusion Detection Active</p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm font-medium text-text-secondary">Global Threat Score</div>
          <div className={`text-5xl font-extrabold shadow-gold text-gold-bright`}>
            {score}%
          </div>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { label: 'Active Blocks', value: 124, icon: Lock, color: 'text-gold-primary' },
            { label: 'Prompt Injections', value: 45, icon: Terminal, color: 'text-gold-elite' },
            { label: 'RBAC Violations', value: 12, icon: XOctagon, color: 'text-socCritical' },
            { label: 'Voice Threats', value: 3, icon: Radio, color: 'text-gold-elite' },
            { label: 'Agent Anomalies', value: 0, icon: Cpu, color: 'text-gold-bright' },
          ].map((metric, idx) => (
            <motion.div 
              key={idx}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-panel p-5 flex flex-col justify-between hover:bg-panel-hover transition-colors shadow-gold group"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-text-secondary text-xs font-semibold uppercase tracking-wider">{metric.label}</span>
                <metric.icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              <div className="text-3xl font-bold text-text-primary font-mono">{metric.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-80">
          
          {/* Security Timeline */}
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-gold-primary" />
              Security Timeline (24h)
            </h3>
            <div className="flex-1 w-full h-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={threatTimelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FF5252" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FF5252" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorBlocks" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD700" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FFD700" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                  <Area type="monotone" dataKey="threats" stroke="#FF5252" fillOpacity={1} fill="url(#colorThreats)" strokeWidth={2} />
                  <Area type="monotone" dataKey="blocks" stroke="#FFD700" fillOpacity={1} fill="url(#colorBlocks)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Prompt Firewall Stats / RBAC */}
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <ShieldAlert className="w-4 h-4 text-gold-elite" />
              RBAC Monitoring
            </h3>
            <div className="flex-1 w-full h-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={rbacData} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" horizontal={false} />
                  <XAxis type="number" stroke="var(--text-secondary)" hide />
                  <YAxis dataKey="category" type="category" stroke="var(--text-secondary)" width={90} tick={{fontSize: 10}} />
                  <Tooltip cursor={{fill: 'var(--border-hover)'}} contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                  <Bar dataKey="count" fill="#FFD700" radius={[0, 4, 4, 0]} barSize={16} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Guardian Coverage */}
          <motion.div 
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Network className="w-4 h-4 text-gold-bright" />
              Guardian Coverage
            </h3>
            <div className="flex-1 w-full h-full flex flex-col items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={guardianCoverageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {guardianCoverageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={guardianColors[index % guardianColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none flex-col">
                <span className="text-3xl font-bold text-gold-primary">92%</span>
                <span className="text-xs text-text-secondary uppercase tracking-widest font-mono">Covered</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* IDS Dashboard / Log Table */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass-panel overflow-hidden flex flex-col shadow-gold"
        >
          <div className="p-4 border-b border-border-primary flex items-center justify-between bg-panel-bg/50">
            <h3 className="font-semibold text-text-primary flex items-center gap-2">
              <Eye className="w-4 h-4 text-gold-primary" />
              IDS Dashboard: Live Feed
            </h3>
            <div className="flex gap-2 items-center">
              <span className="w-2 h-2 rounded-full bg-socCritical animate-pulse" />
              <span className="text-xs text-text-secondary font-mono">SCANNING</span>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-panel-hover text-[10px] uppercase tracking-widest text-text-secondary border-b border-border-primary">
                  <th className="p-3 pl-5 font-semibold">Timestamp</th>
                  <th className="p-3 font-semibold">Source</th>
                  <th className="p-3 font-semibold">Target</th>
                  <th className="p-3 font-semibold">Action</th>
                  <th className="p-3 font-semibold">Risk Level</th>
                  <th className="p-3 pr-5 font-semibold">Result</th>
                </tr>
              </thead>
              <tbody className="text-sm font-mono">
                {mockLogs.map((log, i) => (
                  <motion.tr 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 + (i * 0.1) }}
                    key={log.id} 
                    className="border-b border-border-primary/50 hover:bg-panel-hover transition-colors"
                  >
                    <td className="p-3 pl-5 text-text-secondary text-xs">{log.time}</td>
                    <td className="p-3 text-gold-primary text-xs font-bold">{log.source}</td>
                    <td className="p-3 text-text-primary text-xs">{log.target}</td>
                    <td className="p-3 text-gold-elite text-xs">{log.action}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${
                        log.risk === 'CRITICAL' ? 'bg-[#FF5252]/20 text-[#FF5252] border border-[#FF5252]/30' : 
                        log.risk === 'HIGH' ? 'bg-[#FFB020]/20 text-[#FFB020] border border-[#FFB020]/30' : 
                        log.risk === 'MEDIUM' ? 'bg-gold-primary/20 text-gold-primary border border-border-primary' : 
                        'bg-gold-bright/10 text-gold-bright border border-border-primary/50'
                      }`}>
                        {log.risk}
                      </span>
                    </td>
                    <td className="p-3 pr-5 text-xs font-bold">
                      <span className={log.status === 'BLOCKED' ? 'text-[#FF5252]' : log.status === 'DENIED' ? 'text-[#FFB020]' : 'text-gold-primary shadow-gold'}>
                        {log.status}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
