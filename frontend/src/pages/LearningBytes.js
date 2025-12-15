import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, Lightbulb, Video, Timer, Calendar, Play } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const LearningBytes = () => {
  const navigate = useNavigate();
  const [dailyTip, setDailyTip] = useState(null);
  const [tedTalks, setTedTalks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rotationInfo, setRotationInfo] = useState(null);
  const [tipNumber, setTipNumber] = useState(1);
  const [totalTips, setTotalTips] = useState(14);
  const [expandedVideo, setExpandedVideo] = useState(null);
  
  const fetchContent = async () => {
    try {
      // Use mock data instead of actual API calls
      const mockTip = {
        tip: "Maintain steady eye contact with your audience. Research shows that leaders who make consistent eye contact are perceived as 37% more trustworthy and 28% more competent.",
        category: "Presence",
        tip_number: 5,
        total_tips: 14,
        rotation_info: {
          next_rotation: new Date(Date.now() + 86400000).toISOString()
        }
      };
      
      const mockTalks = [
        {
          id: "talk_1",
          title: "Your Body Language May Shape Who You Are",
          speaker: "Amy Cuddy",
          duration: "21:04",
          description: "Body language affects how others see us, but it may also change how we see ourselves. Social psychologist Amy Cuddy argues that 'power posing' -- standing in a posture of confidence, even when we don't feel confident -- can boost feelings of confidence.",
          relevance: "Presence, Gravitas",
          embed_url: "https://www.youtube.com/embed/Ks-_Mh1QhMc"
        },
        {
          id: "talk_2",
          title: "How Great Leaders Inspire Action",
          speaker: "Simon Sinek",
          duration: "18:04",
          description: "How do you explain when others are able to do the things that seem impossible? Why are people who do the extraordinary things deemed 'leaders'? Simon Sinek offers a simple but powerful model for inspirational leadership -- starting with a golden circle and the question 'Why?'",
          relevance: "Communication, Storytelling",
          embed_url: "https://www.youtube.com/embed/qp0HIF3SfI4"
        },
        {
          id: "talk_3",
          title: "The Power of Vulnerability",
          speaker: "Brené Brown",
          duration: "20:06",
          description: "Brené Brown studies human connection -- our ability to empathize, belong, love. In a poignant, funny talk at TEDxHouston, she shares a deep insight from her research, one that sent her on a personal quest to know herself as well as to understand humanity.",
          relevance: "Presence, Communication",
          embed_url: "https://www.youtube.com/embed/iCvmsMzlF7o"
        }
      ];
      
      setDailyTip({ tip: mockTip.tip, category: mockTip.category });
      setRotationInfo(mockTip.rotation_info);
      setTipNumber(mockTip.tip_number || 1);
      setTotalTips(mockTip.total_tips || 14);
      setTedTalks(mockTalks);
    } catch (error) {
      console.error('Error fetching learning content:', error);
      toast.error('Failed to load content');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchContent();
    
    // Update countdown every minute
    const interval = setInterval(() => {
      fetchContent();
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
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
          <p style={{color: '#64748B'}}>Loading...</p>
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
      
      <div className="container mx-auto px-6 py-12 max-w-5xl">
        <div style={{marginBottom: '40px'}}>
          <h1 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
            Learning <span style={{color: '#D4AF37'}}>Bytes</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B'}}>
            Daily insights and expert resources to enhance your executive presence
          </p>
        </div>
        
        {dailyTip && (
          <div className="card-3d" style={{
            backgroundColor: 'rgba(212, 175, 55, 0.05)',
            border: '2px solid #D4AF37',
            borderRadius: '16px', padding: '32px', marginBottom: '40px'
          }}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                <div style={{
                  width: '48px', height: '48px', borderRadius: '12px',
                  backgroundColor: 'rgba(212, 175, 55, 0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <Lightbulb style={{width: '24px', height: '24px', color: '#D4AF37'}} />
                </div>
                <div>
                  <h2 style={{fontSize: '20px', fontWeight: 600, color: '#0F172A'}}>
                    Today's Tip — {dailyTip.category}
                  </h2>
                  <p style={{fontSize: '13px', color: '#64748B', marginTop: '4px'}}>
                    Fresh insight every day at midnight UTC
                  </p>
                </div>
              </div>
              <div style={{
                padding: '6px 14px',
                backgroundColor: '#D4AF37', color: '#FFFFFF',
                borderRadius: '20px', fontSize: '12px', fontWeight: 600
              }}>
                #{tipNumber}
              </div>
            </div>
            <p style={{fontSize: '17px', color: '#1E293B', lineHeight: 1.7, fontWeight: 400}}>
              {dailyTip.tip}
            </p>
          </div>
        )}
        
        <div style={{marginBottom: '24px'}}>
          <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
            Recommended <span style={{color: '#D4AF37'}}>TED Talks</span>
          </h2>
          <p style={{fontSize: '15px', color: '#64748B'}}>
            Expert insights on leadership, communication, and presence
          </p>
        </div>
        
        <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
          {tedTalks.map((talk) => (
            <div
              key={talk.id}
              className="card-3d"
              style={{
                backgroundColor: '#FFFFFF',
                border: expandedVideo === talk.id ? '2px solid #D4AF37' : '2px solid #E2E8F0',
                borderRadius: '16px', padding: '24px',
                transition: 'all 0.3s ease'
              }}
            >
              <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                <div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px'}}>
                    <Video style={{width: '18px', height: '18px', color: '#D4AF37'}} />
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>{talk.duration}</span>
                  </div>
                  
                  <h3 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A', marginBottom: '4px'}}>{talk.title}</h3>
                  <p style={{fontSize: '14px', color: '#D4AF37', marginBottom: '8px', fontWeight: 500}}>by {talk.speaker}</p>
                  <p style={{fontSize: '15px', color: '#1E293B', marginBottom: '12px', lineHeight: 1.6}}>{talk.description}</p>
                  
                  <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px'}}>
                    {talk.relevance.split(', ').map((tag, idx) => (
                      <span key={idx} style={{
                        backgroundColor: 'rgba(212, 175, 55, 0.1)',
                        border: '1px solid rgba(212, 175, 55, 0.3)',
                        borderRadius: '12px', padding: '4px 10px',
                        fontSize: '12px', color: '#92400E'
                      }}>{tag}</span>
                    ))}
                  </div>
                </div>
                
                {expandedVideo === talk.id ? (
                  <>
                    <div style={{
                      position: 'relative',
                      paddingBottom: '56.25%',
                      height: 0,
                      overflow: 'hidden',
                      borderRadius: '12px',
                      backgroundColor: '#000'
                    }}>
                      <iframe
                        src={talk.embed_url}
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: '100%',
                          border: 'none'
                        }}
                        allowFullScreen
                        title={talk.title}
                      />
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setExpandedVideo(null)}
                      style={{border: '2px solid #D4AF37', color: '#D4AF37'}}
                    >
                      Hide Video
                    </Button>
                  </>
                ) : (
                  <Button 
                    size="sm" 
                    onClick={() => setExpandedVideo(talk.id)}
                    style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}
                  >
                    <Play className="mr-2 h-4 w-4" /> Watch Video
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="card-3d" style={{
          marginTop: '48px',
          backgroundColor: 'rgba(212, 175, 55, 0.05)',
          border: '2px solid #D4AF37',
          borderRadius: '16px', padding: '32px', textAlign: 'center'
        }}>
          <h3 style={{fontSize: '22px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
            Want Personalized Learning?
          </h3>
          <p style={{fontSize: '15px', color: '#64748B', marginBottom: '20px', maxWidth: '500px', margin: '0 auto 20px'}}>
            Complete video assessments to get AI-powered recommendations tailored to your specific areas for improvement.
          </p>
          <Button onClick={() => navigate('/dashboard')} style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}>
            Start Assessment
          </Button>
        </div>
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default LearningBytes;
