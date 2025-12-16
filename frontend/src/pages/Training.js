import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { 
  BookOpen, GraduationCap, RotateCw, 
  Clock, TrendingUp, Star, Zap, Calendar,
  Play, FileText, Target
} from 'lucide-react';
import { api } from '../lib/api';

const Training = () => {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [rotationInfo, setRotationInfo] = useState(null);
  const [weekTheme, setWeekTheme] = useState('');
  const [weekNumber, setWeekNumber] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);
  const [moduleContent, setModuleContent] = useState('');
  
  const fetchModules = async () => {
    try {
      // Fetch training modules
      const modulesResponse = await api.get('/training/modules');
      
      const data = modulesResponse.data;
      setModules(data.modules || []);
      setRotationInfo(data.rotation_info);
      setWeekTheme(data.week_theme || "Executive Communication Fundamentals");
      setWeekNumber(data.week_number || 1);
    } catch (error) {
      console.error('Error fetching modules:', error);
      toast.error('Failed to load training modules');
    } finally {
      setLoading(false);
    }
  };
  
  const loadModule = async (module) => {
    setSelectedModule(module);
    setLoadingContent(true);
    
    try {
      const token = localStorage.getItem('session_token');
      
      // Fetch module content (in a real app, this would fetch actual content)
      // For now, we'll simulate loading content
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockContent = {
        content: `# ${module.title}

## Key Principles

In this module, you'll learn:

- Core communication techniques for executive presence
- Strategies to command attention and build credibility
- Methods to articulate vision and inspire teams

## Module Overview

${module.description}

## Learning Objectives

By the end of this module, you will be able to:

1. Demonstrate confident body language and vocal presence
2. Structure communications for maximum impact
3. Adapt your communication style to different audiences
4. Deliver compelling presentations that drive action

## Practice Exercises

1. **Voice Projection Exercise** - Practice projecting your voice clearly across different room sizes
2. **Pause Power** - Learn to use strategic pauses for emphasis and clarity
3. **Storytelling Framework** - Apply a structured approach to executive storytelling

## Key Takeaways

- Executive presence is built through consistent practice of fundamental skills
- Confidence comes from preparation and authentic communication
- Great leaders adapt their communication style to their audience while staying true to their authentic voice`
      };
      
      setModuleContent(mockContent.content);
    } catch (error) {
      console.error('Error loading module:', error);
      toast.error('Failed to load module content');
    } finally {
      setLoadingContent(false);
    }
  };
  
  useEffect(() => {
    fetchModules();
    
    // Update every minute
    const interval = setInterval(() => {
      fetchModules();
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
          <p style={{color: '#64748B'}}>Loading training modules...</p>
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
              <GraduationCap style={{display: 'inline', width: '28px', height: '28px', color: '#D4AF37', marginRight: '8px'}} />
              Training <span style={{color: '#D4AF37'}}>Modules</span>
            </h1>
            
            <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
              <Badge variant="outline" style={{borderColor: '#D4AF37', color: '#D4AF37', fontWeight: 600}}>
                <RotateCw style={{width: '14px', height: '14px', marginRight: '6px'}} />
                Rotates in {rotationInfo?.remaining_formatted || '5d 14h 32m'}
              </Badge>
              
              <Button 
                variant="outline" 
                onClick={fetchModules}
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
              <h2 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A'}}>Week {weekNumber}: {weekTheme}</h2>
            </div>
            <p style={{color: '#64748B', fontSize: '15px', lineHeight: 1.6}}>
              Structured learning modules to develop your executive presence skills. New modules rotate weekly.
            </p>
          </div>
        </div>
      </nav>
      
      <div className="container mx-auto px-6 py-8">
        {selectedModule ? (
          <div>
            <div style={{marginBottom: '24px'}}>
              <Button 
                variant="outline" 
                onClick={() => setSelectedModule(null)}
                style={{borderColor: '#E2E8F0', color: '#64748B', marginBottom: '16px'}}
              >
                ← Back to Modules
              </Button>
              
              <Card style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '16px',
                border: '1px solid #E2E8F0',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)'
              }}>
                <CardHeader style={{borderBottom: '1px solid #F1F5F9'}}>
                  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                    <CardTitle style={{fontSize: '24px', color: '#0F172A'}}>
                      {selectedModule.title}
                    </CardTitle>
                    <Badge style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}>
                      {selectedModule.focus_area}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent style={{padding: '24px'}}>
                  {loadingContent ? (
                    <div style={{textAlign: 'center', padding: '48px'}}>
                      <div style={{
                        width: '48px', height: '48px',
                        border: '4px solid #E2E8F0', borderTopColor: '#D4AF37',
                        borderRadius: '50%', animation: 'spin 1s linear infinite',
                        margin: '0 auto 16px'
                      }}></div>
                      <p style={{color: '#64748B'}}>Loading module content...</p>
                    </div>
                  ) : (
                    <div style={{lineHeight: 1.7}}>
                      {moduleContent.split('\n\n').map((paragraph, index) => {
                        if (paragraph.startsWith('# ')) {
                          return <h1 key={index} style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '24px'}}>{paragraph.substring(2)}</h1>;
                        } else if (paragraph.startsWith('## ')) {
                          return <h2 key={index} style={{fontSize: '22px', fontWeight: 600, color: '#0F172A', marginTop: '32px', marginBottom: '16px'}}>{paragraph.substring(3)}</h2>;
                        } else if (paragraph.startsWith('### ')) {
                          return <h3 key={index} style={{fontSize: '18px', fontWeight: 600, color: '#0F172A', marginTop: '24px', marginBottom: '12px'}}>{paragraph.substring(4)}</h3>;
                        } else if (paragraph.startsWith('- ')) {
                          return (
                            <ul key={index} style={{marginBottom: '16px', paddingLeft: '20px'}}>
                              {paragraph.split('\n').map((item, i) => (
                                <li key={i} style={{marginBottom: '8px'}}>{item.substring(2)}</li>
                              ))}
                            </ul>
                          );
                        } else {
                          return <p key={index} style={{marginBottom: '16px', color: '#334155'}}>{paragraph}</p>;
                        }
                      })}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px'}}>
            {modules.map((module) => {
              const diffColors = {
                Beginner: { bg: '#DCFCE7', text: '#166534', border: '#86EFAC' },
                Intermediate: { bg: '#FEF3C7', text: '#92400E', border: '#FDE68A' },
                Advanced: { bg: '#FEE2E2', text: '#B91C1C', border: '#FCA5A5' }
              }[module.difficulty] || { bg: '#F3F4F6', text: '#374151', border: '#D1D5DB' };
              
              return (
                <div 
                  key={module.id} 
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '16px',
                    border: '1px solid #E2E8F0',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
                    overflow: 'hidden',
                    transition: 'all 0.2s ease',
                    cursor: 'pointer',
                    position: 'relative'
                  }}
                  onClick={() => loadModule(module)}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                  <div style={{padding: '24px'}}>
                    <div style={{display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px'}}>
                      <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>{module.title}</h3>
                      <span style={{
                        backgroundColor: diffColors.bg, color: diffColors.text,
                        border: `1px solid ${diffColors.border}`,
                        padding: '4px 10px', borderRadius: '8px',
                        fontSize: '12px', fontWeight: 600
                      }}>{module.difficulty}</span>
                    </div>
                    
                    <p style={{fontSize: '14px', color: '#64748B', marginBottom: '16px', lineHeight: 1.6}}>{module.description}</p>
                    
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '16px', borderTop: '1px solid #E2E8F0'}}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '4px', color: '#94A3B8'}}>
                        <Clock style={{width: '16px', height: '16px'}} />
                        <span style={{fontSize: '13px'}}>{module.duration}</span>
                      </div>
                      
                      <div style={{display: 'flex', alignItems: 'center', gap: '4px', color: '#94A3B8'}}>
                        <Target style={{width: '16px', height: '16px'}} />
                        <span style={{fontSize: '13px'}}>{module.focus_area}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Training;