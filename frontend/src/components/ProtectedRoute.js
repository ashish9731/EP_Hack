import React, { useState, useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { authAPI } from '../lib/api';

export const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [user, setUser] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();
  
  useEffect(() => {
    console.log('ProtectedRoute: Checking authentication status');
    console.log('Location state:', location.state);
    
    if (location.state?.user) {
      console.log('Using user from location state:', location.state.user);
      setUser(location.state.user);
      setIsAuthenticated(true);
      return;
    }
    
    const checkAuth = async () => {
      try {
        console.log('Calling authAPI.getMe() to check authentication');
        const response = await authAPI.getMe();
        console.log('Received response from getMe:', response);
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('ProtectedRoute: Authentication check failed:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response,
          request: error.request
        });
        setIsAuthenticated(false);
      }
    };
    
    checkAuth();
  }, [location.state]);
  
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }
  
  if (isAuthenticated === false) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};