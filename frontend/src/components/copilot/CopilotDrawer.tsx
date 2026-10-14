import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, ActionChip } from '@/types/api';
import { X, Send, Bot, User, ChevronDown, ChevronRight, Sparkles, ShieldAlert, Terminal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface CopilotDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  companyId: string;
}

export const CopilotDrawer: React.FC<CopilotDrawerProps> = ({ isOpen, onClose, companyId }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello, I am your AuraCFO Autonomous Copilot. I analyze your ledger, forecast liquidity, monitor debt covenants, and help you draft collection notices with deterministic math and cryptographic governance.',
      timestamp: new Date().toLocaleTimeString(),
      actionChips: [
        { label: 'Explain Cash Runway', action: 'explain_runway' },
        { label: 'Review Covenant Breaches', action: 'covenants' },
        { label: 'View Overdue Invoices', action: 'invoices', route: '/operations' },
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedThoughts, setExpandedThoughts] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  if (!isOpen) return null;

  const toggleThought = (id: string) => {
    setExpandedThoughts((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId, message: userText }),
      });

      if (!response.ok) {
        throw new Error(`Chat request failed with status ${response.status}`);
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantText = '';
      let thoughts: any[] = [];
      let chips: ActionChip[] = [];
      let isBlocked = false;

      const assistantMsgId = `asst-${Date.now()}`;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));

                if (data.type === 'thought') {
                  thoughts.push({
                    step: data.step,
                    detail: data.detail,
                    timestamp: data.timestamp,
                    tool_call: data.tool_call,
                  });
                } else if (data.type === 'token') {
                  assistantText += data.token;
                } else if (data.type === 'action_chips') {
                  chips = data.chips || [];
                } else if (data.type === 'security_alert') {
                  isBlocked = true;
                  assistantText = data.message || 'Prompt injection intercepted.';
                }

                // Update UI state with partial output
                setMessages((prev) => {
                  const filtered = prev.filter((m) => m.id !== assistantMsgId);
                  return [
                    ...filtered,
                    {
                      id: assistantMsgId,
                      role: 'assistant',
                      content: assistantText,
                      timestamp: new Date().toLocaleTimeString(),
                      thoughts: [...thoughts],
                      actionChips: [...chips],
                      blocked: isBlocked,
                    },
                  ];
                });
              } catch {
                // Ignore parse errors on SSE delimiters
              }
            }
          }
        }
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `Error: ${err.message || 'Unable to communicate with copilot service.'}`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleChipClick = (chip: ActionChip) => {
    if (chip.route) {
      navigate(chip.route);
    } else {
      handleSendMessage(chip.label);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[440px] bg-[#11131A] border-l border-[#232738] shadow-2xl flex flex-col animate-in slide-in-from-right duration-250">
      {/* Header */}
      <div className="p-4 border-b border-[#232738] bg-[#181B24] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
              AuraCFO Copilot
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                LangGraph
              </span>
            </div>
            <div className="text-[11px] text-slate-400">Deterministic Financial Reasoning</div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-[#232738] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[90%] rounded-xl p-3.5 space-y-2 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white font-medium'
                  : msg.blocked
                  ? 'bg-red-950/30 border border-red-500/30 text-red-300'
                  : 'bg-[#181B24] border border-[#232738] text-slate-200'
              }`}
            >
              {/* Agent role / security header */}
              {msg.role === 'assistant' && (
                <div className="flex items-center justify-between border-b border-[#232738] pb-1 text-[10px] text-slate-400">
                  <span className="flex items-center gap-1 font-mono text-indigo-400">
                    <Sparkles className="w-3 h-3" /> AuraCFO Treasury Agent
                  </span>
                  <span>{msg.timestamp}</span>
                </div>
              )}

              {msg.blocked && (
                <div className="flex items-center gap-1.5 text-red-400 font-bold uppercase text-[10px]">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  Pre-Flight Security Alert: Attack Blocked
                </div>
              )}

              {/* Thoughts Stream (LangGraph reasoning) */}
              {msg.thoughts && msg.thoughts.length > 0 && (
                <div className="rounded-lg border border-indigo-500/20 bg-indigo-950/20 overflow-hidden my-2">
                  <button
                    onClick={() => toggleThought(msg.id)}
                    className="w-full p-2 flex items-center justify-between text-[11px] font-mono text-indigo-300 hover:bg-indigo-900/20"
                  >
                    <span className="flex items-center gap-1.5">
                      <Terminal className="w-3 h-3" /> Thought Stream ({msg.thoughts.length} steps)
                    </span>
                    {expandedThoughts[msg.id] ? (
                      <ChevronDown className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {expandedThoughts[msg.id] && (
                    <div className="p-2.5 border-t border-indigo-500/20 space-y-2 text-[11px] font-mono bg-[#090A0F]/80">
                      {msg.thoughts.map((t, idx) => (
                        <div key={idx} className="space-y-0.5 border-l-2 border-indigo-500/40 pl-2">
                          <span className="text-indigo-400 font-semibold">{t.step}: </span>
                          <span className="text-slate-300">{t.detail}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Message Content */}
              <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

              {/* Action Chips */}
              {msg.actionChips && msg.actionChips.length > 0 && (
                <div className="pt-2 flex flex-wrap gap-1.5">
                  {msg.actionChips.map((chip, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleChipClick(chip)}
                      className="px-2.5 py-1 rounded-md bg-[#232738] hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-medium transition-colors"
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono p-3 bg-[#181B24] border border-[#232738] rounded-xl max-w-[80%]">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
            Deterministic financial engine executing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Pills */}
      <div className="p-2.5 border-t border-[#232738] bg-[#0E1017] flex items-center gap-1.5 overflow-x-auto text-[11px]">
        {[
          'Explain my cash runway',
          'Why did CMSME scheme fail?',
          'Simulate 30-day debtor delay',
        ].map((pill, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(pill)}
            className="whitespace-nowrap px-2.5 py-1 rounded-full bg-[#181B24] hover:bg-[#232738] text-slate-300 border border-[#232738] transition-colors"
          >
            {pill}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-[#232738] bg-[#181B24]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask AuraCFO Copilot (e.g. runway, covenants, collections)..."
            className="flex-1 bg-[#090A0F] border border-[#232738] focus:border-indigo-500 focus:outline-none rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder:text-slate-500"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
