import React, { useState, useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { authAPI } from '../lib/api';

export const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Always authenticated
  const [user, setUser] = useState({
    user_id: "mock_user_123",
    email: "demo@example.com",
    name: "Demo User",
    created_at: new Date().toISOString()
  });
  const location = useLocation();
  const navigate = useNavigate();
  
  // Skip authentication check entirely
  useEffect(() => {
    // No need to check auth anymore
    setIsAuthenticated(true);
  }, []);
  
  // Always render children since we're bypassing authentication
  return children;
};