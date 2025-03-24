import React from 'react';
import { useQuery } from 'react-query';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import axios from 'axios';

interface Order {
  order_id: string;
  customer_name: string;
  item: string;
  quantity: number;
  status: string;
  created_at: string;
}

const OrderList: React.FC = () => {
  const { data: orders, isLoading, error } = useQuery<Order[]>('orders', async () => {
    const response = await axios.get('http://localhost:8000/orders/');
    return response.data;
  });

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading orders: {(error as Error).message}
      </Alert>
    );
  }

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Orders
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Item</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders?.map((order) => (
              <TableRow key={order.order_id}>
                <TableCell>{order.order_id}</TableCell>
                <TableCell>{order.customer_name}</TableCell>
                <TableCell>{order.item}</TableCell>
                <TableCell align="right">{order.quantity}</TableCell>
                <TableCell>{order.status}</TableCell>
                <TableCell>
                  {new Date(order.created_at).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default OrderList; 