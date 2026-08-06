import React, { useState } from 'react';
import { Send, BookOpen, AlertTriangle, Terminal, Bot, User, Sparkles, CheckCircle2, RefreshCw, Zap } from 'lucide-react';

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
      content: 'ContextOS AI Operations Agent ready. I can investigate live service degradations, run vector RAG queries over your runbooks, and dispatch authorized MCP tool actions.',
    },
  ]);
  const [isStreaming, setIsStreaming] = useState(false);

  const samplePrompts = [
    'Investigate DB CPU spike',
    'Reset rate limit for ACC-9941',
    'Check Redis connection pool exhaustion',
  ];

  const handleSend = async (customPrompt?: string) => {
    const textToSend = customPrompt || query;
    if (!textToSend.trim() || isStreaming) return;

    setQuery('');
    const userMsg: Message = { id: Date.now().toString(), sender: 'USER', content: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    // Simulated turn
    setTimeout(() => {
      const agentMsgId = (Date.now() + 1).toString();
      const isRemediation = textToSend.toLowerCase().includes('reset') || textToSend.toLowerCase().includes('remediation');

      let responseText = '';
      if (isRemediation) {
        responseText = 'Intercepted write operation request. Verified operational scope: ops:write. Analyzing enterprise tenant ACC-9941 rate limiter keys in Redis cluster...\nRate limit quota overflow detected [Doc:Database Runbook.md#Chunk:0]. Intercepted by Human-in-the-Loop Approval Gate.';
      } else {
        responseText = 'Retrieved 3 knowledge evidence chunks via postgres pgvector HNSW similarity search. High CPU utilization on primary pool detected due to unindexed vector search query spikes [Doc:Database Runbook.md#Chunk:0].\n\nRecommended Action: Scale primary pool connection limits or execute `reindex_vector_tables` tool.';
      }

      setMessages((prev) => [
        ...prev,
        {
          id: agentMsgId,
          sender: 'AGENT',
          content: responseText,
          citations: [
            { reference_tag: '[Doc:Database Runbook.md#Chunk:0]', document_title: 'Database Runbook.md', snippet: 'High CPU utilization on primary pool occurs when unindexed vectors are searched.' },
          ],
          toolCalls: isRemediation
            ? [{ tool_name: 'execute_account_remediation', status: 'PENDING_APPROVAL', approval_id: 'appr_8891' }]
            : undefined,
        },
      ]);
      setIsStreaming(false);
    }, 400);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-11rem)] bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200/80 bg-slate-50/80 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-violet-100 text-violet-700 border border-violet-200">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <span>Incident Investigation Workbench</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 font-semibold border border-violet-200">RAG + MCP</span>
            </h2>
            <p className="text-xs text-slate-500">Autonomous RAG Evidence Retrieval & MCP Approval Pipeline</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
            Agent Engine Ready
          </span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'USER' ? 'justify-end' : 'justify-start'}`}>
            {msg.sender === 'AGENT' && (
              <div className="mr-3 mt-1 flex-shrink-0">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white flex items-center justify-center shadow-xs">
                  <Bot className="w-5 h-5" />
                </div>
              </div>
            )}

            <div className={`max-w-3xl rounded-2xl p-5 ${
              msg.sender === 'USER'
                ? 'bg-slate-900 text-white shadow-sm rounded-tr-xs'
                : 'bg-white text-slate-800 border border-slate-200/90 shadow-xs rounded-tl-xs'
            }`}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

              {/* Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-slate-200/80">
                  <div className="flex items-center space-x-1.5 text-xs text-violet-700 font-bold mb-2">
                    <BookOpen className="w-3.5 h-3.5 text-violet-600" />
                    <span>Resolvable Runbook Evidence</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.citations.map((cite, i) => (
                      <div key={i} className="px-3 py-1.5 rounded-lg bg-violet-50 text-violet-800 border border-violet-200/80 font-mono text-xs font-medium hover:bg-violet-100 transition-colors cursor-pointer flex items-center space-x-1">
                        <span>{cite.reference_tag}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tool Calls & Approval Gate Indicators */}
              {msg.toolCalls && msg.toolCalls.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200/80">
                  {msg.toolCalls.map((tc, i) => (
                    <div key={i} className="p-3.5 rounded-xl bg-amber-50 border border-amber-200/80 text-amber-900 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-2xs">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-amber-600 animate-bounce flex-shrink-0" />
                        <span>State action <strong>{tc.tool_name}</strong> intercepted by HMAC Approval Gate</span>
                      </div>
                      <span className="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 border border-amber-300 font-mono font-bold text-[11px] shadow-2xs">
                        PENDING_APPROVAL #{tc.approval_id}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {msg.sender === 'USER' && (
              <div className="ml-3 mt-1 flex-shrink-0">
                <div className="w-9 h-9 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs">
                  <User className="w-5 h-5 text-slate-600" />
                </div>
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center space-x-3 text-xs text-violet-600 font-semibold bg-violet-50 p-3 rounded-xl border border-violet-100 w-fit">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Agent retrieving RAG context & running tool guard checks...</span>
          </div>
        )}
      </div>

      {/* Suggested Quick Prompts */}
      <div className="px-6 py-2 bg-slate-100/60 border-t border-slate-200/60 flex items-center space-x-2 overflow-x-auto">
        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1 flex-shrink-0">
          <Zap className="w-3 h-3 text-amber-500" />
          <span>Quick Prompts:</span>
        </span>
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="px-3 py-1 rounded-lg bg-white border border-slate-200 text-slate-700 text-xs font-medium hover:border-violet-300 hover:text-violet-700 transition-all flex-shrink-0 shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-4 border-t border-slate-200/80 bg-white flex items-center space-x-3"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask an operational inquiry or issue command (e.g. 'Investigate DB CPU spike' or 'Reset rate limit for ACC-9941')..."
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition-all"
        />
        <button
          type="submit"
          disabled={isStreaming || !query.trim()}
          className="px-5 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 disabled:opacity-50 text-white text-sm font-semibold shadow-md shadow-violet-500/20 transition-all flex items-center space-x-2"
        >
          <span>Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};

