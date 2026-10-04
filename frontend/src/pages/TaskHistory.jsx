import React, { useState, useEffect } from 'react';
import { History, ExternalLink, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export const TaskHistory = ({ onSelectTask }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await api.getTask('all_history_or_list');
      setTasks(data);
    } catch (err) {
      console.error('Fetch history error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 text-slate-100">
        <History className="w-6 h-6 text-blue-400" />
        <h2 className="text-xl font-bold">Execution Task History</h2>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Task ID</th>
                <th className="p-4">Instruction</th>
                <th className="p-4">Status</th>
                <th className="p-4">Created Date</th>
                <th className="p-4">Actions</th>
                <th className="p-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {tasks && tasks.length > 0 ? (
                tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-slate-800/40 transition-all">
                    <td className="p-4 font-semibold text-blue-400">{task.id}</td>
                    <td className="p-4 font-sans max-w-md truncate text-slate-200">{task.instruction}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold border ${
                        task.status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : task.status === 'failed'
                          ? 'bg-red-500/10 text-red-400 border-red-500/30'
                          : 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                      }`}>
                        {task.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{new Date(task.created_at).toLocaleString()}</td>
                    <td className="p-4 text-slate-400">{task.actions ? task.actions.length : 0}</td>
                    <td className="p-4">
                      <button
                        onClick={() => onSelectTask(task)}
                        className="text-blue-400 hover:text-blue-300 flex items-center space-x-1 font-sans text-xs"
                      >
                        <span>View</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="p-8 text-center text-slate-500 font-sans">
                    {loading ? 'Loading history...' : 'No previous agent tasks found'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
