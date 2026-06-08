import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-inject JWT token into requests
apiClient.interceptors.request.use(async (config) => {
  let token = localStorage.getItem('lyra_jwt_token');
  
  // Auto-login for local development if missing
  if (!token) {
    try {
      const params = new URLSearchParams();
      params.append('username', 'admin');
      params.append('password', 'secret');
      
      const response = await axios.post(`${API_BASE_URL}/security/token`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      token = response.data.access_token;
      if (token) localStorage.setItem('lyra_jwt_token', token);
    } catch (e) {
      console.error("Authentication failed against Security Kernel", e);
    }
  }
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_used?: string;
  timestamp: string;
  prompt_tokens?: number;
  completion_tokens?: number;
  total_duration?: number;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  messages?: Message[];
}

export interface Setting {
  key: string;
  value: string;
}

export interface ModelInfo {
  name: string;
  parameter_size?: string;
  context_size?: number;
  status: string;
  details?: string;
}

export interface GalleryImage {
  filename: string;
  url: string;
  filepath: string;
  timestamp: number;
  prompt: string;
}

export interface AgentInfo {
  name: string;
  role: string;
  desc: string;
  status: 'ONLINE' | 'BUSY' | 'OFFLINE';
}

export interface AgentsTelemetry {
  cpu: number;
  ram: number;
  disk: number;
  uptime: string;
  tasks_today: number;
  active_agent: string;
  agents: AgentInfo[];
}

export interface AgentLog {
  timestamp: string;
  agent_name: string;
  action_taken: string;
  status: 'SUCCESS' | 'FAILED' | 'INFO';
}


export const apiService = {
  // Health Check
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Models Endpoints
  getModels: async (): Promise<ModelInfo[]> => {
    const response = await apiClient.get<ModelInfo[]>('/models');
    return response.data;
  },

  // Conversations Endpoints
  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get<Conversation[]>('/conversations');
    return response.data;
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const response = await apiClient.get<Conversation>(`/conversations/${id}`);
    return response.data;
  },

  createConversation: async (title?: string): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>('/conversations', { title });
    return response.data;
  },

  updateConversation: async (id: string, title: string): Promise<Conversation> => {
    const response = await apiClient.put<Conversation>(`/conversations/${id}`, { title });
    return response.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await apiClient.delete(`/conversations/${id}`);
  },

  // Settings Endpoints
  getSettings: async (): Promise<Setting[]> => {
    const response = await apiClient.get<Setting[]>('/settings');
    return response.data;
  },

  updateSetting: async (key: string, value: string): Promise<Setting> => {
    const response = await apiClient.post<Setting>('/settings', { key, value });
    return response.data;
  },

  // Gallery Images Endpoints
  getGalleryImages: async (): Promise<GalleryImage[]> => {
    const response = await apiClient.get<GalleryImage[]>('/images');
    return response.data;
  },

  openImageNatively: async (filename: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.post<{ status: string; message: string }>(`/images/${filename}/open`);
    return response.data;
  },

  deleteImage: async (filename: string): Promise<{ status: string; message: string }> => {
    const response = await apiClient.delete<{ status: string; message: string }>(`/images/${filename}`);
    return response.data;
  },

  // Agents Telemetry Endpoints
  getAgentsTelemetry: async (): Promise<AgentsTelemetry> => {
    const response = await apiClient.get<AgentsTelemetry>('/agents');
    return response.data;
  },

  getAgentLogs: async (): Promise<AgentLog[]> => {
    const response = await apiClient.get<AgentLog[]>('/agents/logs');
    return response.data;
  },

  executeAgentCommand: async (agentName: string, command: string): Promise<{ status: string; agent: string; command: string; result: string }> => {
    const response = await apiClient.post('/agents/command', { agent_name: agentName, command });
    return response.data;
  },
};
