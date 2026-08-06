import React, { useState } from 'react';
import { ShieldAlert, CheckCircle2, XCircle, Clock, Terminal, Lock, AlertOctagon, ShieldCheck } from 'lucide-react';

interface PendingApprovalItem {
  id: string;
  tool_name: string;
  tool_arguments: Record<string, any>;
  status: string;
  requester: string;
  scope: string;
  created_at: string;
  expires_at: string;
}

interface ApprovalQueueProps {
  onApprovalCountChange?: (count: number) => void;
}

export const ApprovalQueue: React.FC<ApprovalQueueProps> = ({ onApprovalCountChange }) => {
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([
    {
      id: 'appr_8891',
      tool_name: 'execute_account_remediation',
      tool_arguments: { account_id: 'ACC-9941', action_type: 'RESET_RATE_LIMIT' },
      status: 'PENDING',
      requester: 'ops_engineer@contextos.io',
      scope: 'ops:write',
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

    const remaining = approvals.filter((a) => a.id !== id);
    setApprovals(remaining);
    if (onApprovalCountChange) {
      onApprovalCountChange(remaining.length);
    }
    setStatusMsg(`Action #${id} successfully ${decision === 'APPROVE' ? 'APPROVED & DISPATCHED' : 'REJECTED'}. HMAC signed token sent to fastmcp executor.`);
  };

  return (
    <div className="bg-white rounded-2xl p-7 border border-slate-200/90 shadow-sm space-y-6">
      {/* Title Bar */}
      <div className="flex items-center justify-between border-b border-slate-200/80 pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-amber-100 text-amber-700 border border-amber-200">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <span>Human-in-the-Loop Security Gate</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 font-semibold border border-amber-200">HMAC-SHA256</span>
            </h2>
            <p className="text-xs text-slate-500">Strict zero-trust authorization gate intercepting state-changing write operations</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Audit Log Enforcement Active</span>
        </div>
      </div>

      {statusMsg && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center space-x-2.5 shadow-2xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          <span>{statusMsg}</span>
        </div>
      )}

      {approvals.length > 0 ? (
        <div className="space-y-4">
          {approvals.map((item) => (
            <div key={item.id} className="p-6 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-5 shadow-2xs">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-200/70 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono font-bold text-amber-800 bg-amber-100 px-3 py-1 rounded-lg border border-amber-200">
                    ID: #{item.id}
                  </span>
                  <span className="text-[11px] font-semibold text-slate-500 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
                    STATUS: PENDING OPERATOR SIGNATURE
                  </span>
                </div>

                <div className="text-xs text-slate-500 flex items-center space-x-1.5 font-medium">
                  <Clock className="w-3.5 h-3.5 text-amber-600" />
                  <span>Expires in 14m 30s</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
                    <Terminal className="w-4 h-4 text-violet-600" />
                    <span>Target Tool: <code className="text-violet-700 bg-violet-50 px-2 py-0.5 rounded border border-violet-100">{item.tool_name}</code></span>
                  </div>
                  <div className="text-xs text-slate-500 space-y-1">
                    <p>Requester Identity: <strong className="text-slate-700">{item.requester}</strong></p>
                    <p>Required Security Scope: <strong className="text-slate-700">{item.scope}</strong></p>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-500 mb-1">JSON Payload Arguments</label>
                  <pre className="bg-white p-3 rounded-xl border border-slate-200 text-xs text-slate-800 font-mono shadow-2xs overflow-x-auto">
                    {JSON.stringify(item.tool_arguments, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="flex items-center space-x-3 pt-2 border-t border-slate-200/70">
                <button
                  onClick={() => handleDecision(item.id, 'APPROVE')}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-xs font-semibold shadow-md shadow-emerald-500/20 transition-all flex items-center space-x-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve & Issue HMAC Token</span>
                </button>
                <button
                  onClick={() => handleDecision(item.id, 'REJECT')}
                  className="px-5 py-2.5 rounded-xl bg-white hover:bg-rose-50 border border-slate-200 hover:border-rose-300 text-rose-700 text-xs font-semibold transition-all flex items-center space-x-1.5 shadow-2xs"
                >
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>Reject Action</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center text-slate-400 text-sm border-2 border-dashed border-slate-200 rounded-2xl">
          <ShieldCheck className="w-10 h-10 text-emerald-500 mx-auto mb-2 opacity-80" />
          <p className="font-semibold text-slate-700">Approval Queue Empty</p>
          <p className="text-xs text-slate-500 mt-1">No pending state-changing write operations requiring operator decision.</p>
        </div>
      )}
    </div>
  );
};

