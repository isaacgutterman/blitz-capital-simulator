import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Simulation API calls
export const getSimulations = async () => {
  const response = await api.get('/api/simulations');
  return response.data;
};

export const getSimulationStatus = async (simulationId) => {
  const response = await api.get(`/api/simulations/${simulationId}/status`);
  return response.data;
};

export const getSimulationPortfolio = async (simulationId) => {
  const response = await api.get(`/api/simulations/${simulationId}/portfolio`);
  return response.data;
};

export const startHistoricalSimulation = async (simulationData) => {
  const response = await api.post('/api/simulations/historical', simulationData);
  return response.data;
};

export const startRealtimeSimulation = async (simulationData) => {
  const response = await api.post('/api/simulations/realtime', simulationData);
  return response.data;
};

// Algorithm API calls
export const getAlgorithms = async () => {
  const response = await api.get('/api/algorithms');
  return response.data;
};

// WebSocket connection for real-time updates
export const createWebSocketConnection = (simulationId, onMessage) => {
  const wsUrl = `ws://localhost:8000/ws/${simulationId}`;
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return ws;
};

export default api;
