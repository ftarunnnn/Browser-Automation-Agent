import React from 'react';
import { ShieldAlert, Check, X, AlertTriangle } from 'lucide-react';

export const ApprovalDialog = ({ approval, onApprove, onReject }) => {
  if (!approval) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-orange-500/30 rounded-2xl max-w-md w-full p-6 shadow-2xl shadow-orange-500/10 animate-scale-in">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 bg-orange-500/10 rounded-xl text-orange-400 border border-orange-500/20">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-slate-100">Human Approval Required</h3>
            <p className="text-xs text-orange-400 font-medium">Sensitive Browser Action Guard</p>
          </div>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-6 space-y-3">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400">Action Type:</span>
            <span className="font-mono bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded font-semibold uppercase">
              {approval.action_type}
            </span>
          </div>

          <div>
            <span className="text-xs text-slate-400 block mb-1">Details:</span>
            <p className="text-sm text-slate-200 bg-slate-900 p-2.5 rounded border border-slate-800">
              {approval.description}
            </p>
          </div>

          {approval.parameters && Object.keys(approval.parameters).length > 0 && (
            <div>
              <span className="text-xs text-slate-400 block mb-1">Parameters:</span>
              <pre className="text-[11px] font-mono text-slate-300 bg-slate-900 p-2 rounded border border-slate-800 overflow-x-auto">
                {JSON.stringify(approval.parameters, null, 2)}
              </pre>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end space-x-3">
          <button
            onClick={() => onReject(approval.approval_id || approval.id)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition-all"
          >
            <X className="w-4 h-4 text-red-400" />
            <span>Reject Action</span>
          </button>

          <button
            onClick={() => onApprove(approval.approval_id || approval.id)}
            className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium flex items-center space-x-1.5 shadow-lg shadow-emerald-500/20 transition-all"
          >
            <Check className="w-4 h-4" />
            <span>Approve & Continue</span>
          </button>
        </div>
      </div>
    </div>
  );
};
