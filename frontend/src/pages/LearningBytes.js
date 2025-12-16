import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { 
  Lightbulb, BookOpen, Youtube, RotateCw, 
  Clock, User, Eye, Mic, TrendingUp, Star,
  Zap, Calendar
} from 'lucide-react';
import { api } from '../lib/api';

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
      // Fetch daily tip
      const tipResponse = await api.get('/learning/daily-tip');
      
      setDailyTip(tipResponse.data);
      setRotationInfo(tipResponse.data.rotation_info);
      setTipNumber(tipResponse.data.tip_number || 1);
      setTotalTips(tipResponse.data.total_tips || 14);
      
      // Fetch TED talks
      const talksResponse = await api.get('/learning/ted-talks');
      
      setTedTalks(talksResponse.data || []);
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
        position: 'sticky', top: 0, zIndex: 50
      }}>
        <div className="container mx-auto px-6">
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '16px 0', borderBottom: '1px solid #F1F5F9'
          }}>
            <h1 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A'}}>
              <Lightbulb style={{display: 'inline', width: '28px', height: '28px', color: '#D4AF37', marginRight: '8px'}} />
              Learning <span style={{color: '#D4AF37'}}>Bytes</span>
            </h1>
            
            <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
              <Badge variant="outline" style={{borderColor: '#D4AF37', color: '#D4AF37', fontWeight: 600}}>
                <RotateCw style={{width: '14px', height: '14px', marginRight: '6px'}} />
                Rotates in {rotationInfo?.remaining_formatted || '14h 32m'}
              </Badge>
              
              <Button 
                variant="outline" 
                onClick={fetchContent}
                style={{borderColor: '#E2E8F0', color: '#64748B'}}
              >
                <RotateCw style={{width: '16px', height: '16px', marginRight: '6px'}} />
                Refresh
              </Button>
            </div>
          </div>
          
          <div style={{padding: '24px 0'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px'}}>
              <Star style={{width: '20px', height: '20px', color: '#D4AF37'}} />
              <h2 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A'}}>Daily Executive Insight #{tipNumber} of {totalTips}</h2>
            </div>
            <p style={{color: '#64748B', fontSize: '15px', lineHeight: 1.6}}>
              Bite-sized insights to enhance your executive presence. New tips rotate daily.
            </p>
          </div>
        </div>
      </nav>
      
      <div className="container mx-auto px-6 py-8">
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px'}}>
          {/* Daily Tip Card */}
          <Card style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '16px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
            overflow: 'hidden'
          }}>
            <CardHeader style={{backgroundColor: '#FFF7E6', borderBottom: '1px solid #FEF3C7'}}>
              <CardTitle style={{display: 'flex', alignItems: 'center', gap: '10px', color: '#92400E'}}>
                <Lightbulb style={{width: '24px', height: '24px'}} />
                Today's Insight
              </CardTitle>
            </CardHeader>
            <CardContent style={{padding: '24px'}}>
              <p style={{fontSize: '16px', lineHeight: 1.7, color: '#334155', marginBottom: '20px'}}>
                {dailyTip?.tip}
              </p>
              
              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '24px', paddingTop: '20px', borderTop: '1px dashed #E2E8F0'}}>
                <Badge style={{backgroundColor: '#FEF3C7', color: '#92400E'}}>
                  {dailyTip?.category || 'Leadership'}
                </Badge>
                
                <div style={{display: 'flex', alignItems: 'center', gap: '8px', color: '#94A3B8', fontSize: '14px'}}>
                  <Calendar style={{width: '16px', height: '16px'}} />
                  <span>Daily Rotation</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* TED Talks Section */}
          <div>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px'}}>
              <Youtube style={{width: '24px', height: '24px', color: '#D4AF37'}} />
              <h2 style={{fontSize: '20px', fontWeight: 700, color: '#0F172A'}}>Featured Talks</h2>
            </div>
            
            <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
              {tedTalks.map((talk) => (
                <Card 
                  key={talk.id} 
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
                    overflow: 'hidden',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  onClick={() => window.open(talk.link, '_blank')}
                >
                  <CardContent style={{padding: '20px'}}>
                    <h3 style={{fontSize: '16px', fontWeight: 600, color: '#0F172A', marginBottom: '12px'}}>
                      {talk.title}
                    </h3>
                    
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px'}}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                        <User style={{width: '16px', height: '16px', color: '#94A3B8'}} />
                        <span style={{fontSize: '14px', color: '#64748B'}}>{talk.speaker}</span>
                      </div>
                      
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                        <Clock style={{width: '16px', height: '16px', color: '#94A3B8'}} />
                        <span style={{fontSize: '14px', color: '#64748B'}}>{talk.duration}</span>
                      </div>
                    </div>
                    
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                      <Badge variant="secondary" style={{fontSize: '12px'}}>
                        TED Talk
                      </Badge>
                      
                      <div style={{display: 'flex', alignItems: 'center', gap: '4px', color: '#94A3B8', fontSize: '13px'}}>
                        <Eye style={{width: '14px', height: '14px'}} />
                        <span>{talk.views} views</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default LearningBytes;