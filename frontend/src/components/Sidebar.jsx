import React from 'react';
import { LayoutDashboard, PlusCircle, History, Activity, Settings as SettingsIcon, Bot } from 'lucide-react';

export const Sidebar = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'new-task', label: 'New Task', icon: PlusCircle },
    { id: 'history', label: 'Task History', icon: History },
    { id: 'activity', label: 'Agent Activity', icon: Activity },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="p-2 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl text-white shadow-lg shadow-blue-500/20">
          <Bot className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-slate-100 tracking-tight text-base">WebPilot AI</h1>
          <p className="text-[11px] text-slate-400 font-medium">Autonomous Agent</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-500 text-center">
        WebPilot AI v1.0 • Playwright Chromium
      </div>
    </aside>
  );
};
