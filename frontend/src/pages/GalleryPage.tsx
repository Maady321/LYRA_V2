import React, { useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { Database, Search, FolderTree, Network, ExternalLink, Trash2, GitMerge, BrainCircuit, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, AreaChart, Area, LineChart, Line } from 'recharts';

// Mock Data
const semanticClusters = [
  { x: 10, y: 30, z: 200, name: 'Threat Models' },
  { x: 30, y: 200, z: 260, name: 'Agent Memory' },
  { x: 45, y: 100, z: 400, name: 'Prompt Patterns' },
  { x: 50, y: 400, z: 280, name: 'RBAC Logs' },
  { x: 70, y: 150, z: 500, name: 'Vulnerability DB' },
  { x: 100, y: 250, z: 200, name: 'User Sessions' },
  { x: 110, y: 280, z: 200, name: 'Exploit Vectors' },
];

const intelligenceTimeline = [
  { time: '00:00', insights: 20, vectors: 40 },
  { time: '04:00', insights: 25, vectors: 55 },
  { time: '08:00', insights: 80, vectors: 120 },
  { time: '12:00', insights: 150, vectors: 210 },
  { time: '16:00', insights: 110, vectors: 180 },
  { time: '20:00', insights: 60, vectors: 90 },
  { time: '24:00', insights: 30, vectors: 45 },
];

const vectorStats = [
  { time: '1', ingestion: 120 },
  { time: '2', ingestion: 140 },
  { time: '3', ingestion: 200 },
  { time: '4', ingestion: 450 },
  { time: '5', ingestion: 320 },
  { time: '6', ingestion: 150 },
  { time: '7', ingestion: 130 },
];

export default function GalleryPage() {
  const { galleryImages, fetchGalleryImages, openImageNatively, deleteGalleryImage, galleryLoading } = useAppStore();

  useEffect(() => {
    fetchGalleryImages();
  }, [fetchGalleryImages]);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-darkBg text-text-secondary">
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between p-6 border-b border-border-primary bg-panel-bg/50"
      >
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gold-primary/10 text-gold-primary rounded-xl border border-border-primary shadow-gold">
            <Database className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text-primary flex items-center gap-3">
              Intelligence Database
              <span className="text-xs px-3 py-1 rounded-full border font-bold tracking-widest text-gold-bright bg-gold-primary/10 border-border-primary uppercase shadow-gold">
                VECTOR STORE
              </span>
            </h1>
            <p className="text-text-secondary text-sm mt-1 font-mono">Semantic Clusters & Memory Graph</p>
          </div>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'Total Vectors', value: '1.2M', icon: Database, color: 'text-gold-primary' },
            { label: 'Semantic Clusters', value: '42', icon: FolderTree, color: 'text-gold-elite' },
            { label: 'Knowledge Edges', value: '8.4K', icon: Network, color: 'text-gold-bright' },
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
                <metric.icon className={`w-5 h-5 ${metric.color} group-hover:text-gold-bright transition-colors`} />
              </div>
              <div className="text-3xl font-bold text-text-primary font-mono">{metric.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Dashboards Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-80">
          
          {/* Semantic Clusters */}
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <BrainCircuit className="w-4 h-4 text-gold-elite" />
              Semantic Cluster Distribution
            </h3>
            <div className="flex-1 w-full h-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis type="number" dataKey="x" name="dimension 1" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis type="number" dataKey="y" name="dimension 2" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                  <Scatter name="Clusters" data={semanticClusters} fill="#FFD700">
                    {semanticClusters.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#FFD700' : '#FFB300'} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Intelligence Timeline */}
          <motion.div 
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-gold-bright" />
              Intelligence Timeline (24h)
            </h3>
            <div className="flex-1 w-full h-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={intelligenceTimeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorVectors" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFB300" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FFB300" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorInsights" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FFD700" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#FFD700" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                  <Area type="monotone" dataKey="vectors" stroke="#FFB300" fillOpacity={1} fill="url(#colorVectors)" strokeWidth={2} />
                  <Area type="monotone" dataKey="insights" stroke="#FFD700" fillOpacity={1} fill="url(#colorInsights)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>

        {/* Vector Ingestion Rate */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-64">
           <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="glass-panel p-5 flex flex-col shadow-gold hover:shadow-premium transition-all lg:col-span-1"
          >
            <h3 className="font-semibold text-text-primary flex items-center gap-2 mb-4">
              <Database className="w-4 h-4 text-gold-elite" />
              Vector Ingestion Statistics
            </h3>
            <div className="flex-1 w-full h-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={vectorStats} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis dataKey="time" stroke="var(--text-secondary)" hide />
                  <YAxis stroke="var(--text-secondary)" tick={{fontSize: 10}} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--panel-bg)', borderColor: 'var(--border-primary)' }} />
                  <Line type="stepAfter" dataKey="ingestion" stroke="#FFD700" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Animated Knowledge Graph Placeholder */}
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="glass-panel p-5 flex flex-col items-center justify-center lg:col-span-2 shadow-gold relative overflow-hidden"
          >
             <div className="absolute inset-0 bg-[linear-gradient(rgba(255,215,0,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,215,0,0.05)_1px,transparent_1px)] bg-[size:20px_20px]" />
             <motion.div
               animate={{ rotate: 360 }}
               transition={{ duration: 150, repeat: Infinity, ease: "linear" }}
               className="relative z-10 w-64 h-64 flex items-center justify-center"
             >
                <GitMerge className="w-16 h-16 text-gold-primary opacity-20 absolute" />
                <div className="w-full h-full rounded-full border border-dashed border-gold-elite/30 absolute" />
                <div className="w-48 h-48 rounded-full border border-solid border-gold-primary/20 absolute" />
                {/* Node dots */}
                <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2 }} className="w-2 h-2 rounded-full bg-gold-bright absolute top-10 left-20 shadow-gold" />
                <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ repeat: Infinity, duration: 3, delay: 1 }} className="w-3 h-3 rounded-full bg-gold-primary absolute bottom-10 right-20 shadow-gold" />
                <motion.div animate={{ scale: [1, 1.3, 1] }} transition={{ repeat: Infinity, duration: 2.5, delay: 0.5 }} className="w-2 h-2 rounded-full bg-gold-elite absolute top-32 left-4 shadow-gold" />
             </motion.div>
             <div className="z-10 mt-4 text-center">
               <h3 className="text-text-primary font-semibold">Memory Relationship Graph</h3>
               <p className="text-text-secondary text-xs mt-1">Real-time edge computation active</p>
             </div>
          </motion.div>
        </div>

        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="glass-panel overflow-hidden flex flex-col shadow-gold"
        >
          <div className="p-4 border-b border-border-primary flex items-center justify-between bg-panel-bg/50">
            <h3 className="font-semibold text-text-primary flex items-center gap-2">
              <Search className="w-4 h-4 text-gold-primary" />
              Generated Assets & Visual Intelligence
            </h3>
            <span className="text-xs text-text-secondary font-mono">Count: {galleryImages.length}</span>
          </div>
          
          <div className="p-6">
            {galleryLoading ? (
              <div className="flex justify-center p-10"><div className="w-8 h-8 border-2 border-border-primary border-t-gold-primary rounded-full animate-spin" /></div>
            ) : galleryImages.length === 0 ? (
              <div className="text-center py-20 text-text-secondary font-mono text-sm">
                No visual intelligence assets found in the vector store.
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {galleryImages.map((img, i) => (
                  <motion.div 
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.1 * i }}
                    key={img.filename} 
                    className="group relative bg-panel-bg border border-border-primary rounded-xl overflow-hidden hover:border-border-hover hover:shadow-premium transition-all duration-300"
                  >
                    <div className="aspect-square overflow-hidden bg-darkBg relative">
                      <img 
                        src={`/api/gallery/${img.filename}`} 
                        alt={img.filename}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-darkBg via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    </div>
                    
                    <div className="p-3">
                      <p className="text-xs text-text-primary font-mono truncate" title={img.filename}>{img.filename}</p>
                      <div className="flex items-center justify-between mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => openImageNatively(img.filename)}
                          className="flex items-center gap-1.5 px-3 py-1.5 bg-gold-primary/10 hover:bg-gold-primary/20 text-gold-primary rounded text-[10px] font-bold tracking-wider transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" /> OPEN
                        </button>
                        <button 
                          onClick={() => deleteGalleryImage(img.filename)}
                          className="p-1.5 text-text-secondary hover:text-socCritical hover:bg-socCritical/10 rounded transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

      </div>
    </div>
  );
}
