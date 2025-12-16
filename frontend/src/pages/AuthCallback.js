import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../lib/api';
import { toast } from 'sonner';

const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const hasProcessed = useRef(false);
  
  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;
    
    console.log('AuthCallback component mounted');
    console.log('Location:', location);
    
    const processSession = async () => {
      try {
        console.log('Attempting to get user data from backend');
        // Get the user data from the backend
        const response = await authAPI.getMe();
        
        console.log('Received response from getMe:', response);
        
        if (response.data) {
          console.log('User data received, navigating to dashboard:', response.data);
          navigate('/dashboard', { 
            replace: true,
            state: { user: response.data }
          });
        } else {
          console.error('No user data in response');
          throw new Error('Failed to get user data');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        console.error('Error details:', {
          message: error.message,
          response: error.response,
          request: error.request
        });
        toast.error('Authentication failed');
        navigate('/login');
      }
    };
    
    processSession();
  }, [location, navigate]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-accent mx-auto"></div>
        <p className="mt-6 text-lg text-muted-foreground">Completing sign in...</p>
      </div>
    </div>
  );
};

export default AuthCallback;