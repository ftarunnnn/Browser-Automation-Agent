import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { TaskHistory } from './pages/TaskHistory';
import { Settings } from './pages/Settings';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedTask, setSelectedTask] = useState(null);

  const handleSelectHistoryTask = (task) => {
    setSelectedTask(task);
    setActiveTab('dashboard');
  };

  return (
    <div className="flex min-h-screen bg-slate-950 font-sans text-slate-100">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex-1 overflow-y-auto p-8">
        {activeTab === 'dashboard' || activeTab === 'new-task' ? (
          <Dashboard initialTask={selectedTask} />
        ) : activeTab === 'history' || activeTab === 'activity' ? (
          <TaskHistory onSelectTask={handleSelectHistoryTask} />
        ) : activeTab === 'settings' ? (
          <Settings />
        ) : (
          <Dashboard />
        )}
      </div>
    </div>
  );
}

export default App;
