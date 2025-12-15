import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, Video, Clock, Target, RefreshCw, Timer } from 'lucide-react';
import Webcam from 'react-webcam';
import { videoAPI } from '../lib/api';
import { toast } from 'sonner';
import axios from 'axios';

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
      // Use mock data instead of actual API calls
      const mockScenarios = [
        {
          id: "scenario_1",
          title: "Board Presentation Challenge",
          situation: "You're presenting a critical quarterly update to the board. Several members seem skeptical about your division's performance.",
          prompt: "Address concerns diplomatically while demonstrating confidence in your strategy. Show both accountability and vision.",
          difficulty: "High",
          duration: "3 minutes",
          focus: ["Gravitas", "Communication"]
        },
        {
          id: "scenario_2",
          title: "Difficult Stakeholder Conversation",
          situation: "A key client is upset about a project delay and is threatening to pull their business.",
          prompt: "Acknowledge their concerns, explain the situation without making excuses, and outline concrete next steps.",
          difficulty: "Medium",
          duration: "2 minutes",
          focus: ["Communication", "Presence"]
        },
        {
          id: "scenario_3",
          title: "Leading Through Uncertainty",
          situation: "Your team is anxious about upcoming organizational changes that haven't been officially announced yet.",
          prompt: "Provide reassurance without sharing confidential information. Demonstrate calm authority and empathy.",
          difficulty: "Low",
          duration: "90 seconds",
          focus: ["Gravitas", "Presence"]
        }
      ];
      
      setScenarios(mockScenarios);
      setRotationInfo({
        next_rotation: new Date(Date.now() + 86400000).toISOString(),
        pool_size: 12
      });
      setPoolName("Executive Crisis Scenarios");
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
    }
  };
  
  const handleSubmit = async () => {
    if (recordedChunks.length === 0) return;
    
    setProcessing(true);
    
    try {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const file = new File([blob], `scenario_${selectedScenario.id}.webm`, { type: 'video/webm' });
      
      const uploadResponse = await videoAPI.upload(file);
      const videoId = uploadResponse.data.video_id;
      
      const processResponse = await videoAPI.process(videoId);
      const jobId = processResponse.data.job_id;
      
      toast.success('Video submitted! Processing analysis...');
      
      const pollInterval = setInterval(async () => {
        const statusResponse = await videoAPI.getJobStatus(jobId);
        const job = statusResponse.data;
        
        if (job.status === 'completed') {
          clearInterval(pollInterval);
          toast.success('Analysis complete!');
          setTimeout(() => {
            if (job.report_id) {
              navigate(`/report/${job.report_id}`);
            } else {
              toast.error('Report not found for this job');
              setProcessing(false);
            }
          }, 500);
        } else if (job.status === 'failed') {
          clearInterval(pollInterval);
          toast.error('Processing failed: ' + job.error);
          setProcessing(false);
        }
      }, 2000);
    } catch (error) {
      toast.error('Failed to process video');
      setProcessing(false);
    }
  };
  
  useEffect(() => {
    if (recordedChunks.length > 0 && !isRecording) {
      handleSubmit();
    }
  }, [recordedChunks, isRecording]);
  
  const getDifficultyColor = (difficulty) => {
    switch(difficulty) {
      case 'High': return { bg: '#FEE2E2', text: '#991B1B', border: '#FECACA' };
      case 'Medium': return { bg: 'rgba(212, 175, 55, 0.15)', text: '#92400E', border: 'rgba(212, 175, 55, 0.4)' };
      default: return { bg: '#DCFCE7', text: '#166534', border: '#BBF7D0' };
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
  
  if (selectedScenario && !processing) {
    return (
      <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
        <nav style={{
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          padding: '16px 24px',
          position: 'sticky', top: 0, zIndex: 50
        }}>
          <Button variant="ghost" onClick={() => {setSelectedScenario(null); setRecordedChunks([]);}}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Scenarios
          </Button>
        </nav>
        
        <div className="container mx-auto px-6 py-12 max-w-5xl">
          <h1 style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
            {selectedScenario.title}
          </h1>
          
          <div className="card-3d" style={{
            backgroundColor: 'rgba(212, 175, 55, 0.08)',
            border: '2px solid rgba(212, 175, 55, 0.4)',
            borderRadius: '12px', padding: '20px', marginBottom: '24px'
          }}>
            <h3 style={{fontSize: '16px', fontWeight: 700, color: '#92400E', marginBottom: '8px'}}>Situation:</h3>
            <p style={{fontSize: '15px', color: '#78350F', lineHeight: 1.6}}>{selectedScenario.situation}</p>
          </div>
          
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #D4AF37',
            borderRadius: '12px', padding: '20px', marginBottom: '24px'
          }}>
            <h3 style={{fontSize: '16px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>Your Task:</h3>
            <p style={{fontSize: '15px', color: '#1E293B', lineHeight: 1.6}}>{selectedScenario.prompt}</p>
          </div>
          
          <div style={{display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap'}}>
            {selectedScenario.focus.map((item, idx) => (
              <span key={idx} style={{
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                border: '1px solid rgba(212, 175, 55, 0.3)',
                borderRadius: '16px', padding: '6px 14px',
                fontSize: '13px', color: '#92400E', fontWeight: 500
              }}>{item}</span>
            ))}
          </div>
          
          <div style={{
            aspectRatio: '16/9', backgroundColor: '#000000',
            borderRadius: '16px', overflow: 'hidden', marginBottom: '24px',
            border: isRecording ? '3px solid #EF4444' : '3px solid #D4AF37',
            position: 'relative'
          }}>
            <Webcam ref={webcamRef} audio={true} className="w-full h-full object-cover" />
            
            {countdown && (
              <div style={{
                position: 'absolute', inset: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                backgroundColor: 'rgba(0,0,0,0.7)'
              }}>
                <div style={{fontSize: '120px', fontWeight: 700, color: '#D4AF37'}}>{countdown}</div>
              </div>
            )}
            
            {isRecording && (
              <div style={{
                position: 'absolute', top: '16px', left: '16px',
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '8px 16px', backgroundColor: 'rgba(239, 68, 68, 0.9)',
                borderRadius: '20px', color: '#FFFFFF'
              }}>
                <div style={{width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FFFFFF', animation: 'pulse 1s infinite'}} />
                <span style={{fontWeight: 600}}>REC</span>
              </div>
            )}
          </div>
          
          <div style={{display: 'flex', gap: '12px', justifyContent: 'center'}}>
            {!isRecording && !countdown ? (
              <Button onClick={startCountdown} size="lg" style={{backgroundColor: '#D4AF37', color: '#FFFFFF', padding: '14px 36px'}}>
                <Video className="mr-2 h-5 w-5" /> Start Recording
              </Button>
            ) : isRecording ? (
              <Button onClick={stopRecording} size="lg" style={{backgroundColor: '#EF4444', color: '#FFFFFF', padding: '14px 36px'}}>
                Stop Recording
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    );
  }
  
  if (processing) {
    return (
      <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{textAlign: 'center'}}>
          <div style={{
            width: '64px', height: '64px',
            border: '4px solid #E2E8F0', borderTopColor: '#D4AF37',
            borderRadius: '50%', animation: 'spin 1s linear infinite',
            margin: '0 auto 24px'
          }}></div>
          <h2 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>Analyzing Your Response</h2>
          <p style={{fontSize: '16px', color: '#64748B'}}>Processing video with AI analysis...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
      <nav style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '16px 24px',
        position: 'sticky', top: 0, zIndex: 50
      }}>
        <Button variant="ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>
      </nav>
      
      <div className="container mx-auto px-6 py-12">
        <div style={{marginBottom: '40px'}}>
          <h1 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
            Boardroom <span style={{color: '#D4AF37'}}>Simulator</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B'}}>
            Practice high-pressure executive scenarios with AI-powered feedback
          </p>
        </div>
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px'}}>
          {scenarios.map((scenario) => {
            const diffColors = getDifficultyColor(scenario.difficulty);
            return (
              <div
                key={scenario.id}
                className="card-3d"
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #E2E8F0',
                  borderRadius: '16px', padding: '24px',
                  cursor: 'pointer', transition: 'all 0.3s ease'
                }}
                onClick={() => setSelectedScenario(scenario)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#D4AF37';
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 12px 24px -8px rgba(212, 175, 55, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#E2E8F0';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px'}}>
                  <h3 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A'}}>{scenario.title}</h3>
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
