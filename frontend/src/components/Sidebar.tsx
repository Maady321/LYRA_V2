import { useState, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { Plus, Search, Trash2, Edit2, Check, MessageSquare, Settings, Image, Users, Mic } from 'lucide-react';

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
    galleryImages,
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
      const id = await createConversation('New Conversation');
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
    if (confirm("Are you sure you want to delete this session?")) {
      await deleteConversation(id);
    }
  };

  return (
    <aside
      className={`h-full bg-darkSurface flex flex-col border-r border-slate-800/40 select-none font-sans transition-all duration-300 ${
        sidebarOpen ? 'w-72' : 'w-0 overflow-hidden border-r-0'
      }`}
    >
      {/* Brand logo bar */}
      <div className="flex items-center justify-between px-5 py-5 border-b border-slate-800/40">
        <div className="flex items-center gap-2">
          <div className="w-6.5 h-6.5 rounded bg-gradient-to-tr from-cyan-500 to-brandPurple flex items-center justify-center p-0.5 shadow-glow">
            <span className="font-extrabold text-[13px] text-white tracking-tighter">LY</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[14px] font-bold text-slate-100 tracking-wider">LYRA CORE</span>
            <span className="text-[9px] text-brandBlue font-bold uppercase tracking-widest leading-none">Intelligence v1</span>
          </div>
        </div>

        <button
          onClick={toggleSettings}
          className="p-1.5 hover:bg-slate-800/50 rounded-lg text-slate-400 hover:text-slate-200 transition-all"
          title="App Settings"
        >
          <Settings className="w-4.5 h-4.5" />
        </button>
      </div>

      {/* Modern Navigation Tabs */}
      <div className="flex px-3 py-3 gap-1 border-b border-slate-800/30 bg-slate-900/10">
        {settings.chat_enabled && (
          <button
            onClick={() => setView('chat')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[10px] font-extrabold transition-all duration-300 border ${
              currentView === 'chat'
                ? 'bg-darkAccent/50 border-brandBlue/30 text-slate-100 shadow-[0_0_10px_rgba(6,182,212,0.06)]'
                : 'bg-transparent border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <MessageSquare className="w-3 h-3" />
            <span>Chat</span>
            <span className={`px-1 py-0.5 rounded-full text-[8px] leading-none ${
              currentView === 'chat' ? 'bg-brandBlue/20 text-brandBlue font-bold' : 'bg-slate-800/55 text-slate-500'
            }`}>
              {conversations.length}
            </span>
          </button>
        )}
        
        <button
          onClick={() => {
            setView('gallery');
            fetchGalleryImages();
          }}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[10px] font-extrabold transition-all duration-300 border ${
            currentView === 'gallery'
              ? 'bg-darkAccent/50 border-brandPurple/30 text-slate-100 shadow-[0_0_10px_rgba(168,85,247,0.06)]'
              : 'bg-transparent border-transparent text-slate-500 hover:text-slate-300'
          }`}
        >
          <Image className="w-3 h-3" />
          <span>Gallery</span>
          <span className={`px-1 py-0.5 rounded-full text-[8px] leading-none ${
            currentView === 'gallery' ? 'bg-brandPurple/20 text-brandPurple font-bold' : 'bg-slate-800/55 text-slate-500'
          }`}>
            {galleryImages.length}
          </span>
        </button>

        <button
          onClick={() => setView('voice')}
          className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[10px] font-extrabold transition-all duration-300 border ${
            currentView === 'voice'
              ? 'bg-darkAccent/50 border-cyan-400/30 text-slate-100 shadow-[0_0_10px_rgba(34,211,238,0.06)]'
              : 'bg-transparent border-transparent text-slate-500 hover:text-slate-300'
          }`}
        >
          <Mic className="w-3 h-3" />
          <span>Voice</span>
        </button>
      </div>

      {settings.chat_enabled ? (
        <>
          {/* Action triggers */}
          <div className="px-4 pt-4 pb-2">
            <button
              onClick={handleCreate}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-brandBlue to-brandPurple/90 hover:from-cyan-400 hover:to-brandPurple text-white font-semibold text-sm transition-all duration-300 shadow-glow hover:scale-[1.02]"
            >
              <Plus className="w-4 h-4" />
              <span>New Core Session</span>
            </button>
          </div>

          {/* Search inputs */}
          <div className="px-4 py-2 relative">
            <input
              type="text"
              placeholder="Filter history..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-darkBg border border-slate-800/50 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-300 placeholder-slate-600 focus:outline-none focus:border-brandBlue/40 focus:shadow-glow transition-all"
            />
            <Search className="w-3.5 h-3.5 text-slate-600 absolute left-7 top-4.5" />
          </div>

          {/* Conversations history list */}
          <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
            {filteredConversations.length === 0 ? (
              <div className="text-center py-10 text-[11px] text-slate-600">
                No session threads found
              </div>
            ) : (
              filteredConversations.map((c) => {
                const isActive = currentConversationId === c.id;
                const isEditing = editingId === c.id;
                
                return (
                  <div
                    key={c.id}
                    onClick={() => !isEditing && (setView('chat'), selectConversation(c.id))}
                    className={`group flex items-center justify-between px-3 py-2.5 rounded-xl border text-sm cursor-pointer transition-all duration-300 ${
                      isActive
                        ? 'bg-darkAccent/50 border-brandBlue/20 text-slate-100'
                        : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-800/20 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0 flex-1">
                      <MessageSquare className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-brandBlue' : 'text-slate-600'}`} />
                      
                      {isEditing ? (
                        <form
                          onSubmit={(e) => handleSaveRename(c.id, e)}
                          className="flex items-center gap-1 min-w-0 w-full"
                        >
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            className="bg-darkBg border border-brandBlue/30 text-xs px-1.5 py-0.5 rounded text-slate-200 w-full focus:outline-none"
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                          />
                          <button
                            type="submit"
                            className="p-0.5 hover:bg-slate-800 rounded text-brandBlue"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                        </form>
                      ) : (
                        <span className="truncate font-medium text-xs leading-none">{c.title}</span>
                      )}
                    </div>

                    {!isEditing && (
                      <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity gap-0.5 ml-1">
                        <button
                          onClick={(e) => handleStartRename(c.id, c.title, e)}
                          className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-brandBlue"
                          title="Rename"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(c.id, e)}
                          className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-red-400"
                          title="Delete"
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
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-slate-500">
          <Mic className="w-8 h-8 mb-4 opacity-20" />
          <p className="text-xs font-semibold uppercase tracking-wider mb-2">Voice First Mode</p>
          <p className="text-[10px] leading-relaxed">Text chat is disabled. You are interacting with Lyra completely via voice commands.</p>
        </div>
      )}

      {/* Footer bar */}
      <div className="px-4 py-3 bg-darkBg/60 border-t border-slate-800/40 text-center flex items-center justify-between text-[10px] text-slate-600 font-semibold">
        <span>Ollama Core</span>
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Active network</span>
        </span>
      </div>
    </aside>
  );
}
