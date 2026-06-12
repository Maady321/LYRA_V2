import React from 'react';
import { Activity, Cpu, Server, Network, Database, Hexagon, Clock, HardDrive } from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const cpuData = [
  { time: '0s', main: 45, agents: 20 },
  { time: '10s', main: 48, agents: 25 },
  { time: '20s', main: 52, agents: 35 },
  { time: '30s', main: 80, agents: 65 },
  { time: '40s', main: 55, agents: 30 },
  { time: '50s', main: 45, agents: 22 },
  { time: '60s', main: 46, agents: 20 },
];

const memoryData = [
  { time: '0s', heap: 2.1, context: 0.5 },
  { time: '10s', heap: 2.2, context: 0.52 },
  { time: '20s', heap: 2.6, context: 0.6 },
  { time: '30s', heap: 3.0, context: 0.8 },
  { time: '40s', heap: 3.1, context: 0.85 },
  { time: '50s', heap: 2.8, context: 0.6 },
  { time: '60s', heap: 2.7, context: 0.58 },
];

const dbData = [
  { time: '0s', reads: 120, writes: 45 },
  { time: '10s', reads: 140, writes: 50 },
  { time: '20s', reads: 200, writes: 80 },
  { time: '30s', reads: 450, writes: 120 },
  { time: '40s', reads: 320, writes: 90 },
  { time: '50s', reads: 150, writes: 55 },
  { time: '60s', reads: 130, writes: 48 },
];

const latencyData = [
  { time: '0s', fury: 12, vision: 45, stark: 8 },
  { time: '10s', fury: 15, vision: 48, stark: 9 },
  { time: '20s', fury: 22, vision: 120, stark: 15 },
  { time: '30s', fury: 85, vision: 450, stark: 40 },
  { time: '40s', fury: 30, vision: 80, stark: 12 },
  { time: '50s', fury: 14, vision: 50, stark: 8 },
  { time: '60s', fury: 12, vision: 44, stark: 7 },
];

const redisData = [
  { time: '0s', hits: 980, misses: 20 },
  { time: '10s', hits: 1050, misses: 25 },
  { time: '20s', hits: 1200, misses: 40 },
  { time: '30s', hits: 2500, misses: 150 },
  { time: '40s', hits: 1800, misses: 80 },
  { time: '50s', hits: 1100, misses: 30 },
  { time: '60s', hits: 990, misses: 22 },
];

const networkData = [
  { time: '0s', ingress: 4.5, egress: 2.1 },
  { time: '10s', ingress: 4.8, egress: 2.3 },
  { time: '20s', ingress: 8.2, egress: 5.5 },
  { time: '30s', ingress: 25.0, egress: 18.4 },
  { time: '40s', ingress: 12.5, egress: 8.0 },
  { time: '50s', ingress: 5.0, egress: 2.5 },
  { time: '60s', ingress: 4.6, egress: 2.2 },
];

export default function ObservabilityPage() {
  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-text-secondary">
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between p-6 border-b border-border-primary bg-panel-bg/50"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gold-primary/10 text-gold-primary rounded-xl border border-border-primary shadow-gold">
            <Activity className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary flex items-center gap-3">
              System Observability
              <span className="text-xs px-3 py-1 rounded-full border font-bold tracking-widest text-gold-bright bg-gold-primary/10 border-border-primary uppercase">
                TRACING ACTIVE
              </span>
            </h1>
            <p className="text-text-secondary text-sm mt-1 font-mono">Distributed Tracing & Hardware Telemetry</p>
          </div>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {[
            { label: 'CPU Load', value: '46%', icon: Cpu },
            { label: 'Mem Alloc', value: '1.2 GB', icon: Server },
            { label: 'DB IOPS', value: '840/s', icon: HardDrive },
            { label: 'Latency', value: '24ms', icon: Clock },
            { label: 'Redis Ops', value: '1.4K/s', icon: Database },
            { label: 'Net I/O', value: '4.5M/s', icon: Network },
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
                <metric.icon className="w-5 h-5 text-gold-primary group-hover:text-gold-bright transition-colors" />
              </div>
              <div className="text-2xl font-bold text-text-primary font-mono">{metric.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Dashboards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          
          {/* CPU Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Cpu className="w-4 h-4 text-gold-elite" /> CPU Utilization
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cpuData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorMain" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD700" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FFD700" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} />
                  <Area type="monotone" dataKey="main" stroke="#FFD700" fillOpacity={1} fill="url(#colorMain)" strokeWidth={2} />
                  <Line type="monotone" dataKey="agents" stroke="#FFB300" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Memory Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Server className="w-4 h-4 text-gold-elite" /> Memory Footprint (GB)
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={memoryData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} />
                  <Line type="monotone" dataKey="heap" stroke="#FFB300" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="context" stroke="#FFE082" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Database Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.4 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <HardDrive className="w-4 h-4 text-gold-elite" /> DB Throughput (IOPS)
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dbData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} cursor={{fill: 'var(--border-primary)'}} />
                  <Bar dataKey="reads" fill="#FFD700" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="writes" fill="#CC8A00" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Agent Latency Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.5 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Clock className="w-4 h-4 text-gold-elite" /> Agent Latency (ms)
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={latencyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} />
                  <Line type="monotone" dataKey="fury" stroke="#FFD700" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="vision" stroke="#FF5252" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="stark" stroke="#FFE082" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Redis Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.6 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Database className="w-4 h-4 text-gold-elite" /> Redis Cache Hits/Misses
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={redisData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorHits" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD700" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#FFD700" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} />
                  <Area type="monotone" dataKey="hits" stroke="#FFD700" fillOpacity={1} fill="url(#colorHits)" strokeWidth={2} />
                  <Area type="monotone" dataKey="misses" stroke="#CC8A00" fillOpacity={0.5} fill="#CC8A00" strokeWidth={1} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Network Dashboard */}
          <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.7 }} className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all h-72">
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Network className="w-4 h-4 text-gold-elite" /> Network I/O (MB/s)
            </h3>
            <div className="flex-1 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={networkData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)', color: 'var(--text-primary)' }} />
                  <Line type="stepAfter" dataKey="ingress" stroke="#FFD700" strokeWidth={2} dot={false} />
                  <Line type="stepAfter" dataKey="egress" stroke="#FFB300" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
