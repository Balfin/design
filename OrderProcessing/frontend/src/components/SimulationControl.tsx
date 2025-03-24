import React from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import {
  Paper,
  Typography,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import axios from 'axios';

interface SimulationConfig {
  hot_clients: number;
  normal_clients: number;
}

interface SimulationStatus {
  status: 'running' | 'stopped';
  hot_key_memory?: number;
  hot_key?: string;
  hot_key_value?: string;
}

const SimulationControl: React.FC = () => {
  const queryClient = useQueryClient();
  const [config, setConfig] = React.useState<SimulationConfig>({
    hot_clients: 50,
    normal_clients: 10,
  });

  // Query simulation status
  const { data: status, isLoading } = useQuery<SimulationStatus>(
    'simulation-status',
    async () => {
      const response = await axios.get('http://localhost:8000/simulation/status');
      return response.data;
    },
    { refetchInterval: 1000 } // Poll every second
  );

  // Start simulation mutation
  const startSimulation = useMutation(
    (data: SimulationConfig) =>
      axios.post('http://localhost:8000/simulation/start', data),
    {
      onSuccess: () => queryClient.invalidateQueries('simulation-status'),
    }
  );

  // Stop simulation mutation
  const stopSimulation = useMutation(
    () => axios.post('http://localhost:8000/simulation/stop'),
    {
      onSuccess: () => queryClient.invalidateQueries('simulation-status'),
    }
  );

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: parseInt(value) || 0,
    }));
  };

  const handleStartSimulation = () => {
    startSimulation.mutate(config);
  };

  const handleStopSimulation = () => {
    stopSimulation.mutate();
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Redis Hot Key Simulation
      </Typography>

      {(startSimulation.isError || stopSimulation.isError) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error: {((startSimulation.error || stopSimulation.error) as Error).message}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configuration
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Hot Clients"
            name="hot_clients"
            type="number"
            value={config.hot_clients}
            onChange={handleConfigChange}
            disabled={status?.status === 'running'}
          />
          <TextField
            label="Normal Clients"
            name="normal_clients"
            type="number"
            value={config.normal_clients}
            onChange={handleConfigChange}
            disabled={status?.status === 'running'}
          />
        </Box>
        <Button
          variant="contained"
          color={status?.status === 'running' ? 'secondary' : 'primary'}
          onClick={status?.status === 'running' ? handleStopSimulation : handleStartSimulation}
          disabled={startSimulation.isLoading || stopSimulation.isLoading}
        >
          {status?.status === 'running' ? 'Stop Simulation' : 'Start Simulation'}
        </Button>
      </Paper>

      {status?.status === 'running' && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Simulation Status
            </Typography>
            <Typography>Status: {status.status}</Typography>
            <Typography>Hot Key: {status.hot_key}</Typography>
            <Typography>Memory Usage: {status.hot_key_memory} bytes</Typography>
            <Typography>Current Value: {status.hot_key_value}</Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SimulationControl; 