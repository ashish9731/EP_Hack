import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { authAPI, reportAPI, subscriptionAPI } from '../lib/api';
import { toast } from 'sonner';
import { 
  Video, BookOpen, Dumbbell, Users, LogOut, BarChart3, HelpCircle, 
  TrendingUp, TrendingDown, Filter, Calendar, ChevronDown, RefreshCw,
  Target, Award, Zap, MessageSquare
} from 'lucide-react';
import ProfileModal from '../components/ProfileModal';
import axios from 'axios';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart
} from 'recharts';

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [hasProfile, setHasProfile] = useState(true);
  const [dateFilter, setDateFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);
  const [subscription, setSubscription] = useState(null);
  
  const COLORS = {
    gold: '#D4AF37',
    gravitas: '#8B5CF6',
    communication: '#D4AF37',
    presence: '#22C55E',
    storytelling: '#F59E0B',
    overall: '#0F172A'
  };
  
  useEffect(() => {
    checkSubscription();
    fetchData();
  }, []);

  const checkSubscription = async () => {
    try {
      const response = await subscriptionAPI.getStatus();
      setSubscription(response.data);
      
      // Redirect to pricing if first time user on free trial
      const hasSeenPricing = localStorage.getItem('has_seen_pricing');
      if (!hasSeenPricing && response.data.tier === 'free' && !response.data.is_whitelisted) {
        localStorage.setItem('has_seen_pricing', 'true');
        setTimeout(() => navigate('/pricing'), 1000);
      }
      
      // Show upgrade prompt if trial expired
      if (response.data.status === 'expired') {
        toast.error('Your trial has expired. Please upgrade to continue.', {
          duration: 5000,
          action: {
            label: 'Upgrade',
            onClick: () => navigate('/pricing')
          }
        });
      }
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
  };
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      const [userRes, reportsRes, profileRes] = await Promise.all([
        authAPI.getMe(),
        reportAPI.listReports(),
        axios.get(`${API_URL}/api/profile/`, {
          headers: { 'Authorization': `Bearer ${token}` },
          withCredentials: true
        })
      ]);
      
      setUser(userRes.data);
      setReports(reportsRes.data.reports || []);
      
      if (!profileRes.data.has_profile) {
        setHasProfile(false);
        setShowProfileModal(true);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    toast.success('Dashboard refreshed');
  };
  
  const handleLogout = async () => {
    try {
      await authAPI.logout();
      toast.success('Logged out successfully');
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };
  
  // Filter reports by date
  const filteredReports = useMemo(() => {
    if (dateFilter === 'all') return reports;
    
    const now = new Date();
    const filterDate = new Date();
    
    switch (dateFilter) {
      case '7days':
        filterDate.setDate(now.getDate() - 7);
        break;
      case '30days':
        filterDate.setDate(now.getDate() - 30);
        break;
      case '90days':
        filterDate.setDate(now.getDate() - 90);
        break;
      default:
        return reports;
    }
    
    return reports.filter(r => new Date(r.created_at) >= filterDate);
  }, [reports, dateFilter]);
  
  // Calculate analytics
  const analytics = useMemo(() => {
    if (filteredReports.length === 0) return null;
    
    const latest = filteredReports[0];
    const previous = filteredReports[1];
    
    const avgOverall = filteredReports.reduce((sum, r) => sum + r.overall_score, 0) / filteredReports.length;
    const avgGravitas = filteredReports.reduce((sum, r) => sum + (r.gravitas_score || 0), 0) / filteredReports.length;
    const avgCommunication = filteredReports.reduce((sum, r) => sum + (r.communication_score || 0), 0) / filteredReports.length;
    const avgPresence = filteredReports.reduce((sum, r) => sum + (r.presence_score || 0), 0) / filteredReports.length;
    const avgStorytelling = filteredReports.filter(r => r.storytelling_score).reduce((sum, r) => sum + r.storytelling_score, 0) / 
      (filteredReports.filter(r => r.storytelling_score).length || 1);
    
    const bestScore = Math.max(...filteredReports.map(r => r.overall_score));
    const worstScore = Math.min(...filteredReports.map(r => r.overall_score));
    
    const trend = previous ? ((latest.overall_score - previous.overall_score) / previous.overall_score * 100).toFixed(1) : 0;
    
    // Find strongest and weakest dimension
    const dimensions = [
      { name: 'Gravitas', score: avgGravitas },
      { name: 'Communication', score: avgCommunication },
      { name: 'Presence', score: avgPresence },
      { name: 'Storytelling', score: avgStorytelling }
    ];
    const strongest = dimensions.reduce((a, b) => a.score > b.score ? a : b);
    const weakest = dimensions.reduce((a, b) => a.score < b.score ? a : b);
    
    return {
      latest,
      previous,
      avgOverall: avgOverall.toFixed(1),
      avgGravitas: avgGravitas.toFixed(1),
      avgCommunication: avgCommunication.toFixed(1),
      avgPresence: avgPresence.toFixed(1),
      avgStorytelling: avgStorytelling.toFixed(1),
      bestScore: bestScore.toFixed(1),
      worstScore: worstScore.toFixed(1),
      trend,
      strongest,
      weakest,
      totalReports: filteredReports.length
    };
  }, [filteredReports]);
  
  // Prepare chart data
  const lineChartData = useMemo(() => {
    return [...filteredReports].reverse().map((r, idx) => ({
      name: new Date(r.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      overall: r.overall_score,
      gravitas: r.gravitas_score,
      communication: r.communication_score,
      presence: r.presence_score,
      storytelling: r.storytelling_score || 0
    }));
  }, [filteredReports]);
  
  const radarChartData = useMemo(() => {
    if (!analytics) return [];
    return [
      { dimension: 'Gravitas', score: parseFloat(analytics.avgGravitas), fullMark: 100 },
      { dimension: 'Communication', score: parseFloat(analytics.avgCommunication), fullMark: 100 },
      { dimension: 'Presence', score: parseFloat(analytics.avgPresence), fullMark: 100 },
      { dimension: 'Storytelling', score: parseFloat(analytics.avgStorytelling), fullMark: 100 },
    ];
  }, [analytics]);
  
  const pieChartData = useMemo(() => {
    if (!analytics) return [];
    return [
      { name: 'Gravitas', value: parseFloat(analytics.avgGravitas), color: COLORS.gravitas },
      { name: 'Communication', value: parseFloat(analytics.avgCommunication), color: COLORS.communication },
      { name: 'Presence', value: parseFloat(analytics.avgPresence), color: COLORS.presence },
      { name: 'Storytelling', value: parseFloat(analytics.avgStorytelling), color: COLORS.storytelling },
    ];
  }, [analytics]);
  
  const barChartData = useMemo(() => {
    return filteredReports.slice(0, 10).reverse().map((r, idx) => ({
      name: `#${filteredReports.length - idx}`,
      score: r.overall_score,
      fill: r.overall_score >= 70 ? '#22C55E' : r.overall_score >= 50 ? '#D4AF37' : '#EF4444'
    }));
  }, [filteredReports]);
  
  const navItems = [
    { name: 'Know your EP', path: '/know-your-ep', icon: Video, desc: 'Analyze your video' },
    { name: 'Simulator', path: '/simulator', icon: BarChart3, desc: 'Practice scenarios' },
    { name: 'Learning Bytes', path: '/learning', icon: BookOpen, desc: 'Daily tips' },
    { name: 'Training', path: '/training', icon: Dumbbell, desc: 'Skill courses' },
    { name: 'Executive Coaching', path: '/coaching', icon: Users, desc: 'Book sessions' },
    { name: 'How It Works', path: '/methodology', icon: HelpCircle, desc: 'Our methodology' },
  ];
  
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
          <p style={{color: '#64748B'}}>Loading your analytics...</p>
        </div>
      </div>
    );
  }
  
  return (
    <>
      {showProfileModal && (
        <ProfileModal 
          onComplete={() => { setShowProfileModal(false); setHasProfile(true); toast.success('Profile completed!'); }}
          onClose={() => setShowProfileModal(false)}
        />
      )}
      
      <div style={{minHeight: '100vh', backgroundColor: '#F8FAFC'}}>
        {/* Whitelisted User Welcome Banner */}
        {subscription?.is_whitelisted && (
          <div style={{
            background: 'linear-gradient(135deg, #D4AF37 0%, #F4D03F 100%)',
            padding: '16px 24px',
            textAlign: 'center',
            borderBottom: '2px solid #B8941F'
          }}>
            <p style={{fontSize: '16px', fontWeight: 600, color: '#FFFFFF', margin: 0}}>
              🎉 Your Subscription: <strong>Pro Tier</strong> - Enjoy unlimited usage of EP Quotient!
            </p>
          </div>
        )}
        
        {/* Top Navigation */}
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
              <div onClick={() => navigate('/')} style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', cursor: 'pointer'}}>
                EP <span style={{color: '#D4AF37'}}>Quotient</span>
              </div>
              <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                {/* Subscription Tier Badge */}
                {subscription && (
                  <div 
                    onClick={() => navigate('/pricing')}
                    style={{
                      padding: '6px 14px',
                      borderRadius: '20px',
                      backgroundColor: subscription.tier === 'pro' ? 'rgba(212, 175, 55, 0.15)' : 
                                     subscription.tier === 'basic' ? 'rgba(59, 130, 246, 0.15)' : 
                                     'rgba(100, 116, 139, 0.15)',
                      border: `2px solid ${subscription.tier === 'pro' ? '#D4AF37' : 
                                          subscription.tier === 'basic' ? '#3B82F6' : 
                                          '#64748B'}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                    }}
                  >
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: subscription.tier === 'pro' ? '#D4AF37' : 
                                     subscription.tier === 'basic' ? '#3B82F6' : 
                                     '#64748B'
                    }}></div>
                    <span style={{
                      fontSize: '12px',
                      fontWeight: 700,
                      color: subscription.tier === 'pro' ? '#92400E' : 
                             subscription.tier === 'basic' ? '#1E40AF' : 
                             '#475569',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      {subscription.is_whitelisted ? 'PRO ∞' : subscription.tier === 'free' ? 'FREE TRIAL' : subscription.tier.toUpperCase()}
                    </span>
                    {subscription.tier !== 'pro' && subscription.video_limit !== -1 && (
                      <span style={{
                        fontSize: '11px',
                        color: '#64748B',
                        fontWeight: 500
                      }}>
                        ({subscription.videos_used || 0}/{subscription.video_limit})
                      </span>
                    )}
                  </div>
                )}
                <span style={{fontSize: '14px', color: '#64748B'}}>Welcome, <strong style={{color: '#0F172A'}}>{user?.name}</strong></span>
                <Button variant="ghost" size="sm" onClick={handleLogout}><LogOut className="h-4 w-4 mr-2" /> Logout</Button>
              </div>
            </div>
            
            <div style={{display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 0', overflowX: 'auto'}}>
              {navItems.map((item, idx) => {
                const isActive = location.pathname === item.path;
                return (
                  <button key={idx} onClick={() => navigate(item.path)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '10px',
                      padding: '12px 20px', backgroundColor: isActive ? 'rgba(212, 175, 55, 0.1)' : '#FFFFFF',
                      border: isActive ? '2px solid #D4AF37' : '2px solid transparent',
                      borderRadius: '12px', cursor: 'pointer', transition: 'all 0.3s ease', whiteSpace: 'nowrap'
                    }}
                    onMouseEnter={(e) => { if (!isActive) { e.currentTarget.style.border = '2px solid #D4AF37'; e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(212, 175, 55, 0.2)'; }}}
                    onMouseLeave={(e) => { if (!isActive) { e.currentTarget.style.border = '2px solid transparent'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}}
                  >
                    <div style={{
                      width: '36px', height: '36px', borderRadius: '10px',
                      backgroundColor: isActive ? '#D4AF37' : 'rgba(212, 175, 55, 0.15)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                      <item.icon style={{width: '18px', height: '18px', color: isActive ? '#FFFFFF' : '#D4AF37'}} />
                    </div>
                    <div style={{textAlign: 'left'}}>
                      <div style={{fontSize: '14px', fontWeight: 600, color: isActive ? '#D4AF37' : '#0F172A'}}>{item.name}</div>
                      <div style={{fontSize: '11px', color: '#64748B'}}>{item.desc}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>
        
        {/* Main Content */}
        <div className="container mx-auto px-6 py-8">
          {/* Header */}
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '32px'}}>
            <div>
              <h1 style={{fontSize: '36px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
                Analytics <span style={{color: '#D4AF37'}}>Dashboard</span>
              </h1>
              <p style={{fontSize: '16px', color: '#64748B'}}>Real-time insights into your executive presence journey</p>
            </div>
            <div style={{display: 'flex', gap: '12px', alignItems: 'center'}}>
              {/* Date Filter */}
              <div style={{position: 'relative'}}>
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  style={{
                    padding: '10px 40px 10px 16px', borderRadius: '12px',
                    border: '2px solid #E2E8F0', backgroundColor: '#FFFFFF',
                    fontSize: '14px', color: '#0F172A', cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option value="all">All Time</option>
                  <option value="7days">Last 7 Days</option>
                  <option value="30days">Last 30 Days</option>
                  <option value="90days">Last 90 Days</option>
                </select>
                <Filter style={{position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#64748B'}} />
              </div>
              
              <Button variant="outline" onClick={handleRefresh} disabled={refreshing} style={{border: '2px solid #D4AF37', color: '#D4AF37'}}>
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} /> Refresh
              </Button>
              
              <Button onClick={() => navigate('/know-your-ep')}>
                <Video className="h-4 w-4 mr-2" /> New Assessment
              </Button>
            </div>
          </div>
          
          {filteredReports.length === 0 ? (
            /* Empty State */
            <div className="card-3d" style={{
              backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px',
              padding: '80px', textAlign: 'center'
            }}>
              <div style={{
                width: '100px', height: '100px', borderRadius: '24px',
                backgroundColor: 'rgba(212, 175, 55, 0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 24px'
              }}>
                <BarChart3 style={{width: '48px', height: '48px', color: '#D4AF37'}} />
              </div>
              <h2 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>No Reports Yet</h2>
              <p style={{fontSize: '16px', color: '#64748B', marginBottom: '32px', maxWidth: '400px', margin: '0 auto 32px'}}>
                Start your first EP assessment to see beautiful analytics and track your progress over time.
              </p>
              <Button onClick={() => navigate('/know-your-ep')} size="lg">
                <Video className="mr-2 h-5 w-5" /> Create First Assessment
              </Button>
            </div>
          ) : (
            <>
              {/* KPI Cards */}
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '24px'}}>
                {/* Latest Score */}
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                    <div style={{width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(212, 175, 55, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <Target style={{width: '20px', height: '20px', color: '#D4AF37'}} />
                    </div>
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>Latest Score</span>
                  </div>
                  <div style={{fontSize: '36px', fontWeight: 700, color: '#D4AF37', fontFamily: 'IBM Plex Mono, monospace'}}>{analytics?.latest?.overall_score}</div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '6px', marginTop: '8px'}}>
                    {parseFloat(analytics?.trend) >= 0 ? (
                      <TrendingUp style={{width: '16px', height: '16px', color: '#22C55E'}} />
                    ) : (
                      <TrendingDown style={{width: '16px', height: '16px', color: '#EF4444'}} />
                    )}
                    <span style={{fontSize: '13px', color: parseFloat(analytics?.trend) >= 0 ? '#22C55E' : '#EF4444', fontWeight: 600}}>
                      {analytics?.trend > 0 ? '+' : ''}{analytics?.trend}%
                    </span>
                    <span style={{fontSize: '12px', color: '#94A3B8'}}>vs previous</span>
                  </div>
                </div>
                
                {/* Average Score */}
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                    <div style={{width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(34, 197, 94, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <BarChart3 style={{width: '20px', height: '20px', color: '#22C55E'}} />
                    </div>
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>Average Score</span>
                  </div>
                  <div style={{fontSize: '36px', fontWeight: 700, color: '#0F172A', fontFamily: 'IBM Plex Mono, monospace'}}>{analytics?.avgOverall}</div>
                  <div style={{fontSize: '12px', color: '#94A3B8', marginTop: '8px'}}>Across {analytics?.totalReports} reports</div>
                </div>
                
                {/* Best Score */}
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                    <div style={{width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(139, 92, 246, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <Award style={{width: '20px', height: '20px', color: '#8B5CF6'}} />
                    </div>
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>Best Score</span>
                  </div>
                  <div style={{fontSize: '36px', fontWeight: 700, color: '#8B5CF6', fontFamily: 'IBM Plex Mono, monospace'}}>{analytics?.bestScore}</div>
                  <div style={{fontSize: '12px', color: '#94A3B8', marginTop: '8px'}}>Personal best</div>
                </div>
                
                {/* Strongest Dimension */}
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                    <div style={{width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(34, 197, 94, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <Zap style={{width: '20px', height: '20px', color: '#22C55E'}} />
                    </div>
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>Strongest</span>
                  </div>
                  <div style={{fontSize: '20px', fontWeight: 700, color: '#22C55E'}}>{analytics?.strongest?.name}</div>
                  <div style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', fontFamily: 'IBM Plex Mono, monospace'}}>{analytics?.strongest?.score?.toFixed(1)}</div>
                </div>
                
                {/* Needs Improvement */}
                <div className="card-3d" style={{
                  backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(212, 175, 55, 0.15)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px'}}>
                    <div style={{width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                      <MessageSquare style={{width: '20px', height: '20px', color: '#F59E0B'}} />
                    </div>
                    <span style={{fontSize: '13px', color: '#64748B', fontWeight: 500}}>Focus Area</span>
                  </div>
                  <div style={{fontSize: '20px', fontWeight: 700, color: '#F59E0B'}}>{analytics?.weakest?.name}</div>
                  <div style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', fontFamily: 'IBM Plex Mono, monospace'}}>{analytics?.weakest?.score?.toFixed(1)}</div>
                </div>
              </div>
              
              {/* Charts Row 1 */}
              <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px'}}>
                {/* Line Chart - Progress Over Time */}
                <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
                    Score <span style={{color: '#D4AF37'}}>Progression</span>
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={lineChartData}>
                      <defs>
                        <linearGradient id="colorOverall" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#D4AF37" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                      <XAxis dataKey="name" tick={{fontSize: 12, fill: '#64748B'}} />
                      <YAxis domain={[0, 100]} tick={{fontSize: 12, fill: '#64748B'}} />
                      <Tooltip 
                        contentStyle={{backgroundColor: '#FFFFFF', border: '2px solid #D4AF37', borderRadius: '12px'}}
                        labelStyle={{fontWeight: 700, color: '#0F172A'}}
                      />
                      <Legend />
                      <Area type="monotone" dataKey="overall" name="Overall" stroke="#D4AF37" fillOpacity={1} fill="url(#colorOverall)" strokeWidth={3} />
                      <Line type="monotone" dataKey="gravitas" name="Gravitas" stroke="#8B5CF6" strokeWidth={2} dot={{r: 4}} />
                      <Line type="monotone" dataKey="communication" name="Communication" stroke="#D4AF37" strokeWidth={2} dot={{r: 4}} />
                      <Line type="monotone" dataKey="presence" name="Presence" stroke="#22C55E" strokeWidth={2} dot={{r: 4}} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Radar Chart - Dimension Balance */}
                <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
                    Dimension <span style={{color: '#D4AF37'}}>Balance</span>
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarChartData}>
                      <PolarGrid stroke="#E2E8F0" />
                      <PolarAngleAxis dataKey="dimension" tick={{fontSize: 12, fill: '#0F172A', fontWeight: 600}} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{fontSize: 10, fill: '#64748B'}} />
                      <Radar name="Your Score" dataKey="score" stroke="#D4AF37" fill="#D4AF37" fillOpacity={0.4} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              {/* Charts Row 2 */}
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px', marginBottom: '24px'}}>
                {/* Pie Chart - Distribution */}
                <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
                    Score <span style={{color: '#D4AF37'}}>Distribution</span>
                  </h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                        label={({name, value}) => `${name}: ${value}`}
                        labelLine={{stroke: '#64748B'}}
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => value.toFixed(1)} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Bar Chart - Recent Scores */}
                <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
                    Recent <span style={{color: '#D4AF37'}}>Scores</span>
                  </h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={barChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                      <XAxis dataKey="name" tick={{fontSize: 11, fill: '#64748B'}} />
                      <YAxis domain={[0, 100]} tick={{fontSize: 11, fill: '#64748B'}} />
                      <Tooltip 
                        contentStyle={{backgroundColor: '#FFFFFF', border: '2px solid #D4AF37', borderRadius: '12px'}}
                      />
                      <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                        {barChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Dimension Averages */}
                <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A', marginBottom: '20px'}}>
                    Dimension <span style={{color: '#D4AF37'}}>Averages</span>
                  </h3>
                  <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                    {[
                      { name: 'Gravitas', score: analytics?.avgGravitas, color: '#8B5CF6' },
                      { name: 'Communication', score: analytics?.avgCommunication, color: '#D4AF37' },
                      { name: 'Presence', score: analytics?.avgPresence, color: '#22C55E' },
                      { name: 'Storytelling', score: analytics?.avgStorytelling, color: '#F59E0B' },
                    ].map((dim, idx) => (
                      <div key={idx}>
                        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '6px'}}>
                          <span style={{fontSize: '14px', fontWeight: 500, color: '#0F172A'}}>{dim.name}</span>
                          <span style={{fontSize: '14px', fontWeight: 700, color: dim.color}}>{dim.score}</span>
                        </div>
                        <div style={{height: '8px', backgroundColor: '#F1F5F9', borderRadius: '4px', overflow: 'hidden'}}>
                          <div style={{
                            height: '100%', width: `${dim.score}%`,
                            backgroundColor: dim.color, borderRadius: '4px',
                            transition: 'width 0.5s ease'
                          }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Reports List */}
              <div className="card-3d" style={{backgroundColor: '#FFFFFF', border: '2px solid #E2E8F0', borderRadius: '16px', padding: '24px'}}>
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px'}}>
                  <h3 style={{fontSize: '18px', fontWeight: 700, color: '#0F172A'}}>
                    All <span style={{color: '#D4AF37'}}>Reports</span> ({filteredReports.length})
                  </h3>
                </div>
                <div style={{display: 'grid', gap: '12px', maxHeight: '400px', overflowY: 'auto'}}>
                  {filteredReports.map((report, idx) => (
                    <div
                      key={report.report_id}
                      onClick={() => navigate(`/report/${report.report_id}`)}
                      style={{
                        display: 'grid', gridTemplateColumns: '1fr repeat(4, 80px) 100px',
                        alignItems: 'center', padding: '16px 20px',
                        border: '2px solid #F1F5F9', borderRadius: '12px',
                        cursor: 'pointer', transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#D4AF37'; e.currentTarget.style.backgroundColor = '#FAFAFA'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#F1F5F9'; e.currentTarget.style.backgroundColor = 'transparent'; }}
                    >
                      <div>
                        <div style={{fontSize: '15px', fontWeight: 600, color: '#0F172A'}}>Report #{filteredReports.length - idx}</div>
                        <div style={{fontSize: '13px', color: '#64748B'}}>
                          {new Date(report.created_at).toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'})}
                        </div>
                      </div>
                      <div style={{textAlign: 'center'}}>
                        <div style={{fontSize: '11px', color: '#64748B'}}>Gravitas</div>
                        <div style={{fontSize: '16px', fontWeight: 700, color: '#8B5CF6'}}>{report.gravitas_score?.toFixed(0) || '-'}</div>
                      </div>
                      <div style={{textAlign: 'center'}}>
                        <div style={{fontSize: '11px', color: '#64748B'}}>Comm.</div>
                        <div style={{fontSize: '16px', fontWeight: 700, color: '#D4AF37'}}>{report.communication_score?.toFixed(0) || '-'}</div>
                      </div>
                      <div style={{textAlign: 'center'}}>
                        <div style={{fontSize: '11px', color: '#64748B'}}>Presence</div>
                        <div style={{fontSize: '16px', fontWeight: 700, color: '#22C55E'}}>{report.presence_score?.toFixed(0) || '-'}</div>
                      </div>
                      <div style={{textAlign: 'center'}}>
                        <div style={{fontSize: '11px', color: '#64748B'}}>Story</div>
                        <div style={{fontSize: '16px', fontWeight: 700, color: '#F59E0B'}}>{report.storytelling_score?.toFixed(0) || '-'}</div>
                      </div>
                      <div style={{textAlign: 'right'}}>
                        <div style={{fontSize: '11px', color: '#64748B'}}>Overall</div>
                        <div style={{fontSize: '24px', fontWeight: 700, color: '#D4AF37', fontFamily: 'IBM Plex Mono, monospace'}}>{report.overall_score}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </>
  );
};

export default Dashboard;
