import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { 
  Video, Clock, Target, Play, Square, RotateCcw, 
  Users, TrendingUp, Zap, Trophy, Star, Calendar,
  HardDrive, Cpu, Activity
} from 'lucide-react';
import Webcam from 'react-webcam';
import { api } from '../lib/api';

const Simulator = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState([]);
  const [rotationInfo, setRotationInfo] = useState(null);
  const [poolName, setPoolName] = useState('');
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [countdown, setCountdown] = useState(null);
  
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const countdownIntervalRef = useRef(null);
  
  useEffect(() => {
    fetchScenarios();
    
    // Update countdown every minute
    const interval = setInterval(() => {
      if (rotationInfo) {
        fetchScenarios();
      }
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  const fetchScenarios = async () => {
    try {
      const response = await api.get('/simulator/scenarios');
      
      const data = response.data;
      setScenarios(data.scenarios || []);
      setRotationInfo(data.rotation_info);
      setPoolName(data.pool_name || "Executive Crisis Scenarios");
    } catch (error) {
      console.error('Error fetching scenarios:', error);
      toast.error('Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };
  
  const startCountdown = () => {
    setCountdown(3);
    countdownIntervalRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(countdownIntervalRef.current);
          startRecording();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };
  
  const startRecording = () => {
    setIsRecording(true);
    const stream = webcamRef.current?.stream;
    if (!stream) return;
    
    mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' });
    
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        setRecordedChunks((prev) => [...prev, event.data]);
      }
    };
    
    mediaRecorderRef.current.start();
    
    setTimeout(() => {
      stopRecording();
    }, 180000);
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setCountdown(null);
      
      // Process the recorded video
      processVideo();
    }
  };
  
  const processVideo = async () => {
    if (recordedChunks.length === 0) {
      toast.error('No video recorded');
      return;
    }
    
    setProcessing(true);
    
    try {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const formData = new FormData();
      formData.append('video', blob, 'simulation.webm');
      
      const token = localStorage.getItem('session_token');
      
      // Upload video
      const uploadResponse = await api.post('/videos/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const videoId = uploadResponse.data.video_id;
      
      // Process video
      const processResponse = await api.post(`/videos/${videoId}/process`, {});
      
      const jobId = processResponse.data.job_id;
      
      // Redirect to report page
      navigate(`/report/${jobId}`);
      
      toast.success('Video uploaded and processing started');
    } catch (error) {
      console.error('Error processing video:', error);
      toast.error('Failed to process video');
    } finally {
      setProcessing(false);
      setRecordedChunks([]);
    }
  };
  
  if (loading) {
    return (
      <div style={{minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#FAFAFA'}}>
        <div style={{textAlign: 'center'}}>
          <div style={{
            width: '48px', height: '48px',
            border: '4px solid #E2E8F0', borderTopColor: '#D4AF37',
            borderRadius: '50%', animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{color: '#64748B'}}>Loading scenarios...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
      <nav style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        position: 'sticky', top: 0, zIndex: 50,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
      }}>
        <div className="container mx-auto px-6">
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '16px 0', borderBottom: '1px solid #F1F5F9'
          }}>
            <h1 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A'}}>
              <Zap style={{display: 'inline', width: '28px', height: '28px', color: '#D4AF37', marginRight: '8px'}} />
              Simulator
            </h1>
            
            <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
              <Badge variant="outline" style={{borderColor: '#D4AF37', color: '#D4AF37', fontWeight: 600}}>
                <RotateCcw style={{width: '14px', height: '14px', marginRight: '6px'}} />
                Rotates in {rotationInfo?.remaining_formatted || '2d 14h 32m'}
              </Badge>
              
              <Button 
                variant="outline" 
                onClick={fetchScenarios}
                style={{borderColor: '#E2E8F0', color: '#64748B'}}
              >
                <RotateCcw style={{width: '16px', height: '16px', marginRight: '6px'}} />
                Refresh
              </Button>
            </div>
          </div>
          
          <div style={{padding: '24px 0'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px'}}>
              <Star style={{width: '20px', height: '20px', color: '#D4AF37'}} />
              <h2 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A'}}>{poolName}</h2>
            </div>
            <p style={{color: '#64748B', fontSize: '15px', lineHeight: 1.6}}>
              Practice executive presence in realistic business scenarios. New scenarios rotate every 3 days.
            </p>
          </div>
        </div>
      </nav>
      
      <div className="container mx-auto px-6 py-8">
        {countdown !== null && (
          <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              textAlign: 'center',
              color: '#FFFFFF',
              fontSize: '96px',
              fontWeight: 700
            }}>
              {countdown}
            </div>
          </div>
        )}
        
        {isRecording && (
          <Card style={{marginBottom: '24px', border: '2px solid #EF4444'}}>
            <CardContent style={{padding: '20px'}}>
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px'}}>
                <div style={{
                  width: '12px', height: '12px', 
                  backgroundColor: '#EF4444',
                  borderRadius: '50%',
                  animation: 'pulse 1.5s infinite'
                }}></div>
                <span style={{fontWeight: 600, color: '#EF4444'}}>Recording in Progress</span>
                <span style={{color: '#64748B'}}>·</span>
                <span style={{color: '#64748B'}}>Maximum 3 minutes</span>
              </div>
            </CardContent>
          </Card>
        )}
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px'}}>
          {scenarios.map((scenario) => {
            const diffColors = {
              Low: { bg: '#DCFCE7', text: '#166534', border: '#86EFAC' },
              Medium: { bg: '#FEF3C7', text: '#92400E', border: '#FDE68A' },
              High: { bg: '#FEE2E2', text: '#B91C1C', border: '#FCA5A5' }
            }[scenario.difficulty] || { bg: '#F3F4F6', text: '#374151', border: '#D1D5DB' };
            
            return (
              <div key={scenario.id} style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '16px',
                border: '1px solid #E2E8F0',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
                overflow: 'hidden',
                transition: 'all 0.2s ease',
                cursor: 'pointer',
                position: 'relative'
              }}
              onClick={() => setSelectedScenario(scenario)}
              >
                <div style={{padding: '24px'}}>
                  <div style={{display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px'}}>
                    <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>{scenario.title}</h3>
                    <span style={{
                      backgroundColor: diffColors.bg, color: diffColors.text,
                      border: `1px solid ${diffColors.border}`,
                      padding: '4px 10px', borderRadius: '8px',
                      fontSize: '12px', fontWeight: 600
                    }}>{scenario.difficulty}</span>
                  </div>
                  
                  <p style={{fontSize: '14px', color: '#64748B', marginBottom: '16px', lineHeight: 1.6}}>{scenario.situation}</p>
                  
                  <div style={{display: 'flex', alignItems: 'center', gap: '16px', paddingTop: '16px', borderTop: '1px solid #E2E8F0'}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
                      <Clock style={{width: '16px', height: '16px', color: '#D4AF37'}} />
                      <span style={{fontSize: '13px', color: '#64748B'}}>{scenario.duration}</span>
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', gap: '4px'}}>
                      <Target style={{width: '16px', height: '16px', color: '#D4AF37'}} />
                      <span style={{fontSize: '13px', color: '#64748B'}}>{scenario.focus.length} focus areas</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </div>
  );
};

export default Simulator;