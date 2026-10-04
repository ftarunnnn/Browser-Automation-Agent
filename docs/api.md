# WebPilot AI — API Documentation

Complete REST API and WebSocket specification for WebPilot AI backend.

---

## 1. REST Endpoints

### `POST /api/tasks`
Creates and launches a new autonomous browser automation task.
- **Request Body**:
  ```json
  {
    "instruction": "Search for top 5 Python courses and return their names and URLs"
  }
  ```
- **Response**: `TaskResponse` schema containing generated `id`, `status`, `created_at`.

### `GET /api/tasks`
Lists all recent tasks with pagination limit parameter (`?limit=20`).

### `GET /api/tasks/{task_id}`
Retrieves detailed status, plan steps, action logs, screenshots, and extracted results for a specific task.

### `POST /api/tasks/{task_id}/stop`
Stops an actively running agent task and updates status to `STOPPED`.

### `POST /api/tasks/{task_id}/approve`
Approves a pending sensitive browser action request (`?approval_id=123`).

### `POST /api/tasks/{task_id}/reject`
Rejects a pending sensitive browser action request (`?approval_id=123`).

### `GET /api/tasks/{task_id}/logs`
Returns chronologically sorted list of browser tool executions for the task.

### `GET /api/tasks/{task_id}/results`
Returns structured JSON results extracted upon task completion.

### `GET /api/health`
Health check endpoint returning system status, version, and active LLM provider.

---

## 2. Real-Time WebSockets

### `WS /api/tasks/{task_id}/stream`
Streams live execution events to the frontend dashboard.
- **Event Types**:
  - `status_change`: Task status update (`IDLE`, `PLANNING`, `RUNNING`, `WAITING_FOR_APPROVAL`, `COMPLETED`, `FAILED`, `STOPPED`).
  - `page_observation`: Current page URL, title, element count, headings.
  - `action_start`: Starting tool execution (`action_name`, `params`).
  - `action_verified`: Tool execution verified with screenshot path.
  - `action_failed`: Tool action failure message.
  - `approval_required`: Sensitive action confirmation modal prompt.
  - `task_finish`: Task completion event with final structured data.
