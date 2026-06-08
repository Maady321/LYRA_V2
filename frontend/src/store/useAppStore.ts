import { create } from 'zustand';
import { apiService } from '../services/api';
import type { Conversation, Message, ModelInfo, GalleryImage, AgentsTelemetry, AgentLog } from '../services/api';

interface AppSettings {
  system_prompt: string;
  temperature: number;
  max_tokens: number;
  context_window: number;
  theme: string;
  wake_system_enabled: boolean;
  tts_enabled: boolean;
  chat_enabled: boolean;
}

interface AppState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  models: ModelInfo[];
  activeModel: string;
  settings: AppSettings;
  isStreaming: boolean;
  isConnected: boolean;
  error: string | null;
  sidebarOpen: boolean;
  settingsOpen: boolean;
  
  currentView: 'chat' | 'gallery' | 'agents' | 'voice' | 'security';
  galleryImages: GalleryImage[];
  galleryLoading: boolean;

  agentsTelemetry: AgentsTelemetry | null;
  agentsLogs: AgentLog[];
  agentsLoading: boolean;

  // Actions
  setView: (view: 'chat' | 'gallery' | 'agents' | 'voice' | 'security') => void;
  fetchGalleryImages: () => Promise<void>;
  openImageNatively: (filename: string) => Promise<void>;
  deleteGalleryImage: (filename: string) => Promise<void>;
  fetchAgentsData: () => Promise<void>;
  fetchConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<string>;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
  
  fetchModels: () => Promise<void>;
  setActiveModel: (modelName: string) => void;
  
  loadSettings: () => Promise<void>;
  updateSetting: (key: keyof AppSettings, value: any) => Promise<void>;
  
  // UI Helpers
  setStreaming: (streaming: boolean) => void;
  setError: (error: string | null) => void;
  setConnectionStatus: (connected: boolean) => void;
  toggleSidebar: () => void;
  toggleSettings: () => void;
  addMessage: (message: Message) => void;
  updateLastAssistantMessage: (token: string) => void;
  finalizeLastAssistantMessage: (fullContent: string, metrics?: any) => void;
}

const defaultSettings: AppSettings = {
  system_prompt: "You are Lyra, a sophisticated, hyper-intelligent, local desktop AI assistant. Your responses should be precise, clear, and elegant. Code should be formatted with proper markdown syntax highlighting.",
  temperature: 0.7,
  max_tokens: 2048,
  context_window: 4096,
  theme: "dark",
  wake_system_enabled: true,
  tts_enabled: true,
  chat_enabled: true,
};

export const useAppStore = create<AppState>((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  models: [],
  activeModel: "llama3",
  settings: defaultSettings,
  isStreaming: false,
  isConnected: false,
  error: null,
  sidebarOpen: true,
  settingsOpen: false,
  currentView: 'chat',
  galleryImages: [],
  galleryLoading: false,
  agentsTelemetry: null,
  agentsLogs: [],
  agentsLoading: false,

  setView: (view) => set({ currentView: view }),

  fetchGalleryImages: async () => {
    set({ galleryLoading: true });
    try {
      const images = await apiService.getGalleryImages();
      set({ galleryImages: images, galleryLoading: false });
    } catch (e) {
      set({ error: "Failed to fetch generated images.", galleryLoading: false });
    }
  },

  fetchAgentsData: async () => {
    set({ agentsLoading: true });
    try {
      const [telemetry, logs] = await Promise.all([
        apiService.getAgentsTelemetry(),
        apiService.getAgentLogs()
       ]);
      set({ agentsTelemetry: telemetry, agentsLogs: logs, agentsLoading: false });
    } catch (e) {
      // Don't show critical errors if MJ db is not created yet
      set({ agentsLoading: false });
    }
  },

  openImageNatively: async (filename) => {
    try {
      await apiService.openImageNatively(filename);
    } catch (e) {
      set({ error: "Failed to open image natively." });
    }
  },

  deleteGalleryImage: async (filename) => {
    try {
      await apiService.deleteImage(filename);
      set((state) => ({
        galleryImages: state.galleryImages.filter((img) => img.filename !== filename),
      }));
    } catch (e) {
      set({ error: "Failed to delete image from workspace." });
    }
  },

  // --- CONVERSATIONS ---
  fetchConversations: async () => {
    try {
      const list = await apiService.getConversations();
      set({ conversations: list });
      
      // Auto select first conversation if none is active
      if (list.length > 0 && !get().currentConversationId) {
        await get().selectConversation(list[0].id);
      }
    } catch (e: any) {
      set({ error: "Failed to fetch conversations." });
    }
  },

  createConversation: async (title) => {
    try {
      const conv = await apiService.createConversation(title);
      set((state) => ({
        conversations: [conv, ...state.conversations],
        currentConversationId: conv.id,
        messages: [],
      }));
      return conv.id;
    } catch (e: any) {
      set({ error: "Failed to create conversation." });
      throw e;
    }
  },

  selectConversation: async (id) => {
    try {
      set({ currentConversationId: id, isStreaming: false });
      const conv = await apiService.getConversation(id);
      set({ messages: conv.messages || [] });
    } catch (e: any) {
      set({ error: "Failed to select conversation." });
    }
  },

  deleteConversation: async (id) => {
    try {
      await apiService.deleteConversation(id);
      set((state) => {
        const nextList = state.conversations.filter((c) => c.id !== id);
        let nextSelected = state.currentConversationId;
        
        if (state.currentConversationId === id) {
          nextSelected = nextList.length > 0 ? nextList[0].id : null;
        }
        
        return {
          conversations: nextList,
          currentConversationId: nextSelected,
          messages: [],
        };
      });

      const nextId = get().currentConversationId;
      if (nextId) {
        await get().selectConversation(nextId);
      }
    } catch (e: any) {
      set({ error: "Failed to delete conversation." });
    }
  },

  updateConversationTitle: async (id, title) => {
    try {
      const updated = await apiService.updateConversation(id, title);
      set((state) => ({
        conversations: state.conversations.map((c) => (c.id === id ? updated : c)),
      }));
    } catch (e: any) {
      set({ error: "Failed to rename conversation." });
    }
  },

  // --- MODELS ---
  fetchModels: async () => {
    try {
      const modelsList = await apiService.getModels();
      set({ models: modelsList });
      
      // Auto select first installed model if current model isn't in list
      if (modelsList.length > 0) {
        const hasCurrentModel = modelsList.some((m) => m.name === get().activeModel);
        if (!hasCurrentModel) {
          set({ activeModel: modelsList[0].name });
        }
      }
      set({ isConnected: true });
    } catch (e: any) {
      set({ isConnected: false, error: "Ollama offline. Make sure Ollama is active." });
    }
  },

  setActiveModel: (modelName) => {
    set({ activeModel: modelName });
  },

  // --- SETTINGS ---
  loadSettings: async () => {
    try {
      const dbSettings = await apiService.getSettings();
      const mapped: Partial<AppSettings> = {};
      
      dbSettings.forEach((s) => {
        if (s.key in defaultSettings) {
          const typedKey = s.key as keyof AppSettings;
          if (typeof defaultSettings[typedKey] === 'number') {
            (mapped as any)[typedKey] = Number(s.value);
          } else if (typeof defaultSettings[typedKey] === 'boolean') {
            (mapped as any)[typedKey] = s.value === 'true';
          } else {
            (mapped as any)[typedKey] = s.value;
          }
        }
      });
      
      set((state) => ({
        settings: { ...state.settings, ...mapped },
      }));
    } catch (e: any) {
      set({ error: "Failed to retrieve configuration settings." });
    }
  },

  updateSetting: async (key, value) => {
    try {
      const strVal = String(value);
      await apiService.updateSetting(key, strVal);
      set((state) => ({
        settings: {
          ...state.settings,
          [key]: value,
        },
      }));
    } catch (e: any) {
      set({ error: `Failed to save preference: ${key}` });
    }
  },

  // --- UI STATE ACTIONS ---
  setStreaming: (streaming) => set({ isStreaming: streaming }),
  setError: (err) => set({ error: err }),
  setConnectionStatus: (connected) => set({ isConnected: connected }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleSettings: () => set((state) => ({ settingsOpen: !state.settingsOpen })),
  
  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  updateLastAssistantMessage: (token) => {
    set((state) => {
      const list = [...state.messages];
      const lastIndex = list.length - 1;
      
      if (lastIndex >= 0 && list[lastIndex].role === 'assistant') {
        list[lastIndex] = {
          ...list[lastIndex],
          content: list[lastIndex].content + token,
        };
      }
      
      return { messages: list };
    });
  },

  finalizeLastAssistantMessage: (fullContent, metrics) => {
    set((state) => {
      const list = [...state.messages];
      const lastIndex = list.length - 1;
      
      if (lastIndex >= 0 && list[lastIndex].role === 'assistant') {
        list[lastIndex] = {
          ...list[lastIndex],
          content: fullContent,
          prompt_tokens: metrics?.prompt_eval_count,
          completion_tokens: metrics?.eval_count,
          total_duration: metrics?.total_duration,
        };
      }
      
      return { messages: list, isStreaming: false };
    });
  },


}));
