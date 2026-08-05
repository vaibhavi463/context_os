import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle2, XCircle, Clock, Terminal } from 'lucide-react';

interface PendingApprovalItem {
  id: string;
  tool_name: string;
  tool_arguments: Record<string, any>;
  status: string;
  created_at: string;
  expires_at: string;
}

export const ApprovalQueue: React.FC = () => {
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([
    {
      id: 'appr_8891',
      tool_name: 'execute_account_remediation',
      tool_arguments: { account_id: 'ACC-9941', action_type: 'RESET_RATE_LIMIT' },
      status: 'PENDING',
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
    },
  ]);
  const [statusMsg, setStatusMsg] = useState('');

  const handleDecision = async (id: string, decision: 'APPROVE' | 'REJECT') => {
    try {
      await fetch(`/api/v1/approvals/${id}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision }),
      });
    } catch {}

    setApprovals((prev) => prev.filter((a) => a.id !== id));
    setStatusMsg(`Action #${id} successfully ${decision === 'APPROVE' ? 'APPROVED' : 'REJECTED'}. HMAC token dispatched.`);
  };

  return (
    <div className="glass-panel rounded-xl p-6 border border-slate-800 space-y-6">
      <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
        <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Human-in-the-Loop Approval Queue</h2>
          <p className="text-xs text-slate-400">Strict authorization gate intercepting state-changing write operations</p>
        </div>
      </div>

      {statusMsg && (
        <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{statusMsg}</span>
        </div>
      )}

      {approvals.length > 0 ? (
        <div className="space-y-4">
          {approvals.map((item) => (
            <div key={item.id} className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-amber-400 bg-amber-950/60 px-2.5 py-1 rounded border border-amber-800/50">
                  Approval ID: #{item.id}
                </span>
                <span className="text-xs text-slate-400 flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Expires in 14 minutes</span>
                </span>
              </div>

              <div className="text-sm space-y-2">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-4 h-4 text-cyan-400" />
                  <span className="font-semibold text-slate-200">Target Tool: {item.tool_name}</span>
                </div>
                <div className="text-xs text-slate-400">Requester Scope: ops:write | Multi-Tenant Isolated</div>
                <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs text-slate-300 font-mono overflow-x-auto">
                  {JSON.stringify(item.tool_arguments, null, 2)}
                </pre>
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => handleDecision(item.id, 'APPROVE')}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition-colors flex items-center space-x-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve & Execute</span>
                </button>
                <button
                  onClick={() => handleDecision(item.id, 'REJECT')}
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium transition-colors flex items-center space-x-1.5"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Action</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-8 text-center text-slate-500 text-sm">No pending approval requests requiring operator intervention.</div>
      )}
    </div>
  );
};
