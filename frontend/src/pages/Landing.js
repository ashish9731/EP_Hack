import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowRight, CheckCircle, BarChart3, Video, Brain, MessageSquare, Sparkles, LayoutDashboard } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(true);

  useEffect(() => {
    // Skip authentication check - always logged in
    setIsLoggedIn(true);
  }, []);
  
  return (
    <div style={{backgroundColor: '#FFFFFF', minHeight: '100vh'}}>
      <nav style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid #E2E8F0',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div style={{fontSize: '22px', fontWeight: 600, color: '#0F172A', letterSpacing: '-0.5px'}}>
            <span>Executive Presence</span>{' '}
            <span style={{color: '#D4AF37'}}>Quotient</span>
          </div>
          <Button 
            onClick={() => navigate('/dashboard')}
            style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}
          >
            <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
          </Button>
        </div>
      </nav>
      
      <div style={{
        background: 'linear-gradient(135deg, #FAFAFA 0%, #FFFFFF 50%, #FFF9F0 100%)',
        paddingTop: '100px',
        paddingBottom: '120px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '800px',
          height: '800px',
          background: 'radial-gradient(circle, rgba(212, 175, 55, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none'
        }}></div>
        
        <div className="container mx-auto px-6 max-w-5xl relative z-10">
          <div className="text-center">
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: 'rgba(212, 175, 55, 0.1)',
              border: '1px solid rgba(212, 175, 55, 0.3)',
              borderRadius: '24px',
              marginBottom: '32px'
            }}>
              <Sparkles style={{width: '16px', height: '16px', color: '#D4AF37'}} />
              <span style={{fontSize: '14px', color: '#D4AF37', fontWeight: 500}}>
                AI-Powered Leadership Assessment
              </span>
            </div>
            
            <h1 style={{
              fontSize: '64px',
              fontWeight: 700,
              lineHeight: 1.1,
              color: '#0F172A',
              marginBottom: '32px',
              letterSpacing: '-0.03em'
            }}>
              Master Your<br/>
              <span style={{
                background: 'linear-gradient(135deg, #D4AF37 0%, #F4D03F 50%, #D4AF37 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                display: 'inline-block'
              }}>
                Executive Presence
              </span>
            </h1>
            
            <p style={{
              fontSize: '22px',
              color: '#64748B',
              marginBottom: '48px',
              maxWidth: '700px',
              margin: '0 auto 48px',
              lineHeight: 1.6,
              fontWeight: 400
            }}>
              Upload a 3-minute video and receive research-backed insights on communication, gravitas, presence, and storytelling—powered by AI.
            </p>
            
            <div className="flex gap-4 justify-center flex-wrap">
              <>
                <Button 
                  size="lg" 
                  onClick={() => navigate('/dashboard')}
                  style={{
                    fontSize: '17px',
                    padding: '14px 36px',
                    fontWeight: 500,
                    backgroundColor: '#D4AF37',
                    color: '#FFFFFF'
                  }}
                >
                  Go to Dashboard <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  onClick={() => navigate('/pricing')}
                  style={{
                    fontSize: '17px',
                    padding: '14px 36px',
                    borderColor: '#D4AF37',
                    color: '#D4AF37',
                    border: '2px solid #D4AF37'
                  }}
                >
                  View Pricing
                </Button>
              </>
            </div>
            
            <div style={{
              marginTop: '48px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '24px',
              padding: '16px 32px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
            }}>
              <div style={{textAlign: 'center'}}>
                <div style={{fontSize: '28px', fontWeight: 700, color: '#D4AF37', fontFamily: 'IBM Plex Mono'}}>2-3min</div>
                <div style={{fontSize: '13px', color: '#64748B'}}>Analysis Time</div>
              </div>
              <div style={{width: '1px', height: '40px', backgroundColor: '#E2E8F0'}}></div>
              <div style={{textAlign: 'center'}}>
                <div style={{fontSize: '28px', fontWeight: 700, color: '#D4AF37', fontFamily: 'IBM Plex Mono'}}>4</div>
                <div style={{fontSize: '13px', color: '#64748B'}}>EP Dimensions</div>
              </div>
              <div style={{width: '1px', height: '40px', backgroundColor: '#E2E8F0'}}></div>
              <div style={{textAlign: 'center'}}>
                <div style={{fontSize: '28px', fontWeight: 700, color: '#D4AF37', fontFamily: 'IBM Plex Mono'}}>100%</div>
                <div style={{fontSize: '13px', color: '#64748B'}}>AI-Powered</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div style={{
        paddingTop: '80px',
        paddingBottom: '80px',
        backgroundColor: '#FAFAFA'
      }}>
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="text-center mb-16">
            <h2 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
              Four Research-Backed <span style={{color: '#D4AF37'}}>Dimensions</span>
            </h2>
            <p style={{fontSize: '19px', color: '#64748B'}}>
              Comprehensive scoring across key leadership indicators
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Brain, title: 'Gravitas', weight: '25%', desc: 'Commanding presence, decisiveness, poise under pressure', color: '#D4AF37' },
              { icon: MessageSquare, title: 'Communication', weight: '35%', desc: 'Speaking rate, clarity, vocal metrics, filler words', color: '#D4AF37' },
              { icon: Video, title: 'Presence', weight: '25%', desc: 'Posture, eye contact, facial expressions, gestures', color: '#D4AF37' },
              { icon: BarChart3, title: 'Storytelling', weight: '15%', desc: 'Narrative structure, authenticity, concreteness', color: '#D4AF37' },
            ].map((dim, idx) => (
              <div 
                key={idx} 
                className="card-hover"
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #D4AF37',
                  borderRadius: '12px',
                  padding: '28px',
                  cursor: 'pointer'
                }}
              >
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(212, 175, 55, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '20px'
                }}>
                  <dim.icon style={{width: '28px', height: '28px', color: dim.color}} />
                </div>
                <h3 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A', marginBottom: '8px'}}>{dim.title}</h3>
                <div style={{fontSize: '15px', color: '#D4AF37', fontWeight: 600, marginBottom: '12px', fontFamily: 'IBM Plex Mono'}}>{dim.weight}</div>
                <p style={{fontSize: '14px', color: '#64748B', lineHeight: 1.6}}>{dim.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div style={{paddingTop: '80px', paddingBottom: '80px'}}>
        <div className="container mx-auto px-6 max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-16 items-start">
            <div>
              <h2 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '40px'}}>
                How It <span style={{color: '#D4AF37'}}>Works</span>
              </h2>
              <div className="space-y-10">
                {[
                  { num: '01', title: 'Record or Upload', desc: '3-minute video speaking to camera about your role and leadership', icon: Video },
                  { num: '02', title: 'AI Analysis', desc: 'Whisper transcription, GPT-4o vision & NLP analysis in under 3 minutes', icon: Brain },
                  { num: '03', title: 'Detailed Report', desc: 'Comprehensive scores, benchmarks, drill-downs, and coaching tips', icon: BarChart3 },
                  { num: '04', title: 'Improve', desc: 'Practice with scenarios, training modules, and executive coaching', icon: Sparkles },
                ].map((item, idx) => (
                  <div key={idx} className="flex gap-6">
                    <div style={{
                      fontSize: '36px',
                      fontWeight: 700,
                      color: '#D4AF37',
                      fontFamily: 'IBM Plex Mono',
                      minWidth: '70px'
                    }}>
                      {item.num}
                    </div>
                    <div style={{flex: 1}}>
                      <h3 style={{fontSize: '22px', fontWeight: 600, color: '#0F172A', marginBottom: '10px'}}>{item.title}</h3>
                      <p style={{fontSize: '16px', color: '#64748B', lineHeight: 1.7}}>{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="card-hover" style={{
              backgroundColor: '#FAFAFA',
              border: '2px solid #D4AF37',
              borderRadius: '16px',
              padding: '40px'
            }}>
              <div style={{
                display: 'inline-block',
                padding: '8px 16px',
                backgroundColor: 'rgba(212, 175, 55, 0.15)',
                borderRadius: '20px',
                marginBottom: '24px'
              }}>
                <span style={{fontSize: '14px', color: '#D4AF37', fontWeight: 600}}>What You'll Receive</span>
              </div>
              
              <h3 style={{fontSize: '26px', fontWeight: 700, color: '#0F172A', marginBottom: '28px'}}>
                Comprehensive EP Report
              </h3>
              
              <div className="space-y-4">
                {[
                  'Overall EP Score with performance level',
                  'Scores across 4 dimensions with benchmarks',
                  'Word-by-word filler word timestamps',
                  'Pause detection with duration classification',
                  'Sentence clarity breakdown',
                  'Vocal metrics (pitch, loudness, articulation)',
                  'Visual presence analysis',
                  'Leadership signal analysis',
                  'Personalized coaching recommendations',
                  'PDF export for coaches',
                ].map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle style={{width: '22px', height: '22px', color: '#D4AF37', marginTop: '2px', flexShrink: 0}} />
                    <span style={{fontSize: '15px', color: '#1E293B', lineHeight: 1.5}}>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div style={{
        paddingTop: '80px',
        paddingBottom: '80px',
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '0',
          left: '0',
          right: '0',
          bottom: '0',
          backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(212, 175, 55, 0.15) 0%, transparent 50%), radial-gradient(circle at 80% 50%, rgba(212, 175, 55, 0.15) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        
        <div className="container mx-auto px-6 text-center relative z-10">
          <h2 style={{fontSize: '48px', fontWeight: 700, color: '#FFFFFF', marginBottom: '20px'}}>
            Ready to Assess Your <span style={{color: '#D4AF37'}}>Executive Presence</span>?
          </h2>
          <p style={{fontSize: '20px', color: 'rgba(255,255,255,0.8)', marginBottom: '40px', maxWidth: '700px', margin: '0 auto 40px'}}>
            Join leaders mastering their communication through AI-powered insights
          </p>
          <Button 
            size="lg" 
            onClick={() => navigate('/signup')} 
            data-testid="footer-cta"
            style={{
              fontSize: '18px',
              padding: '16px 40px',
              fontWeight: 600
            }}
          >
            Get Started Now <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </div>
      
      <footer style={{
        paddingTop: '32px',
        paddingBottom: '32px',
        borderTop: '1px solid #E2E8F0',
        backgroundColor: '#FAFAFA'
      }}>
        <div className="container mx-auto px-6 text-center">
          <p style={{fontSize: '14px', color: '#64748B'}}>
            © 2025 Executive Presence Quotient. Professional leadership assessment platform.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
