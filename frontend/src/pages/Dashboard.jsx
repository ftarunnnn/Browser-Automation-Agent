import React, { useState, useEffect } from 'react';
import { Bot, Sparkles, Server } from 'lucide-react';
import { TaskInput } from '../components/TaskInput';
import { AgentStatus } from '../components/AgentStatus';
import { BrowserPreview } from '../components/BrowserPreview';
import { ActionLog } from '../components/ActionLog';
import { ResultPanel } from '../components/ResultPanel';
import { ApprovalDialog } from '../components/ApprovalDialog';
import { api } from '../services/api';
import { TaskWebSocket } from '../services/websocket';

export const Dashboard = () => {
  const [currentTask, setCurrentTask] = useState(null);
  const [taskLogs, setTaskLogs] = useState([]);
  const [pendingApproval, setPendingApproval] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [latestScreenshot, setLatestScreenshot] = useState('');
  const [taskResults, setTaskResults] = useState([]);

  useEffect(() => {
    let ws = null;

    if (currentTask && currentTask.id) {
      ws = new TaskWebSocket(
        currentTask.id,
        (eventData) => {
          const { event, data } = eventData;

          // Add to log list
          setTaskLogs((prev) => [...prev, { event, data, timestamp: new Date().toLocaleTimeString() }]);

          if (event === 'status_change') {
            setCurrentTask((prev) => ({ ...prev, status: data.status }));
            if (data.status === 'completed' || data.status === 'failed' || data.status === 'stopped') {
              setIsLoading(false);
              fetchTaskDetails(currentTask.id);
            }
          } else if (event === 'page_observation') {
            setCurrentTask((prev) => ({ ...prev, current_url: data.url }));
          } else if (event === 'action_verified') {
            if (data.screenshot) setLatestScreenshot(data.screenshot);
          } else if (event === 'approval_required') {
            setPendingApproval(data);
          } else if (event === 'approval_response') {
            setPendingApproval(null);
          } else if (event === 'task_finish') {
            setTaskResults([{ structured_data: data.extracted_data }]);
          }
        },
        (err) => console.error('WS Error:', err)
      );
      ws.connect();
    }

    return () => {
      if (ws) ws.disconnect();
    };
  }, [currentTask?.id]);

  const fetchTaskDetails = async (taskId) => {
    try {
      const data = await api.getTask(taskId);
      setCurrentTask(data);
      if (data.results) setTaskResults(data.results);
      if (data.screenshots && data.screenshots.length > 0) {
        setLatestScreenshot(data.screenshots[data.screenshots.length - 1].filepath);
      }
    } catch (err) {
      console.error('Fetch task error:', err);
    }
  };

  const handleTaskSubmit = async (instruction) => {
    setIsLoading(true);
    setTaskLogs([]);
    setPendingApproval(null);
    setTaskResults([]);
    setLatestScreenshot('');

    try {
      const newTask = await api.createTask(instruction);
      setCurrentTask(newTask);
      setTaskLogs([{ event: 'status_change', data: { status: 'planning', message: 'Task submitted' } }]);
    } catch (err) {
      console.error('Task submission error:', err);
      setIsLoading(false);
    }
  };

  const handleStopTask = async () => {
    if (!currentTask) return;
    try {
      await api.stopTask(currentTask.id);
      setIsLoading(false);
    } catch (err) {
      console.error('Stop task error:', err);
    }
  };

  const handleApprove = async (approvalId) => {
    if (!currentTask) return;
    try {
      await api.approveAction(currentTask.id, approvalId);
      setPendingApproval(null);
    } catch (err) {
      console.error('Approve error:', err);
    }
  };

  const handleReject = async (approvalId) => {
    if (!currentTask) return;
    try {
      await api.rejectAction(currentTask.id, approvalId);
      setPendingApproval(null);
    } catch (err) {
      console.error('Reject error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navbar Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl shadow-lg shadow-blue-500/20 text-white">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-100 tracking-tight">AI Browser Automation Agent</h1>
            <p className="text-xs text-slate-400">Autonomous Playwright Navigation & Natural Language Execution</p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-400">
          <Server className="w-4 h-4 text-emerald-400" />
          <span>Backend Online</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <TaskInput onSubmit={handleTaskSubmit} isLoading={isLoading} />

        {currentTask && (
          <AgentStatus task={currentTask} onStop={handleStopTask} />
        )}

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Live Browser View & Results */}
          <div className="lg:col-span-7 space-y-6">
            <BrowserPreview
              currentUrl={currentTask?.current_url || ''}
              screenshotPath={latestScreenshot}
            />

            {taskResults && taskResults.length > 0 && (
              <ResultPanel results={taskResults} />
            )}
          </div>

          {/* Right Column: Execution Log & Steps */}
          <div className="lg:col-span-5 flex flex-col space-y-6">
            <ActionLog logs={taskLogs} />
          </div>
        </div>
      </main>

      {/* Approval Dialog Modal */}
      {pendingApproval && (
        <ApprovalDialog
          approval={pendingApproval}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      )}
    </div>
  );
};
