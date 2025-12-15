import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, BookOpen, Clock, Target, Play, Timer, Calendar } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Training = () => {
  const navigate = useNavigate();
  const [modules, setModules] = useState([]);
  const [selectedModule, setSelectedModule] = useState(null);
  const [moduleContent, setModuleContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingContent, setLoadingContent] = useState(false);
  const [rotationInfo, setRotationInfo] = useState(null);
  const [weekTheme, setWeekTheme] = useState('');
  const [weekNumber, setWeekNumber] = useState(1);
  
  useEffect(() => {
    fetchModules();
    
    // Update countdown every minute
    const interval = setInterval(() => {
      fetchModules();
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  const fetchModules = async () => {
    try {
      // Use mock data instead of actual API calls
      const mockModules = [
        {
          id: "module_1",
          title: "Mastering Vocal Authority",
          description: "Learn techniques to project confidence through your voice, including pace, tone, and strategic pauses.",
          focus_area: "Communication",
          duration: "12 min read",
          difficulty: "Beginner"
        },
        {
          id: "module_2",
          title: "Commanding Physical Presence",
          description: "Develop your body language toolkit with posture, gestures, and spatial awareness techniques.",
          focus_area: "Presence",
          duration: "15 min read",
          difficulty: "Intermediate"
        },
        {
          id: "module_3",
          title: "Strategic Storytelling Framework",
          description: "Craft compelling narratives that drive action and create emotional connections with stakeholders.",
          focus_area: "Storytelling",
          duration: "18 min read",
          difficulty: "Advanced"
        }
      ];
      
      setModules(mockModules);
      setRotationInfo({
        next_rotation: new Date(Date.now() + 604800000).toISOString()
      });
      setWeekTheme("Executive Communication Fundamentals");
      setWeekNumber(3);
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
      // Use mock data instead of actual API calls
      const mockContent = {
        content: `# ${module.title}

## Key Principles

In this module, you'll learn:

1. **Core Techniques**: Evidence-based strategies to enhance your ${module.focus_area.toLowerCase()}
2. **Real-world Applications**: Case studies from Fortune 500 executives
3. **Practice Exercises**: Actionable drills you can implement immediately

## Module Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

## Key Takeaways

- Point 1: Essential insight for developing executive presence
- Point 2: Practical technique you can apply today
- Point 3: Advanced strategy for seasoned leaders

## Practice Exercise

Take 5 minutes to:

1. Reflect on a recent challenging communication scenario
2. Identify one area for improvement
3. Commit to implementing one specific technique this week

Remember: Executive presence is developed through consistent, deliberate practice.`
      };
      
      setModuleContent(mockContent);
    } catch (error) {
      console.error('Error loading module:', error);
      toast.error('Failed to load module content');
    } finally {
      setLoadingContent(false);
    }
  };
  
  const getFocusAreaColor = (focusArea) => {
    switch(focusArea) {
      case 'Communication': return { bg: 'rgba(212, 175, 55, 0.15)', text: '#92400E', border: 'rgba(212, 175, 55, 0.4)' };
      case 'Presence': return { bg: 'rgba(34, 197, 94, 0.15)', text: '#166534', border: 'rgba(34, 197, 94, 0.4)' };
      case 'Gravitas': return { bg: 'rgba(139, 92, 246, 0.15)', text: '#5B21B6', border: 'rgba(139, 92, 246, 0.4)' };
      case 'Storytelling': return { bg: 'rgba(245, 158, 11, 0.15)', text: '#92400E', border: 'rgba(245, 158, 11, 0.4)' };
      default: return { bg: '#F1F5F9', text: '#64748B', border: '#E2E8F0' };
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
          <p style={{color: '#64748B'}}>Loading modules...</p>
        </div>
      </div>
    );
  }
  
  if (selectedModule) {
    return (
      <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
        <nav style={{
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          padding: '16px 24px',
          position: 'sticky', top: 0, zIndex: 50
        }}>
          <Button variant="ghost" onClick={() => { setSelectedModule(null); setModuleContent(null); }}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Modules
          </Button>
        </nav>
        
        <div className="container mx-auto px-6 py-12 max-w-4xl">
          <div style={{marginBottom: '32px'}}>
            <div style={{
              display: 'inline-block', padding: '6px 16px',
              backgroundColor: getFocusAreaColor(selectedModule.focus_area).bg,
              color: getFocusAreaColor(selectedModule.focus_area).text,
              borderRadius: '20px', fontSize: '13px', fontWeight: 600, marginBottom: '16px',
              border: `1px solid ${getFocusAreaColor(selectedModule.focus_area).border}`
            }}>{selectedModule.focus_area}</div>
            
            <h1 style={{fontSize: '36px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
              {selectedModule.title}
            </h1>
            <p style={{fontSize: '18px', color: '#64748B', marginBottom: '24px'}}>{selectedModule.description}</p>
            
            <div style={{display: 'flex', gap: '16px', alignItems: 'center'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                <Clock style={{width: '18px', height: '18px', color: '#D4AF37'}} />
                <span style={{fontSize: '14px', color: '#64748B'}}>{selectedModule.duration}</span>
              </div>
              <div style={{
                padding: '4px 12px',
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                border: '1px solid rgba(212, 175, 55, 0.3)',
                borderRadius: '12px', fontSize: '13px', color: '#92400E', fontWeight: 500
              }}>{selectedModule.difficulty}</div>
            </div>
          </div>
          
          {loadingContent ? (
            <div style={{textAlign: 'center', padding: '60px 0'}}>
              <div style={{
                width: '48px', height: '48px',
                border: '4px solid #E2E8F0', borderTopColor: '#D4AF37',
                borderRadius: '50%', animation: 'spin 1s linear infinite',
                margin: '0 auto 16px'
              }}></div>
              <p style={{color: '#64748B'}}>Generating personalized content...</p>
            </div>
          ) : moduleContent && (
            <div>
              <div className="card-3d" style={{
                backgroundColor: '#FFFFFF',
                border: '2px solid #E2E8F0',
                borderRadius: '16px', padding: '32px', marginBottom: '32px'
              }}>
                <div style={{fontSize: '15px', lineHeight: 1.8, color: '#1E293B', whiteSpace: 'pre-line'}}>
                  {moduleContent.content}
                </div>
              </div>
              
              <div className="card-3d" style={{
                backgroundColor: 'rgba(212, 175, 55, 0.05)',
                border: '2px solid #D4AF37',
                borderRadius: '16px', padding: '24px', marginBottom: '32px'
              }}>
                <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
                  Ready to Practice?
                </h3>
                <p style={{fontSize: '15px', color: '#64748B', marginBottom: '16px'}}>
                  Apply what you've learned by recording a practice video. Get instant AI feedback on your technique.
                </p>
                <Button onClick={() => navigate('/dashboard')} style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}>
                  <Play className="mr-2 h-4 w-4" /> Start Practice Recording
                </Button>
              </div>
              
              <div style={{textAlign: 'center'}}>
                <Button variant="outline" onClick={() => { setSelectedModule(null); setModuleContent(null); }}
                  style={{border: '2px solid #D4AF37', color: '#D4AF37'}}>
                  Complete Module
                </Button>
              </div>
            </div>
          )}
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
            Training <span style={{color: '#D4AF37'}}>Modules</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B'}}>
            Structured micro-courses with AI-generated content tailored to your profile
          </p>
        </div>
        
        {/* Current Week Theme Banner */}
        {weekTheme && (
          <div className="card-3d" style={{
            backgroundColor: 'rgba(212, 175, 55, 0.05)',
            border: '2px solid #D4AF37',
            borderRadius: '16px', padding: '24px', marginBottom: '32px',
            display: 'flex', alignItems: 'center', gap: '20px'
          }}>
            <div style={{
              width: '60px', height: '60px', borderRadius: '16px',
              backgroundColor: '#D4AF37',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <BookOpen style={{width: '30px', height: '30px', color: '#FFFFFF'}} />
            </div>
            <div>
              <h2 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '4px'}}>
                This Week's Focus: <span style={{color: '#D4AF37'}}>{weekTheme}</span>
              </h2>
              <p style={{fontSize: '15px', color: '#64748B'}}>
                Complete all {modules.length} modules this week to master {weekTheme.toLowerCase()}
              </p>
            </div>
          </div>
        )}
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px'}}>
          {modules.map((module, idx) => {
            const colors = getFocusAreaColor(module.focus_area);
            return (
              <div
                key={module.id}
                className="card-3d"
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '2px solid #E2E8F0',
                  borderRadius: '16px', padding: '24px',
                  cursor: 'pointer', transition: 'all 0.3s ease',
                  position: 'relative', overflow: 'hidden'
                }}
                onClick={() => loadModule(module)}
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
                {/* Module Number Badge */}
                <div style={{
                  position: 'absolute', top: '16px', right: '16px',
                  width: '32px', height: '32px', borderRadius: '50%',
                  backgroundColor: '#D4AF37', color: '#FFFFFF',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '14px', fontWeight: 700
                }}>
                  {idx + 1}
                </div>
                
                <div style={{
                  display: 'inline-block', padding: '4px 12px',
                  backgroundColor: colors.bg, color: colors.text,
                  borderRadius: '12px', fontSize: '12px', fontWeight: 600, marginBottom: '12px',
                  border: `1px solid ${colors.border}`
                }}>{module.focus_area}</div>
                
                <h3 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A', marginBottom: '8px', paddingRight: '40px'}}>
                  {module.title}
                </h3>
                <p style={{fontSize: '14px', color: '#64748B', marginBottom: '16px', lineHeight: 1.6}}>
                  {module.description}
                </p>
                
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  paddingTop: '16px', borderTop: '1px solid #E2E8F0'
                }}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                    <Clock style={{width: '16px', height: '16px', color: '#D4AF37'}} />
                    <span style={{fontSize: '13px', color: '#64748B'}}>{module.duration}</span>
                  </div>
                  <span style={{
                    fontSize: '12px', color: '#92400E',
                    padding: '4px 10px',
                    backgroundColor: 'rgba(212, 175, 55, 0.1)',
                    borderRadius: '8px', fontWeight: 500
                  }}>{module.difficulty}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Training;
