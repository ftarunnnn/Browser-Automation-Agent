import React, { useState } from 'react';
import { Settings as SettingsIcon, Sliders, Cpu, Shield, Save } from 'lucide-react';

export const Settings = () => {
  const [provider, setProvider] = useState('gemini');
  const [headless, setHeadless] = useState(true);
  const [maxSteps, setMaxSteps] = useState(20);
  const [maxRetries, setMaxRetries] = useState(3);
  const [savedMsg, setSavedMsg] = useState('');

  const handleSave = (e) => {
    e.preventDefault();
    setSavedMsg('Settings saved successfully!');
    setTimeout(() => setSavedMsg(''), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center space-x-3 text-slate-100">
        <SettingsIcon className="w-6 h-6 text-blue-400" />
        <h2 className="text-xl font-bold">Agent Configuration & Settings</h2>
      </div>

      <form onSubmit={handleSave} className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
        {/* LLM Provider Selection */}
        <div>
          <label className="flex items-center space-x-2 text-sm font-semibold text-slate-200 mb-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>LLM Reasoning Provider</span>
          </label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full max-w-md bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:ring-2 focus:ring-blue-500/50"
          >
            <option value="gemini">Google Gemini 2.5 Flash</option>
            <option value="openai">OpenAI GPT-4o-mini</option>
            <option value="local">Local Rule Engine / Fallback</option>
          </select>
        </div>

        {/* Execution Constraints */}
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <label className="flex items-center space-x-2 text-sm font-semibold text-slate-200">
            <Sliders className="w-4 h-4 text-emerald-400" />
            <span>Execution Constraints</span>
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-slate-400 block mb-1">Max Task Steps</span>
              <input
                type="number"
                value={maxSteps}
                onChange={(e) => setMaxSteps(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200"
              />
            </div>

            <div>
              <span className="text-xs text-slate-400 block mb-1">Max Retry Attempts</span>
              <input
                type="number"
                value={maxRetries}
                onChange={(e) => setMaxRetries(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200"
              />
            </div>
          </div>
        </div>

        {/* Headless Mode Toggle */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-sm font-semibold text-slate-200 block">Headless Browser Mode</span>
            <span className="text-xs text-slate-400">Run Playwright browser silently in background</span>
          </div>
          <button
            type="button"
            onClick={() => setHeadless(!headless)}
            className={`w-12 h-6 rounded-full p-1 transition-colors ${headless ? 'bg-blue-600' : 'bg-slate-800'}`}
          >
            <div className={`w-4 h-4 rounded-full bg-white transition-transform ${headless ? 'translate-x-6' : 'translate-x-0'}`} />
          </button>
        </div>

        {/* Submit */}
        <div className="pt-4 border-t border-slate-800 flex items-center space-x-4">
          <button
            type="submit"
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg flex items-center space-x-2 shadow-lg shadow-blue-500/20"
          >
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
          {savedMsg && <span className="text-xs text-emerald-400 font-medium">{savedMsg}</span>}
        </div>
      </form>
    </div>
  );
};
