import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import {
  TextField,
  Button,
  Paper,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import axios from 'axios';

interface OrderFormData {
  customer_name: string;
  item: string;
  quantity: number;
}

const OrderCreate: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [formData, setFormData] = React.useState<OrderFormData>({
    customer_name: '',
    item: '',
    quantity: 1,
  });

  const createOrder = useMutation(
    (data: OrderFormData) =>
      axios.post('http://localhost:8000/orders/', data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        navigate('/');
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createOrder.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) || 0 : value,
    }));
  };

  return (
    <Paper sx={{ p: 4, maxWidth: 500, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Create New Order
      </Typography>
      
      {createOrder.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error creating order: {(createOrder.error as Error).message}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Customer Name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleChange}
            required
          />
          
          <TextField
            label="Item"
            name="item"
            value={formData.item}
            onChange={handleChange}
            required
          />
          
          <TextField
            label="Quantity"
            name="quantity"
            type="number"
            value={formData.quantity}
            onChange={handleChange}
            required
            inputProps={{ min: 1 }}
          />
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={createOrder.isLoading}
          >
            {createOrder.isLoading ? 'Creating...' : 'Create Order'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default OrderCreate; 