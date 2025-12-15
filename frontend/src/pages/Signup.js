import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { authAPI } from '../lib/api';
import { toast } from 'sonner';
import { ArrowLeft, Sparkles } from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await authAPI.signup({ email, password, name });
      toast.success('Account created successfully!');
      setTimeout(() => {
        navigate('/dashboard', { replace: true });
      }, 100);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGoogleSignup = async () => {
    try {
      const response = await authAPI.googleRedirect();
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Failed to initiate Google signup');
    }
  };
  
  return (
    <div style={{minHeight: '100vh', display: 'flex', backgroundColor: '#FFFFFF'}}>
      <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px'}}>
        <div style={{width: '100%', maxWidth: '440px'}}>
          <Button variant="ghost" onClick={() => navigate('/')} style={{marginBottom: '32px'}} data-testid="back-button">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
          </Button>
          
          <div style={{marginBottom: '40px'}}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              backgroundColor: 'rgba(212, 175, 55, 0.1)',
              border: '1px solid rgba(212, 175, 55, 0.3)',
              borderRadius: '20px',
              marginBottom: '16px'
            }}>
              <Sparkles style={{width: '14px', height: '14px', color: '#D4AF37'}} />
              <span style={{fontSize: '13px', color: '#D4AF37', fontWeight: 500}}>Join Leaders</span>
            </div>
            
            <h2 style={{fontSize: '36px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>Create Your Account</h2>
            <p style={{fontSize: '16px', color: '#64748B'}}>Start your executive presence journey today</p>
          </div>
          
          <Button 
            variant="outline" 
            style={{
              width: '100%',
              marginBottom: '28px',
              padding: '12px'
            }}
            onClick={handleGoogleSignup}
            data-testid="google-signup-button"
          >
            <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign up with Google
          </Button>
          
          <div style={{position: 'relative', marginBottom: '28px'}}>
            <div style={{position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', backgroundColor: '#E2E8F0'}} />
            <div style={{position: 'relative', textAlign: 'center'}}>
              <span style={{backgroundColor: '#FFFFFF', padding: '0 12px', fontSize: '13px', color: '#64748B'}}>Or continue with email</span>
            </div>
          </div>
          
          <form onSubmit={handleSignup} style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
            <div>
              <Label htmlFor="name" style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block'}}>Full Name</Label>
              <Input 
                id="name"
                type="text" 
                placeholder="John Executive" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                data-testid="name-input"
                style={{
                  border: '2px solid #E2E8F0',
                  borderRadius: '8px',
                  padding: '12px 14px',
                  fontSize: '15px',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#D4AF37'}
                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
              />
            </div>
            
            <div>
              <Label htmlFor="email" style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block'}}>Email Address</Label>
              <Input 
                id="email"
                type="email" 
                placeholder="you@company.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="email-input"
                style={{
                  border: '2px solid #E2E8F0',
                  borderRadius: '8px',
                  padding: '12px 14px',
                  fontSize: '15px',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#D4AF37'}
                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
              />
            </div>
            
            <div>
              <Label htmlFor="password" style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block'}}>Password</Label>
              <Input 
                id="password"
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                data-testid="password-input"
                style={{
                  border: '2px solid #E2E8F0',
                  borderRadius: '8px',
                  padding: '12px 14px',
                  fontSize: '15px',
                  transition: 'all 0.2s'
                }}
                onFocus={(e) => e.target.style.borderColor = '#D4AF37'}
                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
              />
            </div>
            
            <Button 
              type="submit" 
              disabled={loading} 
              data-testid="submit-button"
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                fontWeight: 600,
                marginTop: '8px'
              }}
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>
          
          <p style={{marginTop: '32px', textAlign: 'center', fontSize: '15px', color: '#64748B'}}>
            Already have an account?{' '}
            <Link to="/login" style={{color: '#D4AF37', textDecoration: 'none', fontWeight: 600}} data-testid="login-link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
      
      <div style={{
        flex: 1,
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '64px',
        position: 'relative',
        overflow: 'hidden'
      }} className="hidden lg:flex">
        <div style={{
          position: 'absolute',
          top: '0',
          left: '0',
          right: '0',
          bottom: '0',
          backgroundImage: 'radial-gradient(circle at 30% 40%, rgba(212, 175, 55, 0.15) 0%, transparent 50%), radial-gradient(circle at 70% 60%, rgba(212, 175, 55, 0.15) 0%, transparent 50%)',
          pointerEvents: 'none'
        }}></div>
        
        <div style={{maxWidth: '500px', position: 'relative', zIndex: 1}}>
          <h1 style={{fontSize: '42px', fontWeight: 700, color: '#FFFFFF', marginBottom: '24px'}}>
            Begin Your <span style={{color: '#D4AF37'}}>Leadership Transformation</span>
          </h1>
          <p style={{fontSize: '18px', color: 'rgba(255,255,255,0.8)', lineHeight: 1.7, marginBottom: '32px'}}>
            Join executives who are mastering their presence through AI-powered video analysis and personalized coaching.
          </p>
          
          <div style={{marginTop: '40px', display: 'flex', flexDirection: 'column', gap: '16px'}}>
            {[
              { icon: '✓', text: 'Research-backed EP scoring across 4 dimensions' },
              { icon: '✓', text: 'Real-time AI analysis with GPT-4o & Whisper' },
              { icon: '✓', text: 'Personalized coaching tips and training modules' },
              { icon: '✓', text: 'Executive scenarios and practice simulations' }
            ].map((item, idx) => (
              <div key={idx} style={{display: 'flex', alignItems: 'start', gap: '12px'}}>
                <div style={{color: '#D4AF37', fontSize: '20px', fontWeight: 'bold'}}>{item.icon}</div>
                <p style={{fontSize: '16px', color: 'rgba(255,255,255,0.9)', margin: 0}}>{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;