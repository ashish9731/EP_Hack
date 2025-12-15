import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { videoAPI, retentionAPI } from '../lib/api';
import { toast } from 'sonner';
import { Upload, Video, PlayCircle, ArrowLeft, Camera, StopCircle, RotateCcw, CheckCircle, AlertCircle, Mic, MicOff, Settings, Clock, Trash2 } from 'lucide-react';
import Webcam from 'react-webcam';

const KnowYourEP = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('intro');
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  
  // Recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [recordingTime, setRecordingTime] = useState(0);
  const [countdown, setCountdown] = useState(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [facingMode, setFacingMode] = useState('user');
  const [showSettings, setShowSettings] = useState(false);
  
  // Retention settings
  const [retentionPolicy, setRetentionPolicy] = useState('30_days');
  
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const fileInputRef = useRef(null);
  const timerRef = useRef(null);
  const countdownRef = useRef(null);
  
  const RECOMMENDED_DURATION = 180; // 3 minutes
  const MAX_DURATION = 240; // 4 minutes
  
  // Video constraints for better quality
  const videoConstraints = {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: facingMode,
    frameRate: { ideal: 30 }
  };
  
  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (file.size > 200 * 1024 * 1024) {
      toast.error('File size must be less than 200MB');
      return;
    }
    
    setVideoFile(file);
    setVideoPreview(URL.createObjectURL(file));
    setStep('preview');
  };
  
  const startCountdown = () => {
    setCountdown(3);
    countdownRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(countdownRef.current);
          startRecording();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  };
  
  const startRecording = useCallback(() => {
    setIsRecording(true);
    setRecordedChunks([]);
    setRecordingTime(0);
    
    const stream = webcamRef.current?.stream;
    if (!stream) {
      toast.error('Camera not ready');
      return;
    }
    
    // Try to use best codec available
    let mimeType = 'video/webm;codecs=vp9,opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'video/webm;codecs=vp8,opus';
    }
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'video/webm';
    }
    
    mediaRecorderRef.current = new MediaRecorder(stream, {
      mimeType,
      videoBitsPerSecond: 2500000 // 2.5 Mbps for good quality
    });
    
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        setRecordedChunks(prev => [...prev, event.data]);
      }
    };
    
    mediaRecorderRef.current.start(1000); // Collect data every second
    
    // Start timer
    timerRef.current = setInterval(() => {
      setRecordingTime(prev => {
        if (prev >= MAX_DURATION) {
          stopRecording();
          return prev;
        }
        return prev + 1;
      });
    }, 1000);
    
    toast.success('Recording started!');
  }, []);
  
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
      toast.success('Recording stopped');
    }
  }, [isRecording]);
  
  const cancelRecording = () => {
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      setCountdown(null);
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    setRecordingTime(0);
    setRecordedChunks([]);
  };
  
  // Process recorded chunks when recording stops
  useEffect(() => {
    if (recordedChunks.length > 0 && !isRecording) {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const file = new File([blob], `ep_recording_${Date.now()}.webm`, { type: 'video/webm' });
      setVideoFile(file);
      setVideoPreview(URL.createObjectURL(blob));
      setStep('preview');
      setRecordedChunks([]);
    }
  }, [recordedChunks, isRecording]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);
  
  const handleUploadAndProcess = async () => {
    if (!videoFile) return;
    
    setUploading(true);
    try {
      const uploadResponse = await videoAPI.upload(videoFile);
      const videoId = uploadResponse.data.video_id;
      toast.success('Video uploaded successfully');
      
      // Set retention policy
      try {
        await retentionAPI.setVideoRetention(videoId, retentionPolicy);
      } catch (e) {
        console.warn('Failed to set retention policy:', e);
      }
      
      setUploading(false);
      setProcessing(true);
      setStep('processing');
      
      const processResponse = await videoAPI.process(videoId);
      const newJobId = processResponse.data.job_id;
      
      pollJobStatus(newJobId);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed');
      setUploading(false);
      setProcessing(false);
    }
  };
  
  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const statusResponse = await videoAPI.getJobStatus(jobId);
        const job = statusResponse.data;
        
        setProgress(job.progress);
        setCurrentStep(job.current_step);
        
        if (job.status === 'completed') {
          clearInterval(interval);
          toast.success('Analysis complete!');
          
          if (job.report_id) {
            navigate(`/report/${job.report_id}`);
          } else {
            toast.error('Report not found');
            setProcessing(false);
            setStep('preview');
          }
        } else if (job.status === 'failed') {
          clearInterval(interval);
          toast.error('Processing failed: ' + job.error);
          setProcessing(false);
        }
      } catch (error) {
        console.error('Error polling job:', error);
      }
    }, 2000);
  };
  
  const getTimerColor = () => {
    if (recordingTime >= MAX_DURATION - 30) return '#EF4444'; // Red - almost done
    if (recordingTime >= RECOMMENDED_DURATION) return '#22C55E'; // Green - good length
    if (recordingTime >= RECOMMENDED_DURATION - 30) return '#D4AF37'; // Gold - approaching recommended
    return '#64748B'; // Gray - keep going
  };
  
  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
      <nav style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '16px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <Button variant="ghost" onClick={() => navigate('/dashboard')} data-testid="back-to-dashboard">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
          </Button>
          {step === 'record' && (
            <Button variant="ghost" onClick={() => setShowSettings(!showSettings)}>
              <Settings className="h-4 w-4" />
            </Button>
          )}
        </div>
      </nav>
      
      <div className="container mx-auto px-6 py-12 max-w-4xl">
        {/* INTRO STEP */}
        {step === 'intro' && (
          <div data-testid="intro-step">
            <h1 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
              Know Your <span style={{color: '#D4AF37'}}>EP</span>
            </h1>
            <p style={{fontSize: '18px', color: '#64748B', marginBottom: '32px'}}>
              Record or upload a 3-minute video and get your Executive Presence report
            </p>
            
            {/* Instructions Card */}
            <div className="card-3d" style={{
              padding: '28px',
              marginBottom: '24px',
              backgroundColor: 'rgba(212, 175, 55, 0.05)',
              border: '2px solid rgba(212, 175, 55, 0.3)',
              borderRadius: '16px'
            }}>
              <h3 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A', marginBottom: '16px'}}>
                📝 Recording Instructions
              </h3>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px'}}>
                <div style={{padding: '12px', backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E2E8F0'}}>
                  <div style={{fontSize: '24px', marginBottom: '8px'}}>⏱️</div>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A'}}>Duration</div>
                  <div style={{fontSize: '13px', color: '#64748B'}}>2-4 minutes (ideal: 3 min)</div>
                </div>
                <div style={{padding: '12px', backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E2E8F0'}}>
                  <div style={{fontSize: '24px', marginBottom: '8px'}}>👤</div>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A'}}>Introduction</div>
                  <div style={{fontSize: '13px', color: '#64748B'}}>Name, role & context (30-40s)</div>
                </div>
                <div style={{padding: '12px', backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E2E8F0'}}>
                  <div style={{fontSize: '24px', marginBottom: '8px'}}>🎯</div>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A'}}>Key Initiative</div>
                  <div style={{fontSize: '13px', color: '#64748B'}}>Current project/challenge (60-90s)</div>
                </div>
                <div style={{padding: '12px', backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E2E8F0'}}>
                  <div style={{fontSize: '24px', marginBottom: '8px'}}>📖</div>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A'}}>Leadership Story</div>
                  <div style={{fontSize: '13px', color: '#64748B'}}>Challenge & resolution (60-90s)</div>
                </div>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
              <div 
                className="card-3d"
                onClick={() => setStep('record')}
                style={{
                  padding: '32px',
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #D4AF37',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
                data-testid="record-button"
              >
                <Camera style={{width: '48px', height: '48px', color: '#D4AF37', margin: '0 auto 16px'}} />
                <h3 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A', marginBottom: '8px'}}>
                  Record Video
                </h3>
                <p style={{fontSize: '14px', color: '#64748B'}}>
                  Use your camera to record directly
                </p>
              </div>
              
              <div 
                className="card-3d"
                onClick={() => fileInputRef.current?.click()}
                style={{
                  padding: '32px',
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #E2E8F0',
                  borderRadius: '16px',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
                data-testid="upload-button"
              >
                <Upload style={{width: '48px', height: '48px', color: '#64748B', margin: '0 auto 16px'}} />
                <h3 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A', marginBottom: '8px'}}>
                  Upload Video
                </h3>
                <p style={{fontSize: '14px', color: '#64748B'}}>
                  Upload an existing video file
                </p>
              </div>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              style={{display: 'none'}}
            />
          </div>
        )}
        
        {/* RECORD STEP */}
        {step === 'record' && (
          <div data-testid="record-step">
            <div style={{marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
              <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A'}}>
                Record Your <span style={{color: '#D4AF37'}}>Video</span>
              </h2>
              <Button variant="ghost" onClick={() => setStep('intro')}>
                Cancel
              </Button>
            </div>
            
            {/* Settings Panel */}
            {showSettings && (
              <div className="card-3d" style={{
                padding: '16px',
                marginBottom: '16px',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                borderRadius: '12px'
              }}>
                <div style={{display: 'flex', gap: '24px', alignItems: 'center'}}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <span style={{fontSize: '14px', color: '#64748B'}}>Camera:</span>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setFacingMode(f => f === 'user' ? 'environment' : 'user')}
                    >
                      {facingMode === 'user' ? 'Front' : 'Back'}
                    </Button>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <span style={{fontSize: '14px', color: '#64748B'}}>Audio:</span>
                    <Button 
                      variant={audioEnabled ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setAudioEnabled(!audioEnabled)}
                    >
                      {audioEnabled ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              </div>
            )}
            
            {/* Webcam View */}
            <div style={{
              position: 'relative',
              aspectRatio: '16/9',
              backgroundColor: '#000000',
              borderRadius: '16px',
              overflow: 'hidden',
              marginBottom: '24px',
              border: isRecording ? '3px solid #EF4444' : '3px solid #D4AF37'
            }}>
              <Webcam
                ref={webcamRef}
                audio={audioEnabled}
                videoConstraints={videoConstraints}
                onUserMedia={() => setCameraReady(true)}
                onUserMediaError={() => {
                  toast.error('Camera access denied');
                  setCameraReady(false);
                }}
                style={{width: '100%', height: '100%', objectFit: 'cover'}}
                mirrored={facingMode === 'user'}
              />
              
              {/* Countdown Overlay */}
              {countdown && (
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'rgba(0,0,0,0.7)'
                }}>
                  <div style={{
                    fontSize: '120px',
                    fontWeight: 700,
                    color: '#D4AF37',
                    animation: 'pulse 1s ease-in-out'
                  }}>
                    {countdown}
                  </div>
                </div>
              )}
              
              {/* Recording Indicator */}
              {isRecording && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  left: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  backgroundColor: 'rgba(239, 68, 68, 0.9)',
                  borderRadius: '20px',
                  color: '#FFFFFF'
                }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: '#FFFFFF',
                    animation: 'pulse 1s infinite'
                  }} />
                  <span style={{fontWeight: 600}}>REC</span>
                </div>
              )}
              
              {/* Timer */}
              {(isRecording || recordingTime > 0) && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  right: '16px',
                  padding: '8px 16px',
                  backgroundColor: 'rgba(0,0,0,0.7)',
                  borderRadius: '20px',
                  color: getTimerColor(),
                  fontFamily: 'monospace',
                  fontSize: '20px',
                  fontWeight: 700
                }}>
                  {formatTime(recordingTime)} / {formatTime(RECOMMENDED_DURATION)}
                </div>
              )}
              
              {/* Progress Bar */}
              {isRecording && (
                <div style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  backgroundColor: 'rgba(255,255,255,0.3)'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${(recordingTime / MAX_DURATION) * 100}%`,
                    backgroundColor: getTimerColor(),
                    transition: 'width 1s linear'
                  }} />
                </div>
              )}
            </div>
            
            {/* Recording Controls */}
            <div style={{display: 'flex', gap: '12px', justifyContent: 'center'}}>
              {!isRecording && !countdown ? (
                <Button 
                  onClick={startCountdown}
                  disabled={!cameraReady}
                  size="lg"
                  style={{
                    backgroundColor: '#D4AF37',
                    color: '#FFFFFF',
                    padding: '16px 40px',
                    fontSize: '16px'
                  }}
                >
                  <PlayCircle className="mr-2 h-5 w-5" /> Start Recording
                </Button>
              ) : isRecording ? (
                <Button 
                  onClick={stopRecording}
                  size="lg"
                  style={{
                    backgroundColor: '#EF4444',
                    color: '#FFFFFF',
                    padding: '16px 40px',
                    fontSize: '16px'
                  }}
                >
                  <StopCircle className="mr-2 h-5 w-5" /> Stop Recording
                </Button>
              ) : null}
              
              {(isRecording || countdown) && (
                <Button 
                  onClick={cancelRecording}
                  variant="outline"
                  size="lg"
                >
                  <RotateCcw className="mr-2 h-4 w-4" /> Cancel
                </Button>
              )}
            </div>
            
            {/* Tips during recording */}
            {isRecording && recordingTime < RECOMMENDED_DURATION && (
              <div style={{
                marginTop: '24px',
                padding: '16px',
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                borderRadius: '12px',
                border: '1px solid rgba(212, 175, 55, 0.3)',
                textAlign: 'center'
              }}>
                <p style={{fontSize: '14px', color: '#92400E'}}>
                  {recordingTime < 30 && '👤 Start with your introduction...'}
                  {recordingTime >= 30 && recordingTime < 90 && '🎯 Now share your key initiative...'}
                  {recordingTime >= 90 && recordingTime < 150 && '📖 Tell a leadership story...'}
                  {recordingTime >= 150 && '✨ Great! Wrap up when ready...'}
                </p>
              </div>
            )}
          </div>
        )}
        
        {/* PREVIEW STEP */}
        {step === 'preview' && (
          <div data-testid="preview-step">
            <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '24px'}}>
              Review Your <span style={{color: '#D4AF37'}}>Video</span>
            </h2>
            
            <div style={{
              aspectRatio: '16/9',
              backgroundColor: '#000000',
              borderRadius: '16px',
              overflow: 'hidden',
              marginBottom: '24px',
              border: '3px solid #D4AF37'
            }}>
              <video 
                src={videoPreview} 
                controls 
                style={{width: '100%', height: '100%'}}
              />
            </div>
            
            {/* Retention Settings */}
            <div className="card-3d" style={{
              padding: '20px',
              marginBottom: '24px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px'
            }}>
              <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                <Clock style={{width: '20px', height: '20px', color: '#D4AF37'}} />
                <span style={{fontSize: '15px', fontWeight: 600, color: '#0F172A'}}>Video Retention</span>
              </div>
              <div style={{display: 'flex', gap: '8px', flexWrap: 'wrap'}}>
                {['7_days', '30_days', '90_days', '1_year', 'permanent'].map(policy => (
                  <button
                    key={policy}
                    onClick={() => setRetentionPolicy(policy)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: 500,
                      border: retentionPolicy === policy ? '2px solid #D4AF37' : '1px solid #E2E8F0',
                      backgroundColor: retentionPolicy === policy ? 'rgba(212, 175, 55, 0.1)' : '#FFFFFF',
                      color: retentionPolicy === policy ? '#92400E' : '#64748B',
                      cursor: 'pointer'
                    }}
                  >
                    {policy.replace('_', ' ')}
                  </button>
                ))}
              </div>
              <p style={{fontSize: '12px', color: '#64748B', marginTop: '8px'}}>
                Video will be automatically deleted after this period for your privacy.
              </p>
            </div>
            
            <div style={{display: 'flex', gap: '12px', justifyContent: 'center'}}>
              <Button
                variant="outline"
                onClick={() => {
                  setVideoFile(null);
                  setVideoPreview(null);
                  setStep('intro');
                }}
              >
                <RotateCcw className="mr-2 h-4 w-4" /> Re-record
              </Button>
              <Button
                onClick={handleUploadAndProcess}
                disabled={uploading}
                style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}
              >
                {uploading ? 'Uploading...' : 'Analyze My EP'}
              </Button>
            </div>
          </div>
        )}
        
        {/* PROCESSING STEP */}
        {step === 'processing' && (
          <div data-testid="processing-step" style={{textAlign: 'center', padding: '48px 0'}}>
            <div style={{
              width: '80px',
              height: '80px',
              border: '4px solid #E2E8F0',
              borderTopColor: '#D4AF37',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 32px'
            }} />
            
            <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
              Analyzing Your <span style={{color: '#D4AF37'}}>Presence</span>
            </h2>
            
            <p style={{fontSize: '16px', color: '#64748B', marginBottom: '32px'}}>
              {currentStep || 'Processing your video...'}
            </p>
            
            <div style={{maxWidth: '400px', margin: '0 auto'}}>
              <Progress value={progress} className="h-3" />
              <p style={{fontSize: '14px', color: '#64748B', marginTop: '8px'}}>
                {Math.round(progress)}% complete
              </p>
            </div>
            
            <div style={{
              marginTop: '32px',
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: '16px',
              maxWidth: '600px',
              margin: '32px auto 0'
            }}>
              {[
                { step: 'Transcription', threshold: 20 },
                { step: 'Audio Analysis', threshold: 40 },
                { step: 'Video Analysis', threshold: 60 },
                { step: 'AI Scoring', threshold: 80 },
              ].map((item, idx) => (
                <div key={idx} style={{textAlign: 'center'}}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px',
                    backgroundColor: progress >= item.threshold ? 'rgba(34, 197, 94, 0.1)' : '#F8FAFC',
                    border: progress >= item.threshold ? '2px solid #22C55E' : '2px solid #E2E8F0'
                  }}>
                    {progress >= item.threshold ? (
                      <CheckCircle style={{width: '20px', height: '20px', color: '#22C55E'}} />
                    ) : (
                      <span style={{fontSize: '14px', color: '#64748B'}}>{idx + 1}</span>
                    )}
                  </div>
                  <span style={{fontSize: '12px', color: progress >= item.threshold ? '#22C55E' : '#64748B'}}>
                    {item.step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default KnowYourEP;
