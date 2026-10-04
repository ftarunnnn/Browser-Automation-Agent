import React, { useEffect, useRef } from 'react';
import { Terminal, CheckCircle, AlertCircle, Info, ShieldAlert } from 'lucide-react';

export const ActionLog = ({ logs }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const getLogIcon = (type) => {
    switch (type) {
      case 'action_verified':
      case 'task_finish':
        return <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />;
      case 'action_failed':
      case 'error':
        return <AlertCircle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />;
      case 'approval_required':
        return <ShieldAlert className="w-3.5 h-3.5 text-orange-400 shrink-0 mt-0.5" />;
      default:
        return <Info className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />;
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col h-full">
      <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center space-x-2">
        <Terminal className="w-4 h-4 text-emerald-400" />
        <h3 className="font-semibold text-xs text-slate-200 uppercase tracking-wider">Agent Activity Log</h3>
      </div>

      <div ref={scrollRef} className="p-4 space-y-2 overflow-y-auto max-h-[320px] font-mono text-xs">
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={index} className="flex items-start space-x-2 bg-slate-950/60 p-2 rounded border border-slate-800/50">
              {getLogIcon(log.event)}
              <div className="flex-1">
                <div className="flex items-center justify-between text-[10px] text-slate-500 mb-0.5">
                  <span className="font-semibold uppercase tracking-wider text-slate-400">{log.event}</span>
                  <span>{log.timestamp || new Date().toLocaleTimeString()}</span>
                </div>
                <p className="text-slate-300 whitespace-pre-wrap break-words">
                  {typeof log.data === 'string' ? log.data : JSON.stringify(log.data, null, 2)}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-slate-600">
            <p>No activity logs recorded yet</p>
          </div>
        )}
      </div>
    </div>
  );
};
