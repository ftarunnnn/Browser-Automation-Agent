export class TaskWebSocket {
  constructor(taskId, onMessage, onError) {
    this.taskId = taskId;
    this.onMessage = onMessage;
    this.onError = onError;
    this.ws = null;
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8000/api/tasks/${this.taskId}/stream`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (this.onMessage) this.onMessage(payload);
      } catch (err) {
        console.error('WebSocket message parse error:', err);
      }
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket connection error:', err);
      if (this.onError) this.onError(err);
    };

    this.ws.onclose = () => {
      console.log(`WebSocket closed for task ${this.taskId}`);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
