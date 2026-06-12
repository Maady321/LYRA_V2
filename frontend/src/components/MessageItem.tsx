import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Cpu, Clock, Zap, User } from 'lucide-react';
import { type Message } from '../services/api';

interface MessageItemProps {
  message: Message;
}

export default function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user';
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);



  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const handleCopyCode = (code: string, blockId: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeId(blockId);
    setTimeout(() => setCopiedCodeId(null), 2000);
  };

  // Compute generation performance metrics
  const promptTokens = message.prompt_tokens;
  const completionTokens = message.completion_tokens;
  const durationNs = message.total_duration; // nanoseconds
  
  let speedTps = 0;
  let durationSec = 0;
  if (completionTokens && durationNs) {
    durationSec = durationNs / 1_000_000_000;
    speedTps = completionTokens / durationSec;
  }

  return (
    <div
      className={`flex gap-4 p-5 rounded-2xl border transition-all duration-300 ${
        isUser
          ? 'bg-panel-hover/10 border-border-primary/10'
          : 'bg-panel-bg/40 border-border-primary/20 glass-panel-light'
      }`}
    >
      {/* Avatar block */}
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-glow ${
          isUser
            ? 'bg-gold-primary/10 border border-gold-primary/30 text-gold-primary'
            : 'bg-gold-bright/10 border border-gold-bright/30 text-gold-bright animate-pulse'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Cpu className="w-5 h-5" />}
      </div>

      {/* Main message text & structure */}
      <div className="flex-1 min-w-0 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold tracking-wider uppercase text-text-secondary">
            {isUser ? 'Core Command' : 'Lyra Engine'}
          </span>
          <div className="flex items-center gap-2">

            <span className="text-[10px] font-semibold text-text-secondary font-mono select-none">
              {formatTime(message.timestamp)}
            </span>
          </div>
        </div>

        {/* Markdown parser content */}
        <div className="text-text-primary text-sm leading-relaxed font-sans select-text select-all-inside break-words prose prose-invert max-w-none">
          <ReactMarkdown
            children={message.content}
            components={{
              code: ({ node, inline, className, children, ...props }: any) => {
                const match = /language-(\w+)/.exec(className || '');
                const lang = match ? match[1] : 'plaintext';
                const codeString = String(children).replace(/\n$/, '');
                const blockId = Math.random().toString(36).substring(7);
                
                if (inline) {
                  return (
                    <code className="bg-darkBg/90 text-gold-primary border border-gold-primary/30 rounded px-1.5 py-0.5 text-xs font-mono font-medium break-words whitespace-pre-wrap shadow-glow">
                      {children}
                    </code>
                  );
                }

                // Destructure ref to prevent SyntaxHighlighter type collision
                const { ref, ...cleanProps } = props;

                return (
                  <div className="relative group my-4 rounded-xl overflow-hidden border border-border-primary shadow-premium">
                    {/* Header bar of code block */}
                    <div className="flex items-center justify-between px-4 py-2 bg-darkBg border-b border-border-primary/30 text-[10px] text-text-secondary font-mono font-semibold select-none">
                      <span>{lang.toUpperCase()}</span>
                      <button
                        onClick={() => handleCopyCode(codeString, blockId)}
                        className="flex items-center gap-1.5 hover:text-text-primary transition-colors"
                      >
                        {copiedCodeId === blockId ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-500" />
                            <span className="text-emerald-500 font-bold">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Code contents syntax highlighted */}
                    <SyntaxHighlighter
                      children={codeString}
                      style={vscDarkPlus as any}
                      language={lang}
                      PreTag="div"
                      wrapLongLines={true}
                      customStyle={{
                        margin: 0,
                        padding: '1rem',
                        background: '#060A13',
                        fontSize: '0.825rem',
                        fontFamily: 'Fira Code, JetBrains Mono, monospace',
                      }}
                      {...cleanProps}
                    />
                  </div>
                );
              },
            }}
          />
        </div>

        {/* Statistics metadata ribbon */}
        {!isUser && (promptTokens || completionTokens) && (
          <div className="flex flex-wrap gap-x-4 gap-y-2 mt-4 pt-3.5 border-t border-border-primary/30 text-[10px] text-text-secondary font-mono select-none">
            {message.model_used && (
              <span className="flex items-center gap-1">
                <Cpu className="w-3 h-3 text-text-secondary" />
                <span>{message.model_used}</span>
              </span>
            )}
            {durationSec > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-text-secondary" />
                <span>{durationSec.toFixed(2)}s generation</span>
              </span>
            )}
            {speedTps > 0 && (
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-gold-bright/70 animate-pulse" />
                <span className="font-semibold text-gold-bright">{speedTps.toFixed(1)} tok/s</span>
              </span>
            )}
            {completionTokens && (
              <span className="text-text-secondary">
                ({promptTokens} in / {completionTokens} out)
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
