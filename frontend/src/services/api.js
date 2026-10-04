import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  createTask: async (instruction) => {
    const res = await axios.post(`${API_BASE}/tasks`, { instruction });
    return res.data;
  },

  getTask: async (taskId) => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}`);
    return res.data;
  },

  stopTask: async (taskId) => {
    const res = await axios.post(`${API_BASE}/tasks/${taskId}/stop`);
    return res.data;
  },

  approveAction: async (taskId, approvalId) => {
    const res = await axios.post(`${API_BASE}/tasks/${taskId}/approve?approval_id=${approvalId}`);
    return res.data;
  },

  rejectAction: async (taskId, approvalId) => {
    const res = await axios.post(`${API_BASE}/tasks/${taskId}/reject?approval_id=${approvalId}`);
    return res.data;
  },

  getLogs: async (taskId) => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/logs`);
    return res.data;
  },

  getResults: async (taskId) => {
    const res = await axios.get(`${API_BASE}/tasks/${taskId}/results`);
    return res.data;
  }
};
