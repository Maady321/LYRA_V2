import { useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import type { Message } from '../services/api';
import { getFemaleVoice } from '../utils/speech';

const WS_URL = 'ws://127.0.0.1:8000/api/ws/chat';

const speakResponse = async (text: string) => {
  try {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Cancel any ongoing speech

      // Clean markdown tags and code blocks for a warm, natural narration
      let cleanText = text
        .replace(/```[\s\S]*?```/g, '[code block omitted]')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/[*_~#]/g, '')
        .replace(/-\s+/g, '')
        .trim();

      if (!cleanText) return;

      const selectedVoice = await getFemaleVoice();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.05; // Slightly faster natural pacing
      utterance.pitch = 1.05; // Slightly warmer/friendly pitch
      utterance.volume = 0.9;

      const fs = (window as any).require ? (window as any).require('fs') : null;
      if (selectedVoice) {
        utterance.voice = selectedVoice;
        utterance.lang = selectedVoice.lang; // CRITICAL: match voice locale to prevent Windows male fallback
        if (fs) {
          try {
            const path = (window as any).require('path');
            fs.writeFileSync(path.join(process.cwd(), 'selected_voice.log'), `Selected Voice: ${selectedVoice.name} (${selectedVoice.lang})`);
          } catch (e) {}
        }
      } else {
        if (fs) {
          try {
            const path = (window as any).require('path');
            fs.writeFileSync(path.join(process.cwd(), 'selected_voice.log'), `Selected Voice: NONE (Fallback default used)`);
          } catch (e) {}
        }
      }

      window.speechSynthesis.speak(utterance);
    }
  } catch (err) {
    console.error("TTS voice readout failed:", err);
  }
};

export function useWebSocket() {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<any>(null);
  const reconnectAttemptRef = useRef(0);
  const MAX_RECONNECT_DELAY = 30000; // 30 seconds max
  
  const {
    currentConversationId,
    activeModel,
    settings,
    isStreaming,
    setStreaming,
    setError,
    setConnectionStatus,
    addMessage,
    updateLastAssistantMessage,
    finalizeLastAssistantMessage,
    fetchConversations,
  } = useAppStore();

  const connect = useCallback(() => {
    // Prevent double connections
    if (socketRef.current?.readyState === WebSocket.OPEN || socketRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    console.log("Establishing Lyra Core WebSocket channel...");
    const ws = new WebSocket(WS_URL);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket linked to core network.");
      reconnectAttemptRef.current = 0; // Reset backoff on successful connection
      setConnectionStatus(true);
      setError(null);
    };

    ws.onclose = (event) => {
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptRef.current), MAX_RECONNECT_DELAY);
      console.warn(`WebSocket closed: code ${event.code}. Reconnecting in ${delay / 1000}s (attempt ${reconnectAttemptRef.current + 1})...`);
      setConnectionStatus(false);
      setStreaming(false);
      
      // Auto reconnect with exponential backoff
      reconnectTimeoutRef.current = setTimeout(() => {
        reconnectAttemptRef.current++;
        connect();
      }, delay);
    };

    ws.onerror = (err) => {
      console.error("WebSocket network socket error:", err);
      setConnectionStatus(false);
      setStreaming(false);
      setError("WebSocket link failure. Backend server might be offline.");
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event: eventName, data } = payload;
        
        switch (eventName) {
          case 'chat_start':
            // Assistant response has begun streaming. Append blank message
            const initialMsg: Message = {
              id: data.message_id,
              conversation_id: data.conversation_id,
              role: 'assistant',
              content: '',
              model_used: data.model,
              timestamp: new Date().toISOString(),
            };
            addMessage(initialMsg);
            setStreaming(true);
            break;
            
          case 'chat_token':
            // Stream token
            updateLastAssistantMessage(data.token);
            break;
            
          case 'chat_end':
            // Generation terminated. Finalize
            finalizeLastAssistantMessage(data.full_content, data.metrics);
            
            // Speak response if voice narration is active
            if (settings.tts_enabled) {
              speakResponse(data.full_content);
            }

            // Reload conversations to update title summaries asynchronously
            setTimeout(() => {
              fetchConversations();
            }, 1000);

            break;
            
          case 'chat_error':
            console.error("WebSocket server-side error:", data.message);
            setError(data.message || "An unexpected error occurred during model generation.");
            setStreaming(false);
            break;
            
          default:
            console.log("Unhandled WebSocket event type:", eventName);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket packet:", err);
      }
    };
  }, [
    addMessage,
    updateLastAssistantMessage,
    finalizeLastAssistantMessage,
    fetchConversations,
    setConnectionStatus,
    setStreaming,
    setError,
  ]);

  // Handle manual message prompt submissions
  const sendPrompt = useCallback((content: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      setError("Cannot transmit prompt. Core network offline.");
      return;
    }

    if (!currentConversationId) {
      setError("No active conversation selected.");
      return;
    }

    if (isStreaming) {
      return; // Await current generation block
    }

    // Append standard client-side message representation immediately
    const userMsg: Message = {
      id: Math.random().toString(36).substring(7),
      conversation_id: currentConversationId,
      role: 'user',
      content: content,
      model_used: activeModel,
      timestamp: new Date().toISOString(),
    };
    
    addMessage(userMsg);
    setStreaming(true);
    setError(null);

    // Send payload to backend
    const payload = {
      event: "send_message",
      data: {
        conversation_id: currentConversationId,
        content: content,
        model: activeModel,
        system_prompt: settings.system_prompt,
        temperature: settings.temperature,
        max_tokens: settings.max_tokens,
        context_window: settings.context_window,
      },
    };

    socketRef.current.send(JSON.stringify(payload));
  }, [currentConversationId, activeModel, settings, isStreaming, addMessage, setStreaming, setError]);

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.onclose = null; // Prevent reconnect cycle during unmount
        socketRef.current.close();
      }
    };
  }, [connect]);

  return {
    sendPrompt,
    isConnected: socketRef.current?.readyState === WebSocket.OPEN,
  };
}
