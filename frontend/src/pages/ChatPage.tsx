import { useWebSocket } from '../hooks/useWebSocket';
import ChatWindow from '../components/ChatWindow';

export default function ChatPage() {
  const { sendPrompt } = useWebSocket();

  return <ChatWindow sendPrompt={sendPrompt} />;
}
