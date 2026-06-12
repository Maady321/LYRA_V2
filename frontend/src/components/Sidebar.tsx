import { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { Plus, Search, Trash2, Edit2, Check, MessageSquare, Settings, Database, Cpu, Mic, Shield, Network, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar() {
  const {
    conversations,
    currentConversationId,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
    sidebarOpen,
    toggleSettings,
    currentView,
    setView,
    fetchGalleryImages,
    settings,
  } = useAppStore();

  useEffect(() => {
    fetchGalleryImages();
  }, [fetchGalleryImages]);

  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async () => {
    try {
      const id = await createConversation('New Mission Thread');
      setView('chat');
      await selectConversation(id);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartRename = (id: string, currentTitle: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const handleSaveRename = async (id: string, e: React.FormEvent | React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (editTitle.trim()) {
      await updateConversationTitle(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to terminate this mission thread?")) {
      await deleteConversation(id);
    }
  };

  const navItems = [
    { id: 'home', label: 'Command Hub', icon: Shield, show: true, color: 'text-gold-primary', bg: 'bg-gold-primary' },
    { id: 'chat', label: 'Mission Console', icon: MessageSquare, show: settings.chat_enabled, color: 'text-gold-bright', bg: 'bg-gold-bright' },
    { id: 'agents', label: 'Autonomous Units', icon: Cpu, show: true, color: 'text-gold-elite', bg: 'bg-gold-elite' },
    { id: 'gallery', label: 'Intelligence Db', icon: Database, show: true, color: 'text-gold-primary', bg: 'bg-gold-primary' },
    { id: 'workflows', label: 'Mission Planner', icon: Network, show: true, color: 'text-gold-bright', bg: 'bg-gold-bright' },
    { id: 'voice', label: 'Tactical Voice', icon: Mic, show: true, color: 'text-gold-primary', bg: 'bg-gold-primary' },
    { id: 'security', label: 'Security Command', icon: Shield, show: true, color: 'text-gold-elite', bg: 'bg-gold-elite' },
    { id: 'observability', label: 'Observability', icon: Activity, show: true, color: 'text-gold-bright', bg: 'bg-gold-bright' },
  ];

  return (
    <aside
      className={`h-full bg-panel-bg flex flex-col border-r border-border-primary select-none font-sans transition-all duration-300 ${
        sidebarOpen ? 'w-72' : 'w-0 overflow-hidden border-r-0'
      }`}
    >
      {/* Tactical Brand logo bar */}
      <div className="flex items-center justify-between px-5 py-5 border-b border-border-primary bg-darkBg">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-primary-gradient flex items-center justify-center shadow-glow border border-gold-bright/30">
            <Shield className="w-4 h-4 text-black" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold text-text-primary tracking-wider">LYRA AIOS</span>
            <span className="text-[9px] text-gold-primary font-mono uppercase tracking-widest leading-none">Elite Operations</span>
          </div>
        </div>

        <button
          onClick={toggleSettings}
          className="p-1.5 hover:bg-panel-hover rounded-lg text-text-secondary hover:text-gold-primary hover:shadow-glow transition-all"
          title="System Control"
        >
          <Settings className="w-4.5 h-4.5" />
        </button>
      </div>

      {/* Modern Navigation Tabs */}
      <div className="flex flex-col px-3 py-4 gap-1.5 border-b border-border-primary bg-darkBg/50">
        {navItems.filter(item => item.show).map((item) => {
          const isActive = currentView === item.id;
          const Icon = item.icon;
          return (
            <motion.button
              key={item.id}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                setView(item.id as any);
                if (item.id === 'gallery') fetchGalleryImages();
              }}
              className={`flex items-center gap-3 px-3 py-2.5 text-xs font-semibold transition-all duration-200 relative overflow-hidden group hover:bg-[linear-gradient(90deg,rgba(255,215,0,.15),rgba(255,215,0,.03))] ${
                isActive
                  ? `text-gold-primary`
                  : 'text-text-secondary hover:text-text-primary'
              }`}
              style={{
                ...(isActive ? { 
                  background: 'linear-gradient(90deg, rgba(255,215,0,.15), rgba(255,215,0,.03))',
                  borderLeft: '3px solid #FFD700'
                } : {
                  borderLeft: '3px solid transparent'
                })
              }}
            >
              {isActive && (
                <motion.div 
                  initial={{ x: '-100%' }}
                  animate={{ x: '200%' }}
                  transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                  className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-gold-primary/20 to-transparent skew-x-12"
                />
              )}
              <Icon className={`w-4 h-4 z-10 ${isActive ? item.color : 'text-text-secondary'}`} />
              <span className="tracking-wide z-10">{item.label}</span>
              {isActive && (
                <div className={`ml-auto w-1.5 h-1.5 rounded-full z-10 ${item.bg} shadow-glow`} />
              )}
            </motion.button>
          );
        })}
      </div>

      {settings.chat_enabled ? (
        <>
          {/* Action triggers */}
          <div className="px-4 pt-5 pb-2">
            <button
              onClick={handleCreate}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-panel-hover border border-border-primary hover:border-gold-primary/50 text-gold-primary font-mono text-xs transition-all duration-300 hover:shadow-glow"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>NEW THREAD</span>
            </button>
          </div>

          {/* Search inputs */}
          <div className="px-4 py-2 relative">
            <input
              type="text"
              placeholder="Search logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-darkBg border border-border-primary rounded-lg pl-9 pr-3 py-2 text-xs text-text-primary placeholder-[#888] focus:outline-none focus:border-gold-primary/40 transition-all font-mono"
            />
            <Search className="w-3.5 h-3.5 text-text-secondary absolute left-7 top-4.5" />
          </div>

          {/* Conversations history list */}
          <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
            {filteredConversations.length === 0 ? (
              <div className="text-center py-10 text-[11px] text-text-secondary font-mono uppercase tracking-widest">
                No active operations
              </div>
            ) : (
              filteredConversations.map((c) => {
                const isActive = currentConversationId === c.id;
                const isEditing = editingId === c.id;
                
                return (
                  <div
                    key={c.id}
                    onClick={() => !isEditing && (setView('chat'), selectConversation(c.id))}
                    className={`group flex items-center justify-between px-3 py-2.5 rounded-lg border text-xs cursor-pointer transition-all duration-300 ${
                      isActive
                        ? 'bg-panel-hover border-gold-primary/20 text-text-primary'
                        : 'bg-transparent border-transparent text-text-secondary hover:bg-panel-hover/50 hover:text-text-primary'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isActive ? 'bg-gold-primary shadow-glow' : 'bg-panel-hover'}`} />
                      
                      {isEditing ? (
                        <form
                          onSubmit={(e) => handleSaveRename(c.id, e)}
                          className="flex items-center gap-1 min-w-0 w-full"
                        >
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            className="bg-darkBg border border-gold-primary/30 text-xs px-1.5 py-0.5 rounded text-text-primary w-full focus:outline-none font-mono"
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                          />
                          <button
                            type="submit"
                            className="p-0.5 hover:bg-panel-bg rounded text-gold-primary"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                        </form>
                      ) : (
                        <span className="truncate font-medium font-sans leading-none">{c.title}</span>
                      )}
                    </div>

                    {!isEditing && (
                      <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity gap-0.5 ml-1">
                        <button
                          onClick={(e) => handleStartRename(c.id, c.title, e)}
                          className="p-1 hover:bg-panel-bg rounded text-text-secondary hover:text-gold-primary"
                          title="Rename"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(c.id, e)}
                          className="p-1 hover:bg-panel-bg rounded text-text-secondary hover:text-socCritical"
                          title="Terminate"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-text-secondary">
          <Shield className="w-8 h-8 mb-4 opacity-20" />
          <p className="text-xs font-semibold uppercase tracking-wider mb-2">Tactical Core Mode</p>
          <p className="text-[10px] leading-relaxed">Console disabled. Voice operations active.</p>
        </div>
      )}

      {/* Footer bar */}
      <div className="px-5 py-3 bg-darkBg border-t border-border-primary flex items-center justify-between text-[10px] text-text-secondary font-mono">
        <span>SYS.STAT: <span className="text-socSuccess">NOMINAL</span></span>
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-socSuccess animate-pulse shadow-[0_0_8px_#00E676]" />
          <span>SECURED</span>
        </span>
      </div>
    </aside>
  );
}
