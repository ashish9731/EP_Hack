import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import KnowYourEP from './pages/KnowYourEP';
import Report from './pages/Report';
import Simulator from './pages/Simulator';
import LearningBytes from './pages/LearningBytes';
import Training from './pages/Training';
import ExecutiveCoaching from './pages/ExecutiveCoaching';
import SharedReport from './pages/SharedReport';
import AuthCallback from './pages/AuthCallback';
import Methodology from './pages/Methodology';
import Pricing from './pages/Pricing';
// import { ProtectedRoute } from './components/ProtectedRoute';

function AppRouter() {
  const location = useLocation();
  
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/know-your-ep" element={<KnowYourEP />} />
      <Route path="/report/:reportId" element={<Report />} />
      <Route path="/simulator" element={<Simulator />} />
      <Route path="/learning" element={<LearningBytes />} />
      <Route path="/training" element={<Training />} />
      <Route path="/coaching" element={<ExecutiveCoaching />} />
      <Route path="/methodology" element={<Methodology />} />
      <Route path="/shared/:shareId" element={<SharedReport />} />
      
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

function App() {
  return (
    <>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
      <Toaster position="top-right" />
    </>
  );
}

export default App;
