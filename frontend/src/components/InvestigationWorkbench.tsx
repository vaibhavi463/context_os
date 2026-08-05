import React, { useState } from 'react';
import { Send, Shield, BookOpen, AlertTriangle, Terminal, CheckCircle2 } from 'lucide-react';

interface Message {
  id: string;
  sender: 'USER' | 'AGENT';
  content: string;
  citations?: Array<{ reference_tag: string; snippet: string; document_title: string }>;
  toolCalls?: Array<{ tool_name: string; status: string; approval_id?: string }>;
}

export const InvestigationWorkbench: React.FC = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'AGENT',
      content: 'ContextOS Investigation System initialized. State your incident inquiry or symptom to begin automated evidence-backed diagnosis.',
    },
  ]);
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isStreaming) return;

    const userText = query;
    setQuery('');
    const userMsg: Message = { id: Date.now().toString(), sender: 'USER', content: userText };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    // Simulated Agent SSE turn
    const agentMsgId = (Date.now() + 1).toString();
    const isRemediation = userText.toLowerCase().includes('reset') || userText.toLowerCase().includes('remediation');

    let initialContent = '';
    if (isRemediation) {
      initialContent = 'Analyzing system telemetry and customer account state...\nDetected rate limit overflow on Enterprise Account ACC-9941 [Doc:Database Runbook.md#Chunk:0].';
    } else {
      initialContent = 'Retrieved 3 knowledge evidence chunks. System CPU utilization spiked due to unindexed vector similarity queries on database primary pool [Doc:Database Runbook.md#Chunk:0]. Recommended action is to check connection pool size.';
    }

    setMessages((prev) => [
      ...prev,
      {
        id: agentMsgId,
        sender: 'AGENT',
        content: initialContent,
        citations: [
          { reference_tag: '[Doc:Database Runbook.md#Chunk:0]', document_title: 'Database Runbook.md', snippet: 'High CPU utilization on primary pool occurs when unindexed vectors are searched.' },
        ],
        toolCalls: isRemediation
          ? [{ tool_name: 'execute_account_remediation', status: 'PENDING_APPROVAL', approval_id: 'appr_8891' }]
          : undefined,
      },
    ]);

    setIsStreaming(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] glass-panel rounded-xl overflow-hidden border border-slate-800">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-100">Incident Investigation Workbench</h2>
            <p className="text-xs text-slate-400">Multi-Turn RAG Evidence Retrieval & MCP Tool Orchestration</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
            Agent Active
          </span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl rounded-xl p-5 ${msg.sender === 'USER' ? 'bg-cyan-600 text-white' : 'bg-slate-900/90 text-slate-200 border border-slate-800'}`}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  <div className="flex items-center space-x-1.5 text-xs text-cyan-400 font-medium mb-2">
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Resolvable Evidence Citations</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.citations.map((cite, i) => (
                      <span key={i} className="px-2 py-1 rounded text-xs bg-cyan-950/60 text-cyan-300 border border-cyan-800/50 font-mono">
                        {cite.reference_tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Tool Calls & Approval Gate Indicators */}
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  {msg.toolCalls.map((tc, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-amber-950/20 border border-amber-500/30 text-amber-300 text-xs">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />
                        <span>State-changing tool <strong>{tc.tool_name}</strong> intercepted by HITL Approval Gate</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-200 font-mono font-medium">
                        PENDING_APPROVAL #{tc.approval_id}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSend} className="p-4 border-t border-slate-800/80 bg-slate-900/40 flex items-center space-x-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask an operational query or command (e.g. 'Investigate DB CPU spike' or 'Reset rate limit for ACC-9941')..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 transition-colors"
        />
        <button
          type="submit"
          disabled={isStreaming || !query.trim()}
          className="px-5 py-3 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium transition-colors flex items-center space-x-2"
        >
          <span>Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
