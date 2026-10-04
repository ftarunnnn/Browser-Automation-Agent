import React from 'react';
import { Monitor, RefreshCw, Lock } from 'lucide-react';

export const BrowserPreview = ({ currentUrl, screenshotPath }) => {
  const imageUrl = screenshotPath
    ? `http://localhost:8000/api/screenshots/${screenshotPath.split(/[/\\]/).pop()}`
    : null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col h-full">
      {/* Browser Chrome Header Bar */}
      <div className="bg-slate-950 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>
          <div className="h-4 w-px bg-slate-800 mx-2" />
          <div className="flex items-center space-x-1 text-xs text-slate-400">
            <Monitor className="w-3.5 h-3.5 text-blue-400" />
            <span className="font-medium text-slate-300">Live Browser View</span>
          </div>
        </div>

        {/* URL Bar */}
        <div className="flex-1 max-w-lg mx-4">
          <div className="bg-slate-900 border border-slate-800 rounded-md px-3 py-1 flex items-center space-x-2 text-xs text-slate-400">
            <Lock className="w-3 h-3 text-emerald-400" />
            <span className="truncate font-mono text-slate-200">{currentUrl || 'about:blank'}</span>
          </div>
        </div>

        <RefreshCw className="w-3.5 h-3.5 text-slate-500 animate-spin-slow" />
      </div>

      {/* Screen Viewport Container */}
      <div className="relative flex-1 bg-slate-950 min-h-[360px] flex items-center justify-center p-2 overflow-hidden">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Live Browser Page"
            className="max-h-full max-w-full object-contain rounded border border-slate-800 shadow-md transition-all duration-300"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-8 text-slate-600">
            <Monitor className="w-12 h-12 mb-3 stroke-[1.5]" />
            <p className="text-sm font-medium text-slate-400">Browser Viewport Standing By</p>
            <p className="text-xs text-slate-600 mt-1">Start a task to see real-time Playwright screen capture</p>
          </div>
        )}
      </div>
    </div>
  );
};
