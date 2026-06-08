import React, { useEffect, useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Activity, Lock, Key, Server, Terminal } from 'lucide-react';
import { apiClient } from '../services/api';

interface SecurityStatus {
  threat_score: number;
  active_blocks: number;
  prompt_injections: number;
  agent_violations: number;
  status: 'SECURE' | 'ELEVATED' | 'CRITICAL';
}

interface AuditLog {
  id: number;
  timestamp: string;
  user_name: string;
  agent_name: string;
  action: string;
  target: string;
  risk_level: string;
  result: string;
  ip_address: string;
}

export default function SecurityCenterPage() {
  const [status, setStatus] = useState<SecurityStatus | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, logsRes] = await Promise.all([
          apiClient.get('/security/status'),
          apiClient.get('/security/logs')
        ]);
        setStatus(statusRes.data);
        setLogs(logsRes.data);
      } catch (err) {
        console.error("Failed to fetch security telemetry", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !status) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  const getStatusColor = (s: string) => {
    if (s === 'SECURE') return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
    if (s === 'ELEVATED') return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
    return 'text-red-500 bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-slate-200">
      <div className="flex items-center gap-3 p-6 border-b border-slate-800/60 bg-darkSurface/50">
        <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            Guardian Security Kernel
            <span className={`text-xs px-2.5 py-0.5 rounded-full border font-bold tracking-wider ${getStatusColor(status.status)}`}>
              {status.status}
            </span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">Zero-Trust AIOS Telemetry & Intrusion Detection</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-darkSurface/40 border border-slate-800/60 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm font-medium">Threat Score</span>
              <Activity className={`w-5 h-5 ${status.threat_score > 80 ? 'text-emerald-500' : 'text-red-500'}`} />
            </div>
            <div className="text-4xl font-bold text-white">{status.threat_score}/100</div>
            <div className="text-xs text-slate-500 mt-2">Real-time risk assessment</div>
          </div>
          
          <div className="bg-darkSurface/40 border border-slate-800/60 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm font-medium">Active Blocks</span>
              <Lock className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-4xl font-bold text-white">{status.active_blocks}</div>
            <div className="text-xs text-slate-500 mt-2">Authentication failures mitigated</div>
          </div>

          <div className="bg-darkSurface/40 border border-slate-800/60 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm font-medium">Jailbreak Attempts</span>
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </div>
            <div className="text-4xl font-bold text-white">{status.prompt_injections}</div>
            <div className="text-xs text-slate-500 mt-2">Prompt firewall blocks</div>
          </div>

          <div className="bg-darkSurface/40 border border-slate-800/60 rounded-xl p-5 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-400 text-sm font-medium">Agent Violations</span>
              <Terminal className="w-5 h-5 text-indigo-500" />
            </div>
            <div className="text-4xl font-bold text-white">{status.agent_violations}</div>
            <div className="text-xs text-slate-500 mt-2">RBAC enforcement actions</div>
          </div>
        </div>

        {/* Audit Log Table */}
        <div className="bg-darkSurface/40 border border-slate-800/60 rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-800/60 flex items-center justify-between bg-slate-900/50">
            <h3 className="font-semibold text-slate-200 flex items-center gap-2">
              <Server className="w-4 h-4 text-slate-400" />
              Live Audit Trail
            </h3>
            <span className="text-xs text-slate-500 font-mono">Total Records: {logs.length}</span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/30 text-xs uppercase tracking-wider text-slate-500 border-b border-slate-800">
                  <th className="p-3 pl-4 font-medium">Timestamp</th>
                  <th className="p-3 font-medium">Agent</th>
                  <th className="p-3 font-medium">Action</th>
                  <th className="p-3 font-medium">Target</th>
                  <th className="p-3 font-medium">Risk</th>
                  <th className="p-3 pr-4 font-medium">Result</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-slate-500">
                      No security events logged yet.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="border-b border-slate-800/40 hover:bg-slate-800/20 transition-colors">
                      <td className="p-3 pl-4 text-slate-400 font-mono text-xs whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </td>
                      <td className="p-3">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300">
                          {log.agent_name}
                        </span>
                      </td>
                      <td className="p-3 text-cyan-400 font-mono text-xs">{log.action}</td>
                      <td className="p-3 text-slate-300 truncate max-w-xs" title={log.target}>{log.target}</td>
                      <td className="p-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          log.risk_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/20' : 
                          log.risk_level === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/20' : 
                          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/10'
                        }`}>
                          {log.risk_level}
                        </span>
                      </td>
                      <td className="p-3 pr-4">
                        <span className={`text-xs ${log.result.includes('BLOCKED') ? 'text-red-400' : 'text-emerald-400'}`}>
                          {log.result}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
