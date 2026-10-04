import React from 'react';
import { Activity, Globe, StopCircle, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Pending', color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30', icon: Clock },
  planning: { label: 'Planning', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30', icon: Activity },
  running: { label: 'Running', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 animate-pulse', icon: Activity },
  paused_approval: { label: 'Approval Required', color: 'bg-orange-500/10 text-orange-400 border-orange-500/30 animate-bounce', icon: AlertTriangle },
  completed: { label: 'Completed', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', icon: CheckCircle2 },
  failed: { label: 'Failed', color: 'bg-red-500/10 text-red-400 border-red-500/30', icon: AlertTriangle },
  stopped: { label: 'Stopped', color: 'bg-slate-500/10 text-slate-400 border-slate-500/30', icon: StopCircle }
};

export const AgentStatus = ({ task, onStop }) => {
  if (!task) return null;

  const statusInfo = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
  const Icon = statusInfo.icon;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-xl backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center space-x-4">
        <div className={`px-3 py-1.5 rounded-full border text-xs font-semibold flex items-center space-x-2 ${statusInfo.color}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{statusInfo.label}</span>
        </div>

        <div className="flex items-center space-x-2 text-xs text-slate-300">
          <Globe className="w-4 h-4 text-blue-400" />
          <span className="font-mono bg-slate-950 px-2.5 py-1 rounded border border-slate-800 max-w-xs truncate">
            {task.current_url || 'about:blank'}
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="text-xs text-slate-400">
          Steps: <span className="font-semibold text-slate-200">{task.steps ? task.steps.length : 0}</span>
        </div>

        {(task.status === 'running' || task.status === 'planning') && (
          <button
            onClick={onStop}
            className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all"
          >
            <StopCircle className="w-3.5 h-3.5" />
            <span>Stop Agent</span>
          </button>
        )}
      </div>
    </div>
  );
};
