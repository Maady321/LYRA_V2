import { useEffect, lazy, Suspense } from 'react';
import { useAppStore } from './store/useAppStore';
import AppLayout from './layouts/AppLayout';
import { ErrorBoundary } from './components/ErrorBoundary';
import ChatPage from './pages/ChatPage';

// Lazy-loaded pages for code splitting
const GalleryPage = lazy(() => import('./pages/GalleryPage'));
const AgentsPage = lazy(() => import('./pages/AgentsPage'));
const VoicePage = lazy(() => import('./pages/VoicePage'));
const SecurityCenterPage = lazy(() => import('./pages/SecurityCenterPage'));
const ObservabilityPage = lazy(() => import('./pages/ObservabilityPage'));
const MissionPlannerPage = lazy(() => import('./pages/MissionPlannerPage'));
const LandingPage = lazy(() => import('./pages/LandingPage'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-gold-primary/30 border-t-gold-primary rounded-full animate-spin" />
        <span className="text-text-secondary text-sm font-medium">Loading module...</span>
      </div>
    </div>
  );
}

export default function App() {
  const { fetchConversations, fetchModels, loadSettings, currentView } = useAppStore();

  useEffect(() => {
    const logVoices = () => {
      try {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          const voiceList = voices.map(v => `${v.name} (${v.lang})`).join('\n');
          const fs = (window as any).require ? (window as any).require('fs') : null;
          if (fs) {
            const path = (window as any).require('path');
            const logPath = path.join(process.cwd(), 'voices.log');
            fs.writeFileSync(logPath, `Available Voices:\n${voiceList}`);
            console.log("Logged available voices to voices.log");
          }
        }
      } catch (e) {
        console.error("Failed to log voices:", e);
      }
    };

    logVoices();
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = logVoices;
    }
  }, []);

  useEffect(() => {
    // Startup initialization
    const bootApp = async () => {
      console.log("Starting Lyra V2 Core platform initialization sequence...");
      try {
        await Promise.all([
          loadSettings(),
          fetchConversations(),
          fetchModels(),
        ]);
        console.log("Lyra V2 Core platform services boot complete.");
      } catch (err) {
        console.error("Error during Lyra startup sequence:", err);
      }
    };

    bootApp();
  }, [fetchConversations, fetchModels, loadSettings]);

  return (
    <AppLayout>
      <ErrorBoundary>
        {currentView === 'chat' && <ChatPage />}
        {currentView === 'gallery' && (
          <Suspense fallback={<PageLoader />}>
            <GalleryPage />
          </Suspense>
        )}
        {currentView === 'agents' && (
          <Suspense fallback={<PageLoader />}>
            <AgentsPage />
          </Suspense>
        )}
        {currentView === 'voice' && (
          <Suspense fallback={<PageLoader />}>
            <VoicePage />
          </Suspense>
        )}
        {currentView === 'security' && (
          <Suspense fallback={<PageLoader />}>
            <SecurityCenterPage />
          </Suspense>
        )}
        {currentView === 'observability' && (
          <Suspense fallback={<PageLoader />}>
            <ObservabilityPage />
          </Suspense>
        )}
        {currentView === 'workflows' && (
          <Suspense fallback={<PageLoader />}>
            <MissionPlannerPage />
          </Suspense>
        )}
        {currentView === 'home' && (
          <Suspense fallback={<PageLoader />}>
            <LandingPage />
          </Suspense>
        )}
      </ErrorBoundary>
    </AppLayout>
  );
}
