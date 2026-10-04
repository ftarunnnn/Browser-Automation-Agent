import React, { useState } from 'react';
import { Play, Sparkles, Compass } from 'lucide-react';

const PRESET_TASKS = [
  "Search for Python courses and collect the top 5 results",
  "Open a website, log in, and navigate to my dashboard",
  "Search for a product and compare its price across websites",
  "Fill a form using the information I provide",
  "Find a specific document on a website and download it"
];

export const TaskInput = ({ onSubmit, isLoading }) => {
  const [instruction, setInstruction] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!instruction.trim() || isLoading) return;
    onSubmit(instruction.trim());
  };

  const handleChipClick = (preset) => {
    setInstruction(preset);
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center space-x-2 mb-4 text-blue-400">
        <Sparkles className="w-5 h-5" />
        <h2 className="font-semibold text-lg text-slate-100">Enter Browser Task</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="e.g. 'Search for top 5 Python courses on Google and extract course titles'"
            className="w-full h-24 px-4 py-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-none font-sans text-sm"
            disabled={isLoading}
          />
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <Compass className="w-4 h-4 text-slate-500" />
            <span>Natural Language Autonomous Execution</span>
          </div>

          <button
            type="submit"
            disabled={!instruction.trim() || isLoading}
            className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-medium rounded-lg flex items-center space-x-2 shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{isLoading ? 'Planning Task...' : 'Run Autonomous Agent'}</span>
          </button>
        </div>
      </form>

      <div className="mt-4 pt-4 border-t border-slate-800/60">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Sample Test Tasks:</span>
        <div className="flex flex-wrap gap-2">
          {PRESET_TASKS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleChipClick(preset)}
              className="text-xs bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-blue-300 px-3 py-1.5 rounded-full border border-slate-700/50 transition-all text-left"
            >
              {preset}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
