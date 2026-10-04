import React from 'react';
import { Database, CheckCircle, FileText, Download } from 'lucide-react';

export const ResultPanel = ({ results }) => {
  if (!results || results.length === 0) return None;

  const resultObj = results[0]?.structured_data || {};

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2 text-emerald-400">
          <CheckCircle className="w-5 h-5" />
          <h3 className="font-semibold text-base text-slate-100">Structured Task Results</h3>
        </div>
        <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full font-medium">
          Task Complete
        </span>
      </div>

      <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs overflow-x-auto max-h-[250px] text-slate-200">
        <pre>{JSON.stringify(resultObj, null, 2)}</pre>
      </div>

      {results[0]?.extracted_text && (
        <div className="mt-4 pt-3 border-t border-slate-800/60">
          <div className="flex items-center space-x-2 mb-2 text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <FileText className="w-4 h-4 text-blue-400" />
            <span>Extracted Page Content Excerpt</span>
          </div>
          <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded border border-slate-800 line-clamp-4 font-sans leading-relaxed">
            {results[0].extracted_text}
          </p>
        </div>
      )}
    </div>
  );
};
