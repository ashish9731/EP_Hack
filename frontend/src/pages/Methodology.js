import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, Video, Mic, Eye, Brain, BarChart3, Lightbulb, CheckCircle, ArrowRight } from 'lucide-react';

const Methodology = () => {
  const navigate = useNavigate();
  
  const dimensions = [
    {
      name: 'Gravitas',
      weight: '25%',
      color: '#8B5CF6',
      icon: '⚡',
      description: 'The projection of confidence, decisiveness, and authority that commands attention and respect.',
      parameters: [
        { name: 'Commanding Presence', calculation: 'Analyzed through posture stability, eye contact consistency, and vocal authority markers', weight: '30%' },
        { name: 'Decisiveness', calculation: 'Measured by response clarity, hedging language frequency, and statement confidence', weight: '25%' },
        { name: 'Poise Under Pressure', calculation: 'Assessed via speech rate consistency, filler word patterns, and nervous gesture detection', weight: '20%' },
        { name: 'Emotional Intelligence', calculation: 'Evaluated through tonal variation, empathy markers in language, and facial expression analysis', weight: '15%' },
        { name: 'Vision Articulation', calculation: 'Scored based on forward-looking statements, strategic language use, and clarity of direction', weight: '10%' },
      ],
      research: 'Based on CTI Executive Presence research showing gravitas accounts for 67% of EP perception.'
    },
    {
      name: 'Communication',
      weight: '35%',
      color: '#D4AF37',
      icon: '🗣️',
      description: 'The ability to speak clearly, persuasively, and with appropriate pacing and emphasis.',
      parameters: [
        { name: 'Speaking Rate', calculation: 'Words per minute calculated from transcript. Optimal range: 120-150 WPM', weight: '20%' },
        { name: 'Filler Words', calculation: 'Count of "um", "uh", "like", "you know" per minute. Lower is better.', weight: '20%' },
        { name: 'Strategic Pauses', calculation: 'Detection of intentional pauses >1s before key points. Optimal: 2-4 per minute', weight: '20%' },
        { name: 'Clarity Score', calculation: 'NLP analysis of sentence structure, vocabulary level, and logical flow', weight: '25%' },
        { name: 'Persuasion Index', calculation: 'Analysis of rhetorical techniques, call-to-action usage, and evidence citation', weight: '15%' },
      ],
      research: 'Harvard Business Review research indicates optimal speaking rate and strategic pauses increase message retention by 40%.'
    },
    {
      name: 'Presence',
      weight: '25%',
      color: '#22C55E',
      icon: '👁️',
      description: 'The visual impact through body language, eye contact, gestures, and overall physical demeanor.',
      parameters: [
        { name: 'Posture Score', calculation: 'Computer vision analysis of spine alignment, shoulder position, and head tilt', weight: '25%' },
        { name: 'Eye Contact Ratio', calculation: 'Percentage of time eyes directed at camera. Optimal: 60-70%', weight: '25%' },
        { name: 'Gesture Rate', calculation: 'Hand movements per minute. Optimal range: 3-6 gestures/min for emphasis', weight: '20%' },
        { name: 'First Impression', calculation: 'Analysis of initial 7 seconds: expression, posture, and vocal energy', weight: '20%' },
        { name: 'Consistency', calculation: 'Variance in energy levels and engagement throughout the video', weight: '10%' },
      ],
      research: 'Princeton research shows first impressions form within 100ms. MIT studies confirm eye contact increases trust by 40%.'
    },
    {
      name: 'Storytelling',
      weight: '15%',
      color: '#F59E0B',
      icon: '📖',
      description: 'The ability to structure narratives that engage, inspire, and make messages memorable.',
      parameters: [
        { name: 'Narrative Structure', calculation: 'Detection of story arc: setup, conflict, resolution pattern', weight: '30%' },
        { name: 'Authenticity', calculation: 'Personal pronoun usage, specific details, and emotional markers', weight: '25%' },
        { name: 'Concreteness', calculation: 'Ratio of specific examples vs. abstract concepts', weight: '20%' },
        { name: 'Pacing', calculation: 'Narrative timing, tension building, and climax placement', weight: '15%' },
        { name: 'Memorability', calculation: 'Use of metaphors, analogies, and memorable phrases', weight: '10%' },
      ],
      research: 'Stanford GSB research shows stories are 22x more memorable than facts alone.'
    },
  ];
  
  const pipelineSteps = [
    { 
      step: 1, 
      name: 'Video Upload', 
      icon: Video, 
      description: 'You upload or record a 2-4 minute video of yourself speaking',
      tech: 'Secure upload to encrypted cloud storage with GridFS'
    },
    { 
      step: 2, 
      name: 'Audio Extraction', 
      icon: Mic, 
      description: 'FFmpeg extracts high-quality audio track from video',
      tech: 'FFmpeg with PCM 16-bit, 16kHz mono conversion'
    },
    { 
      step: 3, 
      name: 'Transcription', 
      icon: Brain, 
      description: 'OpenAI Whisper transcribes speech with word-level timestamps',
      tech: 'whisper-1 model with verbose_json output'
    },
    { 
      step: 4, 
      name: 'Audio Analysis', 
      icon: Mic, 
      description: 'PyDub analyzes speaking rate, pauses, and filler words',
      tech: 'Custom Python analysis with timestamp correlation'
    },
    { 
      step: 5, 
      name: 'Video Analysis', 
      icon: Eye, 
      description: 'OpenCV and GPT-4o analyze visual presence and body language',
      tech: 'Frame sampling + vision model analysis'
    },
    { 
      step: 6, 
      name: 'NLP Scoring', 
      icon: Brain, 
      description: 'GPT-4o evaluates communication quality and storytelling',
      tech: 'Structured prompt engineering with JSON output'
    },
    { 
      step: 7, 
      name: 'Score Aggregation', 
      icon: BarChart3, 
      description: 'Weighted calculation produces final EP score',
      tech: 'Weighted average: 25% Gravitas + 35% Communication + 25% Presence + 15% Storytelling'
    },
    { 
      step: 8, 
      name: 'Report Generation', 
      icon: Lightbulb, 
      description: 'Personalized coaching tips generated based on weak areas',
      tech: 'AI-generated recommendations tailored to your profile'
    },
  ];
  
  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
      {/* Navigation */}
      <nav style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '16px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <Button variant="ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>
      </nav>
      
      <div className="container mx-auto px-6 py-12 max-w-6xl">
        {/* Header */}
        <div style={{textAlign: 'center', marginBottom: '60px'}}>
          <h1 style={{fontSize: '48px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
            How <span style={{color: '#D4AF37'}}>EP Quotient</span> Works
          </h1>
          <p style={{fontSize: '20px', color: '#64748B', maxWidth: '700px', margin: '0 auto', lineHeight: 1.7}}>
            Our AI-powered platform analyzes your executive presence across four scientifically-validated dimensions using advanced machine learning and natural language processing.
          </p>
        </div>
        
        {/* Overall Score Formula */}
        <div className="card-3d" style={{
          backgroundColor: '#FFFFFF',
          border: '2px solid #D4AF37',
          borderRadius: '16px',
          padding: '32px',
          marginBottom: '48px',
          textAlign: 'center'
        }}>
          <h2 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
            EP Score Calculation Formula
          </h2>
          <div style={{
            fontFamily: 'IBM Plex Mono, monospace',
            fontSize: '18px',
            color: '#1E293B',
            backgroundColor: '#F8FAFC',
            padding: '20px',
            borderRadius: '12px',
            marginBottom: '16px'
          }}>
            <span style={{color: '#8B5CF6'}}>Gravitas × 0.25</span> + 
            <span style={{color: '#D4AF37'}}> Communication × 0.35</span> + 
            <span style={{color: '#22C55E'}}> Presence × 0.25</span> + 
            <span style={{color: '#F59E0B'}}> Storytelling × 0.15</span> = 
            <span style={{fontWeight: 700}}> EP Score</span>
          </div>
          <p style={{fontSize: '14px', color: '#64748B'}}>
            Each dimension is scored 0-100 based on multiple parameters, then weighted to calculate your overall EP score.
          </p>
        </div>
        
        {/* Analysis Pipeline */}
        <div style={{marginBottom: '60px'}}>
          <h2 style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '32px', textAlign: 'center'}}>
            Analysis <span style={{color: '#D4AF37'}}>Pipeline</span>
          </h2>
          
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px'}}>
            {pipelineSteps.map((step, idx) => (
              <div key={idx} style={{position: 'relative'}}>
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #E2E8F0',
                  borderRadius: '16px',
                  padding: '24px',
                  height: '100%',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#D4AF37';
                  e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#E2E8F0';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                >
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    backgroundColor: '#D4AF37',
                    color: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '16px',
                    marginBottom: '16px'
                  }}>
                    {step.step}
                  </div>
                  <step.icon style={{width: '24px', height: '24px', color: '#D4AF37', marginBottom: '12px'}} />
                  <h3 style={{fontSize: '16px', fontWeight: 600, color: '#0F172A', marginBottom: '8px'}}>{step.name}</h3>
                  <p style={{fontSize: '13px', color: '#64748B', marginBottom: '12px', lineHeight: 1.5}}>{step.description}</p>
                  <p style={{fontSize: '11px', color: '#94A3B8', fontFamily: 'monospace'}}>{step.tech}</p>
                </div>
                {idx < pipelineSteps.length - 1 && idx !== 3 && (
                  <ArrowRight style={{
                    position: 'absolute',
                    right: '-20px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: '24px',
                    height: '24px',
                    color: '#D4AF37',
                    zIndex: 10
                  }} />
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Four Dimensions Detailed */}
        <div style={{marginBottom: '60px'}}>
          <h2 style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '32px', textAlign: 'center'}}>
            The Four <span style={{color: '#D4AF37'}}>Dimensions</span>
          </h2>
          
          <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
            {dimensions.map((dim, idx) => (
              <div key={idx} className="card-3d" style={{
                backgroundColor: '#FFFFFF',
                border: '2px solid #E2E8F0',
                borderRadius: '16px',
                overflow: 'hidden',
                transition: 'all 0.3s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = dim.color;
                e.currentTarget.style.boxShadow = `0 8px 24px ${dim.color}20`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#E2E8F0';
                e.currentTarget.style.boxShadow = 'none';
              }}
              >
                {/* Dimension Header */}
                <div style={{
                  padding: '24px 28px',
                  borderBottom: '1px solid #E2E8F0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                    <span style={{fontSize: '32px'}}>{dim.icon}</span>
                    <div>
                      <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A'}}>{dim.name}</h3>
                      <p style={{fontSize: '14px', color: '#64748B', marginTop: '4px'}}>{dim.description}</p>
                    </div>
                  </div>
                  <div style={{
                    padding: '8px 20px',
                    backgroundColor: `${dim.color}15`,
                    borderRadius: '20px',
                    border: `2px solid ${dim.color}40`
                  }}>
                    <span style={{fontSize: '18px', fontWeight: 700, color: dim.color}}>{dim.weight}</span>
                    <span style={{fontSize: '12px', color: '#64748B', marginLeft: '4px'}}>weight</span>
                  </div>
                </div>
                
                {/* Parameters Table */}
                <div style={{padding: '24px 28px'}}>
                  <table style={{width: '100%', borderCollapse: 'collapse'}}>
                    <thead>
                      <tr style={{borderBottom: '1px solid #E2E8F0'}}>
                        <th style={{textAlign: 'left', padding: '12px 0', fontSize: '13px', fontWeight: 600, color: '#64748B'}}>Parameter</th>
                        <th style={{textAlign: 'left', padding: '12px 0', fontSize: '13px', fontWeight: 600, color: '#64748B'}}>How It's Calculated</th>
                        <th style={{textAlign: 'right', padding: '12px 0', fontSize: '13px', fontWeight: 600, color: '#64748B'}}>Weight</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dim.parameters.map((param, pIdx) => (
                        <tr key={pIdx} style={{borderBottom: pIdx < dim.parameters.length - 1 ? '1px solid #F1F5F9' : 'none'}}>
                          <td style={{padding: '14px 0', fontSize: '14px', fontWeight: 500, color: '#0F172A'}}>{param.name}</td>
                          <td style={{padding: '14px 0', fontSize: '13px', color: '#64748B', paddingRight: '20px'}}>{param.calculation}</td>
                          <td style={{padding: '14px 0', fontSize: '14px', fontWeight: 600, color: dim.color, textAlign: 'right'}}>{param.weight}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  <div style={{
                    marginTop: '20px',
                    padding: '12px 16px',
                    backgroundColor: '#F8FAFC',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: '#64748B'
                  }}>
                    📚 <strong>Research basis:</strong> {dim.research}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* How to Use */}
        <div className="card-3d" style={{
          backgroundColor: 'rgba(212, 175, 55, 0.05)',
          border: '2px solid #D4AF37',
          borderRadius: '16px',
          padding: '40px',
          marginBottom: '48px'
        }}>
          <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '24px', textAlign: 'center'}}>
            How to <span style={{color: '#D4AF37'}}>Use This App</span>
          </h2>
          
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px'}}>
            {[
              { step: '1', title: 'Record Your Video', desc: 'Use the "Know Your EP" feature to record a 2-4 minute video. Include: introduction (30s), current initiative (60-90s), and a leadership story (60-90s).' },
              { step: '2', title: 'Get Your Analysis', desc: 'Our AI analyzes your video across 20+ parameters in 4 dimensions. Processing takes 2-5 minutes depending on video length.' },
              { step: '3', title: 'Review & Improve', desc: 'Review your detailed report with scores, benchmarks, and personalized coaching tips. Use Training and Simulator to practice weak areas.' },
            ].map((item, idx) => (
              <div key={idx} style={{textAlign: 'center'}}>
                <div style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  backgroundColor: '#D4AF37',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  fontWeight: 700,
                  margin: '0 auto 16px'
                }}>
                  {item.step}
                </div>
                <h3 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A', marginBottom: '8px'}}>{item.title}</h3>
                <p style={{fontSize: '14px', color: '#64748B', lineHeight: 1.6}}>{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
        
        {/* CTA */}
        <div style={{textAlign: 'center'}}>
          <Button onClick={() => navigate('/know-your-ep')} size="lg" style={{padding: '16px 40px', fontSize: '16px'}}>
            <Video className="mr-2 h-5 w-5" /> Start Your Assessment
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Methodology;
