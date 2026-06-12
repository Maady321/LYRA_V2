import React from 'react';
import { Network, PlayCircle, CheckCircle, Clock, AlertTriangle, Workflow } from 'lucide-react';
import { motion } from 'framer-motion';

const mockWorkflows = [
  { id: 'WF-772', name: 'Automated Threat Hunting', status: 'RUNNING', progress: 65, tasks: 12, completed: 8 },
  { id: 'WF-773', name: 'Nightly System Backup', status: 'QUEUED', progress: 0, tasks: 5, completed: 0 },
  { id: 'WF-774', name: 'Log Ingestion Pipeline', status: 'RUNNING', progress: 90, tasks: 3, completed: 2 },
  { id: 'WF-770', name: 'Malware Sandbox Analysis', status: 'COMPLETED', progress: 100, tasks: 8, completed: 8 },
  { id: 'WF-771', name: 'RBAC Sync', status: 'FAILED', progress: 45, tasks: 6, completed: 2 },
];

export default function MissionPlannerPage() {
  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-text-primary">
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
              Mission Planner
              <span className="text-xs px-3 py-1 rounded-full border font-bold tracking-widest text-gold-primary bg-gold-primary/10 border-gold-primary/30 uppercase">
                DAG ORCHESTRATION
              </span>
            </h1>
            <p className="text-text-secondary text-sm mt-1 font-mono">Workflow execution and task dependencies</p>
          </div>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'Active Missions', value: '2', icon: PlayCircle, color: 'text-gold-bright' },
            { label: 'Queued Missions', value: '1', icon: Clock, color: 'text-text-secondary' },
            { label: 'Success Rate', value: '98.5%', icon: CheckCircle, color: 'text-gold-elite' },
            { label: 'Failed Nodes', value: '1', icon: AlertTriangle, color: 'text-socCritical' },
          ].map((metric, idx) => (
            <motion.div 
              key={idx}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: idx * 0.1 }}
              className="glass-panel p-5 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-text-secondary text-xs font-semibold uppercase tracking-wider">{metric.label}</span>
                <metric.icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              <div className="text-3xl font-bold text-white font-mono">{metric.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Workflow Table */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass-panel overflow-hidden flex flex-col"
        >
          <div className="p-4 border-b border-border-primary flex items-center justify-between bg-panel-bg">
            <h3 className="font-semibold text-text-primary flex items-center gap-2">
              <Workflow className="w-4 h-4 text-gold-primary" />
              Mission Queues
            </h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-panel-hover/50 text-[10px] uppercase tracking-widest text-text-secondary border-b border-border-primary">
                  <th className="p-3 pl-5 font-semibold">Mission ID</th>
                  <th className="p-3 font-semibold">Name</th>
                  <th className="p-3 font-semibold">Status</th>
                  <th className="p-3 font-semibold">Progress</th>
                  <th className="p-3 pr-5 font-semibold">Nodes Completed</th>
                </tr>
              </thead>
              <tbody className="text-sm font-sans">
                {mockWorkflows.map((wf, i) => (
                  <motion.tr 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 + (i * 0.1) }}
                    key={wf.id} 
                    className="border-b border-border-primary/50 hover:bg-panel-hover/30 transition-colors"
                  >
                    <td className="p-3 pl-5 text-gold-bright font-mono text-xs font-bold">{wf.id}</td>
                    <td className="p-3 text-text-primary font-semibold">{wf.name}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${
                        wf.status === 'RUNNING' ? 'bg-gold-bright/20 text-gold-bright border border-gold-bright/30' : 
                        wf.status === 'FAILED' ? 'bg-socCritical/20 text-socCritical border border-socCritical/30' : 
                        wf.status === 'COMPLETED' ? 'bg-gold-primary/10 text-gold-primary border border-gold-primary/20' : 
                        'bg-panel-hover/50 text-text-secondary border border-border-primary/50'
                      }`}>
                        {wf.status}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="w-full bg-panel-bg rounded-full h-1.5 border border-border-primary">
                        <div 
                          className={`h-1.5 rounded-full ${
                            wf.status === 'FAILED' ? 'bg-socCritical' : wf.status === 'COMPLETED' ? 'bg-gold-primary' : 'bg-gold-bright shadow-glow'
                          }`} 
                          style={{ width: `${wf.progress}%` }}
                        ></div>
                      </div>
                    </td>
                    <td className="p-3 pr-5 text-xs text-text-secondary font-mono">
                      {wf.completed} / {wf.tasks}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* Visual DAG Placeholder */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="glass-panel p-6 flex flex-col items-center justify-center h-64 border-dashed"
        >
          <Network className="w-12 h-12 text-text-secondary mb-4" />
          <h3 className="text-text-primary font-semibold text-lg">Interactive DAG Visualizer</h3>
          <p className="text-text-secondary text-sm mt-2 max-w-md text-center">
            Node relationship rendering engine initializing. Awaiting task delegation trees from active agents.
          </p>
        </motion.div>

      </div>
    </div>
  );
}
