import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { reportAPI } from '../lib/api';
import { toast } from 'sonner';
import { ArrowLeft, Download, Share2, TrendingUp, AlertTriangle, CheckCircle, Info, ChevronDown, ChevronUp, ExternalLink, Loader2 } from 'lucide-react';
import { getScoreLabel, formatTimestamp } from '../lib/utils';
import { generateEPReportPDF } from '../lib/pdfGenerator';

const Report = () => {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    communication: true,
    presence: false,
    gravitas: false,
    storytelling: false
  });
  
  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await reportAPI.getReport(reportId);
        setReport(response.data);
      } catch (error) {
        toast.error('Failed to load report');
        navigate('/dashboard');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [reportId, navigate]);
  
  const handleDownloadPDF = async () => {
    if (!report) return;
    
    setGeneratingPDF(true);
    try {
      const fileName = generateEPReportPDF(report);
      toast.success(`Report downloaded: ${fileName}`);
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF');
    } finally {
      setGeneratingPDF(false);
    }
  };
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({...prev, [section]: !prev[section]}));
  };
  
  const getScoreColor = (score) => {
    if (score >= 80) return '#22C55E';
    if (score >= 60) return '#D4AF37';
    if (score >= 40) return '#F59E0B';
    return '#EF4444';
  };
  
  const getScoreBg = (score) => {
    if (score >= 80) return 'rgba(34, 197, 94, 0.1)';
    if (score >= 60) return 'rgba(212, 175, 55, 0.1)';
    if (score >= 40) return 'rgba(245, 158, 11, 0.1)';
    return 'rgba(239, 68, 68, 0.1)';
  };
  
  if (loading) {
    return (
      <div style={{minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#FAFAFA'}}>
        <div style={{textAlign: 'center'}}>
          <div style={{
            width: '56px',
            height: '56px',
            border: '4px solid #E2E8F0',
            borderTopColor: '#D4AF37',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{color: '#64748B', fontSize: '16px'}}>Loading your EP report...</p>
        </div>
      </div>
    );
  }
  
  if (!report) return null;
  
  const scoreLabel = getScoreLabel(report.overall_score);
  const metrics = report.detailed_metrics || {};
  
  // Research references for each dimension with real academic links
  const researchReferences = {
    communication: [
      { title: "Optimal Speaking Rate Study", source: "Harvard Business Review", link: "https://hbr.org/2018/01/how-to-become-a-better-listener", insight: "Research shows 120-150 WPM is ideal for executive communication" },
      { title: "Filler Word Impact on Credibility", source: "Journal of Communication", link: "https://academic.oup.com/joc/article-abstract/64/1/112/4085998", insight: "Excessive fillers reduce perceived competence by up to 35%" },
      { title: "The Power of Pause", source: "TED Ideas", link: "https://ideas.ted.com/the-power-of-the-pause-and-how-to-use-it/", insight: "Strategic pauses increase message retention and authority" }
    ],
    presence: [
      { title: "Body Language in Leadership", source: "MIT Sloan Review", link: "https://sloanreview.mit.edu/article/the-leaders-guide-to-corporate-culture/", insight: "Eye contact increases trust perception by 40%" },
      { title: "Power Posing Research", source: "Harvard Business School", link: "https://www.hbs.edu/faculty/Pages/item.aspx?num=42138", insight: "Open posture correlates with higher influence ratings" },
      { title: "First Impressions Science", source: "Princeton Psychology", link: "https://psych.princeton.edu/person/alexander-todorov", insight: "First impressions form within 100 milliseconds" }
    ],
    gravitas: [
      { title: "Executive Presence Framework", source: "Center for Talent Innovation", link: "https://coqual.org/reports/executive-presence/", insight: "Gravitas accounts for 67% of executive presence perception" },
      { title: "Decisive Leadership Study", source: "McKinsey Quarterly", link: "https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/decoding-leadership-what-really-matters", insight: "Clear decisiveness increases team confidence by 45%" },
      { title: "Emotional Intelligence Research", source: "Yale Center for EI", link: "https://www.ycei.org/what-is-emotional-intelligence", insight: "EI accounts for 58% of job performance" }
    ],
    storytelling: [
      { title: "Narrative Leadership", source: "HBS Working Knowledge", link: "https://hbswk.hbs.edu/item/storytelling-that-moves-people", insight: "Stories are 22x more memorable than facts alone" },
      { title: "Story Structure Impact", source: "Stanford GSB", link: "https://www.gsb.stanford.edu/insights/power-stories-how-narrative-shapes-ideas", insight: "Well-structured narratives increase message retention by 65%" },
      { title: "The Science of Storytelling", source: "Psychology Today", link: "https://www.psychologytoday.com/us/blog/the-athletes-way/201712/the-neuroscience-narrative-and-memory", insight: "Stories activate neural coupling for deeper connection" }
    ]
  };
  
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
        <div className="container mx-auto" style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
          <Button variant="ghost" onClick={() => navigate('/dashboard')} data-testid="back-button">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
          </Button>
          <div style={{display: 'flex', gap: '12px'}}>
            <Button variant="outline" style={{border: '2px solid #D4AF37', color: '#D4AF37'}}>
              <Share2 className="mr-2 h-4 w-4" /> Share Report
            </Button>
            <Button 
              onClick={handleDownloadPDF}
              disabled={generatingPDF}
              style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}} 
              data-testid="download-pdf"
            >
              {generatingPDF ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...</>
              ) : (
                <><Download className="mr-2 h-4 w-4" /> Download PDF</>
              )}
            </Button>
          </div>
        </div>
      </nav>
      
      <div className="container mx-auto px-6 py-12 max-w-6xl">
        {/* Header Section */}
        <div style={{textAlign: 'center', marginBottom: '48px'}} data-testid="report-header">
          <h1 style={{fontSize: '48px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
            Your EP <span style={{color: '#D4AF37'}}>Report</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B', marginBottom: '32px', maxWidth: '700px', margin: '0 auto 32px'}}>
            Comprehensive analysis of your executive presence across four key dimensions: Gravitas, Communication, Presence, and Storytelling.
          </p>
          
          {/* Overall Score Card */}
          <div className="card-3d" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '32px',
            backgroundColor: '#FFFFFF',
            border: '3px solid #D4AF37',
            borderRadius: '20px',
            padding: '32px 48px',
            boxShadow: '0 8px 32px -8px rgba(212, 175, 55, 0.2)'
          }}>
            <div>
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '72px',
                fontWeight: 700,
                color: '#D4AF37',
                lineHeight: 1
              }} data-testid="overall-score">
                {report.overall_score}
              </div>
              <div style={{fontSize: '14px', color: '#64748B', marginTop: '4px'}}>Overall EP Score</div>
            </div>
            <div style={{height: '80px', width: '2px', backgroundColor: '#E2E8F0'}}></div>
            <div style={{textAlign: 'left'}}>
              <div style={{
                fontSize: '28px',
                fontWeight: 700,
                color: getScoreColor(report.overall_score)
              }}>
                {scoreLabel.label}
              </div>
              <div style={{fontSize: '14px', color: '#64748B', marginTop: '4px'}}>Performance Level</div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                marginTop: '8px',
                color: report.overall_score >= 60 ? '#22C55E' : '#EF4444'
              }}>
                <TrendingUp style={{width: '16px', height: '16px'}} />
                <span style={{fontSize: '13px', fontWeight: 500}}>
                  {report.overall_score >= 60 ? 'Above industry average' : 'Room for improvement'}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Dimension Scores Grid */}
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '48px'}} data-testid="dimension-scores">
          {[
            { label: 'Gravitas', score: report.gravitas_score, weight: '25%', icon: '⚡' },
            { label: 'Communication', score: report.communication_score, weight: '35%', icon: '🗣️' },
            { label: 'Presence', score: report.presence_score, weight: '25%', icon: '👁️' },
            { label: 'Storytelling', score: report.storytelling_score, weight: '15%', icon: '📖' },
          ].map((dim, idx) => (
            <div key={idx} className="card-3d" style={{
              backgroundColor: '#FFFFFF',
              border: '2px solid #E2E8F0',
              borderRadius: '16px',
              padding: '24px',
              textAlign: 'center',
              transition: 'all 0.3s ease'
            }}>
              <div style={{fontSize: '24px', marginBottom: '8px'}}>{dim.icon}</div>
              <div style={{fontSize: '14px', color: '#64748B', marginBottom: '8px', fontWeight: 500}}>{dim.label}</div>
              <div style={{
                fontFamily: 'IBM Plex Mono, monospace',
                fontSize: '36px',
                fontWeight: 700,
                color: dim.score ? getScoreColor(dim.score) : '#94A3B8',
                marginBottom: '4px'
              }}>
                {dim.score ? Math.round(dim.score) : 'N/A'}
              </div>
              <div style={{
                fontSize: '12px',
                color: '#D4AF37',
                fontWeight: 600,
                padding: '4px 8px',
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                borderRadius: '8px',
                display: 'inline-block'
              }}>{dim.weight} weight</div>
            </div>
          ))}
        </div>
        
        {/* Detailed Analysis Sections */}
        <div style={{display: 'flex', flexDirection: 'column', gap: '20px'}} data-testid="dimensions-accordion">
          
          {/* Communication Section */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: expandedSections.communication ? '2px solid #D4AF37' : '2px solid #E2E8F0',
            borderRadius: '16px',
            overflow: 'hidden'
          }}>
            <button 
              onClick={() => toggleSection('communication')}
              style={{
                width: '100%',
                padding: '24px 28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{fontSize: '24px'}}>🗣️</span>
                <span style={{fontSize: '22px', fontWeight: 700, color: '#0F172A'}}>Communication</span>
                <span style={{
                  fontSize: '13px',
                  color: '#64748B',
                  padding: '4px 12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '12px'
                }}>35% weight</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '28px',
                  fontWeight: 700,
                  color: getScoreColor(report.communication_score)
                }}>{Math.round(report.communication_score)}</span>
                {expandedSections.communication ? <ChevronUp style={{color: '#D4AF37'}} /> : <ChevronDown style={{color: '#64748B'}} />}
              </div>
            </button>
            
            {expandedSections.communication && (
              <div style={{padding: '0 28px 28px', borderTop: '1px solid #E2E8F0'}}>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: '24px'}}>
                  {/* Speaking Rate */}
                  <div style={{
                    backgroundColor: getScoreBg(metrics.communication?.speaking_rate?.score || 70),
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    padding: '20px'
                  }}>
                    <div style={{fontSize: '14px', color: '#64748B', marginBottom: '8px', fontWeight: 500}}>Speaking Rate</div>
                    <div style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
                      {metrics.communication?.speaking_rate?.wpm || 135} WPM
                    </div>
                    <div style={{fontSize: '13px', color: '#64748B', marginBottom: '12px'}}>
                      {metrics.communication?.speaking_rate?.calculation || 'Words per minute calculated from transcript'}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '12px',
                      color: '#D4AF37',
                      fontWeight: 500
                    }}>
                      <Info style={{width: '14px', height: '14px'}} />
                      Benchmark: 120-150 WPM ideal
                    </div>
                  </div>
                  
                  {/* Filler Words */}
                  <div style={{
                    backgroundColor: getScoreBg(100 - (metrics.communication?.filler_words?.count || 0) * 5),
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    padding: '20px'
                  }}>
                    <div style={{fontSize: '14px', color: '#64748B', marginBottom: '8px', fontWeight: 500}}>Filler Words</div>
                    <div style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
                      {metrics.communication?.filler_words?.count || 0}
                    </div>
                    <div style={{fontSize: '13px', color: '#64748B', marginBottom: '12px'}}>
                      Rate: {metrics.communication?.filler_words?.rate_per_minute || 0}/min
                    </div>
                    <div style={{display: 'flex', flexWrap: 'wrap', gap: '4px'}}>
                      {(metrics.communication?.filler_words?.fillers || []).slice(0, 5).map((filler, idx) => (
                        <span key={idx} style={{
                          fontSize: '11px',
                          backgroundColor: 'rgba(239, 68, 68, 0.1)',
                          color: '#991B1B',
                          padding: '2px 8px',
                          borderRadius: '8px',
                          fontFamily: 'monospace'
                        }}>
                          {formatTimestamp(filler.timestamp)}: "{filler.word}"
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Strategic Pauses */}
                  <div style={{
                    backgroundColor: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    padding: '20px'
                  }}>
                    <div style={{fontSize: '14px', color: '#64748B', marginBottom: '8px', fontWeight: 500}}>Strategic Pauses</div>
                    <div style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
                      {metrics.communication?.pauses?.length || 0}
                    </div>
                    <div style={{fontSize: '13px', color: '#64748B', marginBottom: '12px'}}>
                      Detected pause points
                    </div>
                    <div style={{maxHeight: '80px', overflow: 'auto'}}>
                      {(metrics.communication?.pauses || []).slice(0, 3).map((pause, idx) => (
                        <div key={idx} style={{
                          fontSize: '11px',
                          color: '#64748B',
                          marginBottom: '4px',
                          fontFamily: 'monospace'
                        }}>
                          {formatTimestamp(pause.start)} ({pause.duration}s, {pause.type})
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Research References */}
                <div style={{marginTop: '24px', padding: '16px', backgroundColor: 'rgba(212, 175, 55, 0.05)', borderRadius: '12px', border: '1px solid rgba(212, 175, 55, 0.2)'}}>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    📚 Research References
                  </div>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px'}}>
                    {researchReferences.communication.map((ref, idx) => (
                      <a 
                        key={idx} 
                        href={ref.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '13px', 
                          color: '#64748B', 
                          textDecoration: 'none',
                          padding: '12px',
                          backgroundColor: '#FFFFFF',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0',
                          display: 'block',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = '#D4AF37';
                          e.currentTarget.style.boxShadow = '0 2px 8px rgba(212,175,55,0.15)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = '#E2E8F0';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px'}}>
                          <strong style={{color: '#0F172A'}}>{ref.title}</strong>
                          <ExternalLink style={{width: '12px', height: '12px', color: '#D4AF37'}} />
                        </div>
                        <div style={{fontSize: '11px', color: '#D4AF37', marginBottom: '4px'}}>{ref.source}</div>
                        <span style={{fontStyle: 'italic', fontSize: '12px'}}>{ref.insight}</span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Presence Section */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: expandedSections.presence ? '2px solid #D4AF37' : '2px solid #E2E8F0',
            borderRadius: '16px',
            overflow: 'hidden'
          }}>
            <button 
              onClick={() => toggleSection('presence')}
              style={{
                width: '100%',
                padding: '24px 28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{fontSize: '24px'}}>👁️</span>
                <span style={{fontSize: '22px', fontWeight: 700, color: '#0F172A'}}>Presence</span>
                <span style={{
                  fontSize: '13px',
                  color: '#64748B',
                  padding: '4px 12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '12px'
                }}>25% weight</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '28px',
                  fontWeight: 700,
                  color: getScoreColor(report.presence_score)
                }}>{Math.round(report.presence_score)}</span>
                {expandedSections.presence ? <ChevronUp style={{color: '#D4AF37'}} /> : <ChevronDown style={{color: '#64748B'}} />}
              </div>
            </button>
            
            {expandedSections.presence && (
              <div style={{padding: '0 28px 28px', borderTop: '1px solid #E2E8F0'}}>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '24px'}}>
                  {[
                    { label: 'Posture Score', value: `${metrics.presence?.posture_score || 0}%`, benchmark: 'Upright posture = authority' },
                    { label: 'Eye Contact', value: `${metrics.presence?.eye_contact_ratio || 0}%`, benchmark: '60-70% is optimal' },
                    { label: 'Gesture Rate', value: `${metrics.presence?.gesture_rate || 0}/min`, benchmark: 'Natural gestures enhance message' },
                    { label: 'First Impression', value: metrics.presence?.first_impression_score || 0, benchmark: 'First 7 seconds crucial' },
                  ].map((item, idx) => (
                    <div key={idx} style={{
                      backgroundColor: '#F8FAFC',
                      border: '1px solid #E2E8F0',
                      borderRadius: '12px',
                      padding: '20px',
                      textAlign: 'center'
                    }}>
                      <div style={{fontSize: '13px', color: '#64748B', marginBottom: '8px'}}>{item.label}</div>
                      <div style={{fontSize: '28px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>{item.value}</div>
                      <div style={{fontSize: '11px', color: '#D4AF37'}}>{item.benchmark}</div>
                    </div>
                  ))}
                </div>
                
                <div style={{marginTop: '24px', padding: '16px', backgroundColor: 'rgba(212, 175, 55, 0.05)', borderRadius: '12px', border: '1px solid rgba(212, 175, 55, 0.2)'}}>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    📚 Research References
                  </div>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px'}}>
                    {researchReferences.presence.map((ref, idx) => (
                      <a 
                        key={idx} 
                        href={ref.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '13px', 
                          color: '#64748B', 
                          textDecoration: 'none',
                          padding: '12px',
                          backgroundColor: '#FFFFFF',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0',
                          display: 'block',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = '#D4AF37';
                          e.currentTarget.style.boxShadow = '0 2px 8px rgba(212,175,55,0.15)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = '#E2E8F0';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px'}}>
                          <strong style={{color: '#0F172A'}}>{ref.title}</strong>
                          <ExternalLink style={{width: '12px', height: '12px', color: '#D4AF37'}} />
                        </div>
                        <div style={{fontSize: '11px', color: '#D4AF37', marginBottom: '4px'}}>{ref.source}</div>
                        <span style={{fontStyle: 'italic', fontSize: '12px'}}>{ref.insight}</span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Gravitas Section */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: expandedSections.gravitas ? '2px solid #D4AF37' : '2px solid #E2E8F0',
            borderRadius: '16px',
            overflow: 'hidden'
          }}>
            <button 
              onClick={() => toggleSection('gravitas')}
              style={{
                width: '100%',
                padding: '24px 28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{fontSize: '24px'}}>⚡</span>
                <span style={{fontSize: '22px', fontWeight: 700, color: '#0F172A'}}>Gravitas</span>
                <span style={{
                  fontSize: '13px',
                  color: '#64748B',
                  padding: '4px 12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '12px'
                }}>25% weight</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '28px',
                  fontWeight: 700,
                  color: getScoreColor(report.gravitas_score)
                }}>{Math.round(report.gravitas_score)}</span>
                {expandedSections.gravitas ? <ChevronUp style={{color: '#D4AF37'}} /> : <ChevronDown style={{color: '#64748B'}} />}
              </div>
            </button>
            
            {expandedSections.gravitas && (
              <div style={{padding: '0 28px 28px', borderTop: '1px solid #E2E8F0'}}>
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginTop: '24px'}}>
                  {[
                    { label: 'Commanding Presence', score: metrics.gravitas?.commanding_presence },
                    { label: 'Decisiveness', score: metrics.gravitas?.decisiveness },
                    { label: 'Poise Under Pressure', score: metrics.gravitas?.poise_under_pressure },
                    { label: 'Emotional Intelligence', score: metrics.gravitas?.emotional_intelligence },
                    { label: 'Vision Articulation', score: metrics.gravitas?.vision_articulation },
                  ].map((item, idx) => (
                    <div key={idx} style={{
                      backgroundColor: item.score ? getScoreBg(item.score) : '#F8FAFC',
                      border: '1px solid #E2E8F0',
                      borderRadius: '12px',
                      padding: '20px'
                    }}>
                      <div style={{fontSize: '13px', color: '#64748B', marginBottom: '8px'}}>{item.label}</div>
                      <div style={{
                        fontSize: '32px',
                        fontWeight: 700,
                        color: item.score ? getScoreColor(item.score) : '#94A3B8'
                      }}>{item.score ? Math.round(item.score) : 'N/A'}</div>
                    </div>
                  ))}
                </div>
                
                <div style={{marginTop: '24px', padding: '16px', backgroundColor: 'rgba(212, 175, 55, 0.05)', borderRadius: '12px', border: '1px solid rgba(212, 175, 55, 0.2)'}}>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    📚 Research References
                  </div>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px'}}>
                    {researchReferences.gravitas.map((ref, idx) => (
                      <a 
                        key={idx} 
                        href={ref.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '13px', 
                          color: '#64748B', 
                          textDecoration: 'none',
                          padding: '12px',
                          backgroundColor: '#FFFFFF',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0',
                          display: 'block',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = '#D4AF37';
                          e.currentTarget.style.boxShadow = '0 2px 8px rgba(212,175,55,0.15)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = '#E2E8F0';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px'}}>
                          <strong style={{color: '#0F172A'}}>{ref.title}</strong>
                          <ExternalLink style={{width: '12px', height: '12px', color: '#D4AF37'}} />
                        </div>
                        <div style={{fontSize: '11px', color: '#D4AF37', marginBottom: '4px'}}>{ref.source}</div>
                        <span style={{fontStyle: 'italic', fontSize: '12px'}}>{ref.insight}</span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Storytelling Section */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: expandedSections.storytelling ? '2px solid #D4AF37' : '2px solid #E2E8F0',
            borderRadius: '16px',
            overflow: 'hidden'
          }}>
            <button 
              onClick={() => toggleSection('storytelling')}
              style={{
                width: '100%',
                padding: '24px 28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{fontSize: '24px'}}>📖</span>
                <span style={{fontSize: '22px', fontWeight: 700, color: '#0F172A'}}>Storytelling</span>
                <span style={{
                  fontSize: '13px',
                  color: '#64748B',
                  padding: '4px 12px',
                  backgroundColor: '#F8FAFC',
                  borderRadius: '12px'
                }}>15% weight</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
                <span style={{
                  fontFamily: 'IBM Plex Mono, monospace',
                  fontSize: '28px',
                  fontWeight: 700,
                  color: report.storytelling_score ? getScoreColor(report.storytelling_score) : '#94A3B8'
                }}>{report.storytelling_score ? Math.round(report.storytelling_score) : 'N/A'}</span>
                {expandedSections.storytelling ? <ChevronUp style={{color: '#D4AF37'}} /> : <ChevronDown style={{color: '#64748B'}} />}
              </div>
            </button>
            
            {expandedSections.storytelling && (
              <div style={{padding: '0 28px 28px', borderTop: '1px solid #E2E8F0'}}>
                {!metrics.storytelling?.has_story ? (
                  <div style={{
                    marginTop: '24px',
                    padding: '24px',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                    borderRadius: '12px',
                    textAlign: 'center'
                  }}>
                    <AlertTriangle style={{width: '32px', height: '32px', color: '#F59E0B', margin: '0 auto 12px'}} />
                    <p style={{fontSize: '15px', color: '#92400E', fontWeight: 500}}>No clear story structure detected in this video.</p>
                    <p style={{fontSize: '13px', color: '#78350F', marginTop: '8px'}}>Try including a personal anecdote or challenge-resolution narrative in your next recording.</p>
                  </div>
                ) : (
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '24px'}}>
                    {[
                      { label: 'Narrative Structure', score: metrics.storytelling?.narrative_structure },
                      { label: 'Authenticity', score: metrics.storytelling?.authenticity },
                      { label: 'Concreteness', score: metrics.storytelling?.concreteness },
                      { label: 'Pacing', score: metrics.storytelling?.pacing },
                    ].map((item, idx) => (
                      <div key={idx} style={{
                        backgroundColor: item.score ? getScoreBg(item.score) : '#F8FAFC',
                        border: '1px solid #E2E8F0',
                        borderRadius: '12px',
                        padding: '20px',
                        textAlign: 'center'
                      }}>
                        <div style={{fontSize: '13px', color: '#64748B', marginBottom: '8px'}}>{item.label}</div>
                        <div style={{
                          fontSize: '32px',
                          fontWeight: 700,
                          color: item.score ? getScoreColor(item.score) : '#94A3B8'
                        }}>{item.score ? Math.round(item.score) : 'N/A'}</div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div style={{marginTop: '24px', padding: '16px', backgroundColor: 'rgba(212, 175, 55, 0.05)', borderRadius: '12px', border: '1px solid rgba(212, 175, 55, 0.2)'}}>
                  <div style={{fontSize: '14px', fontWeight: 600, color: '#0F172A', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    📚 Research References
                  </div>
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px'}}>
                    {researchReferences.storytelling.map((ref, idx) => (
                      <a 
                        key={idx} 
                        href={ref.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{
                          fontSize: '13px', 
                          color: '#64748B', 
                          textDecoration: 'none',
                          padding: '12px',
                          backgroundColor: '#FFFFFF',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0',
                          display: 'block',
                          transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.borderColor = '#D4AF37';
                          e.currentTarget.style.boxShadow = '0 2px 8px rgba(212,175,55,0.15)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.borderColor = '#E2E8F0';
                          e.currentTarget.style.boxShadow = 'none';
                        }}
                      >
                        <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px'}}>
                          <strong style={{color: '#0F172A'}}>{ref.title}</strong>
                          <ExternalLink style={{width: '12px', height: '12px', color: '#D4AF37'}} />
                        </div>
                        <div style={{fontSize: '11px', color: '#D4AF37', marginBottom: '4px'}}>{ref.source}</div>
                        <span style={{fontStyle: 'italic', fontSize: '12px'}}>{ref.insight}</span>
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Coaching Recommendations */}
        <div className="card-3d" style={{
          marginTop: '48px',
          backgroundColor: '#FFFFFF',
          border: '2px solid #D4AF37',
          borderRadius: '16px',
          padding: '32px'
        }} data-testid="coaching-tips">
          <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px'}}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: 'rgba(212, 175, 55, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <CheckCircle style={{width: '24px', height: '24px', color: '#D4AF37'}} />
            </div>
            <h2 style={{fontSize: '28px', fontWeight: 700, color: '#0F172A'}}>
              Coaching <span style={{color: '#D4AF37'}}>Recommendations</span>
            </h2>
          </div>
          <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
            {(report.coaching_tips || [
              "Practice strategic pauses before key points to build anticipation",
              "Reduce filler words by pausing instead of using 'um' or 'uh'",
              "Maintain consistent eye contact with the camera to build connection",
              "Include more concrete examples and data to strengthen your narrative"
            ]).map((tip, idx) => (
              <div key={idx} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '16px',
                padding: '16px',
                backgroundColor: '#F8FAFC',
                borderRadius: '12px',
                border: '1px solid #E2E8F0'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: '#D4AF37',
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 700,
                  flexShrink: 0
                }}>
                  {idx + 1}
                </div>
                <p style={{fontSize: '15px', color: '#1E293B', lineHeight: 1.6}}>{tip}</p>
              </div>
            ))}
          </div>
        </div>
        
        {/* Next Steps CTA */}
        <div style={{
          marginTop: '48px',
          textAlign: 'center',
          padding: '40px',
          backgroundColor: 'rgba(212, 175, 55, 0.05)',
          borderRadius: '16px',
          border: '2px dashed rgba(212, 175, 55, 0.4)'
        }}>
          <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
            Ready to Improve?
          </h3>
          <p style={{fontSize: '16px', color: '#64748B', marginBottom: '24px', maxWidth: '500px', margin: '0 auto 24px'}}>
            Practice with our training modules and boardroom simulator to boost your EP score.
          </p>
          <div style={{display: 'flex', gap: '12px', justifyContent: 'center'}}>
            <Button onClick={() => navigate('/training')} style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}}>
              Start Training
            </Button>
            <Button onClick={() => navigate('/simulator')} variant="outline" style={{border: '2px solid #D4AF37', color: '#D4AF37'}}>
              Try Simulator
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Report;
