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
    
    const processSession = async () => {
      // Always redirect to dashboard without authentication
      const mockUser = {
        user_id: "mock_user_123",
        email: "demo@example.com",
        name: "Demo User",
        created_at: new Date().toISOString()
      };
      
      navigate('/dashboard', { 
        replace: true,
        state: { user: mockUser }
      });
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