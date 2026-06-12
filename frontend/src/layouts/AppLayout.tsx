import React from 'react';
import { useAppStore } from '../store/useAppStore';
import Sidebar from '../components/Sidebar';
import ModelSelector from '../components/ModelSelector';
import SettingsDrawer from '../components/SettingsDrawer';
import WakeSystemController from '../components/WakeSystemController';
import { Menu, Wifi, WifiOff, Settings, Volume2 } from 'lucide-react';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const { sidebarOpen, toggleSidebar, isConnected, toggleSettings, settings } = useAppStore();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-darkBg text-gold-primary font-mono select-none">
      
      {/* History Sidebar Panel */}
      <Sidebar />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        
        {/* Header Bar */}
        <header 
          className="h-16 border-b border-border-primary/40 px-6 flex items-center justify-between z-10 select-none"
          style={{ background: 'linear-gradient(180deg, rgba(255,215,0,.08), rgba(0,0,0,0))' }}
        >
          <div className="flex items-center gap-4">
            <button
              onClick={toggleSidebar}
              className="p-1.5 hover:bg-panel-bg/60 rounded-lg text-text-secondary hover:text-text-primary transition-all"
              title={sidebarOpen ? "Hide History" : "Show History"}
            >
              <Menu className="w-5 h-5" />
            </button>
            
            {/* Status light */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 bg-darkBg/50 border border-border-primary/30 px-2.5 py-1 rounded-lg">
                {isConnected ? (
                  <>
                    <Wifi className="w-3.5 h-3.5 text-emerald-500 animate-pulse" />
                    <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest leading-none">Online</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-3.5 h-3.5 text-red-500" />
                    <span className="text-[10px] font-bold text-red-500 uppercase tracking-widest leading-none">Disconnected</span>
                  </>
                )}
              </div>

              {/* Wake System Breathing Indicator */}
              <div className="flex items-center gap-1.5 bg-darkBg/50 border border-border-primary/30 px-2.5 py-1 rounded-lg select-none" title={settings.wake_system_enabled ? "Wake System is active and passively listening" : "Wake System is disabled"}>
                <Volume2 className={`w-3.5 h-3.5 ${
                  settings.wake_system_enabled ? 'text-gold-primary animate-pulse' : 'text-text-secondary'
                }`} />
                <span className={`text-[10px] font-bold uppercase tracking-widest leading-none ${
                  settings.wake_system_enabled ? 'text-gold-primary' : 'text-text-secondary'
                }`}>
                  Wake: {settings.wake_system_enabled ? 'Listening' : 'Off'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Model switch selection dropdown */}
            <ModelSelector />
            
            {/* Quick settings gear */}
            <button
              onClick={toggleSettings}
              className="p-2 hover:bg-panel-bg/50 rounded-lg text-text-secondary hover:text-gold-primary border border-transparent hover:border-gold-primary/15 hover:shadow-glow transition-all"
              title="Open preferences panel"
            >
              <Settings className="w-4.5 h-4.5" />
            </button>
          </div>
        </header>

        {/* Dynamic Page content */}
        <main className="flex-1 min-h-0 flex flex-col">
          {children}
        </main>
      </div>

      {/* Preferences sliding panel drawer */}
      <SettingsDrawer />

      {/* Background Wake System voice activation controller */}
      <WakeSystemController />
    </div>
  );
}
