import React, { useState } from 'react';
import { Terminal, Database, ShieldAlert, BarChart3, Cpu, Sparkles, CheckCircle2, Search, ExternalLink, User } from 'lucide-react';
import { InvestigationWorkbench } from './components/InvestigationWorkbench';
import { KnowledgeIngestion } from './components/KnowledgeIngestion';
import { ApprovalQueue } from './components/ApprovalQueue';
import { AdminDashboard } from './components/AdminDashboard';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workbench' | 'ingestion' | 'approvals' | 'admin'>('workbench');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(1);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Banner / Status Alert */}
      <div className="bg-gradient-to-r from-violet-600 via-indigo-600 to-blue-600 text-white text-xs py-1.5 px-4 font-medium flex items-center justify-between shadow-xs">
        <div className="flex items-center space-x-2 mx-auto sm:mx-0">
          <Sparkles className="w-3.5 h-3.5 text-violet-200 animate-pulse" />
          <span>ContextOS v1.0.0 Production Mode Active — Multi-tenant Vector & MCP Tool Engine Ready</span>
        </div>
        <div className="hidden sm:flex items-center space-x-4 text-[11px] text-violet-100">
          <span className="flex items-center space-x-1"><CheckCircle2 className="w-3 h-3 text-emerald-300" /> <span>pgvector HNSW</span></span>
          <span className="flex items-center space-x-1"><CheckCircle2 className="w-3 h-3 text-emerald-300" /> <span>HMAC Gate Active</span></span>
        </div>
      </div>

      {/* Main Navbar */}
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur-md px-6 py-3.5 flex items-center justify-between sticky top-0 z-50 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-500/20 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold tracking-tight text-slate-900">ContextOS</h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-violet-50 text-violet-700 border border-violet-200 font-mono font-semibold">
                ENTERPRISE
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Production AI Operations Agent Workbench</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <nav className="flex items-center space-x-1 bg-slate-100/90 p-1.5 rounded-2xl border border-slate-200/80 shadow-inner">
          <button
            onClick={() => setActiveTab('workbench')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              activeTab === 'workbench'
                ? 'bg-white text-violet-700 shadow-sm border border-slate-200/80 scale-[1.01]'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <Terminal className="w-4 h-4 text-violet-600" />
            <span>Investigation Workbench</span>
          </button>

          <button
            onClick={() => setActiveTab('ingestion')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              activeTab === 'ingestion'
                ? 'bg-white text-indigo-700 shadow-sm border border-slate-200/80 scale-[1.01]'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <Database className="w-4 h-4 text-indigo-600" />
            <span>Knowledge Ingestion</span>
          </button>

          <button
            onClick={() => setActiveTab('approvals')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 relative ${
              activeTab === 'approvals'
                ? 'bg-white text-amber-700 shadow-sm border border-slate-200/80 scale-[1.01]'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>HITL Approvals</span>
            {pendingApprovalsCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-amber-500 text-white text-[10px] font-bold shadow-xs">
                {pendingApprovalsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('admin')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              activeTab === 'admin'
                ? 'bg-white text-emerald-700 shadow-sm border border-slate-200/80 scale-[1.01]'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <BarChart3 className="w-4 h-4 text-emerald-600" />
            <span>Telemetry & SLOs</span>
          </button>
        </nav>

        {/* Right Info Badge & User profile */}
        <div className="hidden lg:flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span>Tenant: <strong>acme-prod-01</strong></span>
          </div>
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-violet-500 to-indigo-500 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            OP
          </div>
        </div>
      </header>

      {/* Main Body View */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto space-y-6">
        {activeTab === 'workbench' && <InvestigationWorkbench />}

        {activeTab === 'ingestion' && <KnowledgeIngestion />}

        {activeTab === 'approvals' && (
          <ApprovalQueue onApprovalCountChange={(count) => setPendingApprovalsCount(count)} />
        )}

        {activeTab === 'admin' && <AdminDashboard />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 px-8 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2 mt-auto">
        <div className="flex items-center space-x-4">
          <span className="font-semibold text-slate-700">ContextOS Operations Suite</span>
          <span>•</span>
          <span>FastAPI 0.111</span>
          <span>•</span>
          <span>pgvector 0.7</span>
          <span>•</span>
          <span>Gemini 2.5 Flash</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-emerald-600 font-medium flex items-center space-x-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            <span>RLS Security Policy Enforced</span>
          </span>
        </div>
      </footer>
    </div>
  );
};

export default App;


