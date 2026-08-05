import React, { useState } from 'react';
import { Terminal, Database, ShieldAlert, BarChart3, Lock, Cpu } from 'lucide-react';
import { InvestigationWorkbench } from './components/InvestigationWorkbench';
import { KnowledgeIngestion } from './components/KnowledgeIngestion';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workbench' | 'ingestion' | 'approvals' | 'admin'>('workbench');
  const [approvalDecided, setApprovalDecided] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur px-8 py-3.5 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center space-x-2">
              <span>ContextOS</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono font-medium">v1.0.0</span>
            </h1>
            <p className="text-xs text-slate-400">Production AI Operations Agent Platform</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex items-center space-x-1 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800/80">
          <button
            onClick={() => setActiveTab('workbench')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all flex items-center space-x-2 ${
              activeTab === 'workbench' ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-600/20' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-4 h-4" />
            <span>Investigation Workbench</span>
          </button>

          <button
            onClick={() => setActiveTab('ingestion')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all flex items-center space-x-2 ${
              activeTab === 'ingestion' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Knowledge Ingestion</span>
          </button>

          <button
            onClick={() => setActiveTab('approvals')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all flex items-center space-x-2 ${
              activeTab === 'approvals' ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/20' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            <span>HITL Approvals</span>
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-amber-500/30 text-amber-200 text-[10px]">1</span>
          </button>

          <button
            onClick={() => setActiveTab('admin')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all flex items-center space-x-2 ${
              activeTab === 'admin' ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Admin & Telemetry</span>
          </button>
        </nav>
      </header>

      {/* Main Body */}
      <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
        {activeTab === 'workbench' && <InvestigationWorkbench />}

        {activeTab === 'ingestion' && <KnowledgeIngestion />}

        {activeTab === 'approvals' && (
          <div className="glass-panel rounded-xl p-6 border border-slate-800 space-y-6">
            <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-100">Human-in-the-Loop Approval Queue</h2>
                <p className="text-xs text-slate-400">Explicit security gate for state-changing write operations</p>
              </div>
            </div>

            {approvalDecided && (
              <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-sm">
                Action decided: {approvalDecided}. Signed approval token dispatched to MCP executor.
              </div>
            )}

            {!approvalDecided ? (
              <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded border border-amber-800/50">
                    ID: #appr_8891 (PENDING)
                  </span>
                  <span className="text-xs text-slate-400">Expires in 12m 45s</span>
                </div>
                <div className="text-sm space-y-1">
                  <p className="font-semibold text-slate-200">Tool: execute_account_remediation</p>
                  <p className="text-slate-400 text-xs">Requester: ops_engineer@contextos.io | Scope: ops:write</p>
                  <p className="text-slate-300 font-mono text-xs mt-2 bg-slate-950 p-3 rounded border border-slate-850">
                    Arguments: &#123; "account_id": "ACC-9941", "action_type": "RESET_RATE_LIMIT" &#125;
                  </p>
                </div>
                <div className="flex space-x-3 pt-2">
                  <button
                    onClick={() => setApprovalDecided('APPROVED')}
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors"
                  >
                    Approve Action
                  </button>
                  <button
                    onClick={() => setApprovalDecided('REJECTED')}
                    className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium transition-colors"
                  >
                    Reject Action
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-slate-400 text-sm italic">No pending approval requests in queue.</p>
            )}
          </div>
        )}

        {activeTab === 'admin' && (
          <div className="glass-panel rounded-xl p-6 border border-slate-800 space-y-6">
            <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-100">Telemetry & Performance Dashboard</h2>
                <p className="text-xs text-slate-400">Real-time metrics, p95 latency breakdown, and token cost metrics</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <p className="text-xs text-slate-400">p95 Non-LLM Latency</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1">42.5 ms</p>
                <p className="text-[10px] text-emerald-500 mt-1">Target SLO: &lt;300 ms</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <p className="text-xs text-slate-400">p95 Vector Retrieval</p>
                <p className="text-2xl font-bold text-cyan-400 mt-1">68.0 ms</p>
                <p className="text-[10px] text-cyan-500 mt-1">pgvector HNSW</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <p className="text-xs text-slate-400">Retrieval Recall@K</p>
                <p className="text-2xl font-bold text-indigo-400 mt-1">88.0 %</p>
                <p className="text-[10px] text-indigo-500 mt-1">Benchmark Dataset</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                <p className="text-xs text-slate-400">LLM Token Cost</p>
                <p className="text-2xl font-bold text-amber-400 mt-1">$0.0452</p>
                <p className="text-[10px] text-amber-500 mt-1">Gemini 2.5 Flash</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
