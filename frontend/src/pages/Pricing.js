import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Check, X, Crown, Zap, Building2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Pricing = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly'); // monthly or yearly
  const [userSubscription, setUserSubscription] = useState(null);

  useEffect(() => {
    fetchUserSubscription();
  }, []);

  const fetchUserSubscription = async () => {
    try {
      const token = localStorage.getItem('session_token');
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      const response = await axios.get(`${API_URL}/api/subscription/status`, {
        headers: { 'Authorization': `Bearer ${token}` },
        withCredentials: true
      });
      
      setUserSubscription(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const handleSelectPlan = async (tier) => {
    if (tier === 'enterprise') {
      toast.info('Please contact us at support@epquotient.com for Enterprise pricing');
      return;
    }

    setSelectedPlan(tier);
    setLoading(true);

    try {
      const token = localStorage.getItem('session_token');
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      const response = await axios.post(`${API_URL}/api/subscription/upgrade`, {
        tier,
        billing_cycle: billingCycle
      }, {
        headers: { 'Authorization': `Bearer ${token}` },
        withCredentials: true
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        toast.success('Subscription updated successfully!');
        navigate('/dashboard');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upgrade plan');
      setLoading(false);
    }
  };

  const plans = [
    {
      tier: 'free',
      name: 'Free Trial',
      icon: Zap,
      monthlyPrice: 0,
      yearlyPrice: 0,
      description: '2-day trial to explore',
      features: [
        '1 video analysis',
        '2 simulator scenarios',
        '2 learning bytes',
        'Report preview only',
        'No download access',
        'Basic support'
      ],
      limitations: [
        'No PDF downloads',
        'Limited scenarios',
        'Screenshot protected'
      ],
      color: '#64748B',
      bgColor: 'rgba(100, 116, 139, 0.1)',
      borderColor: '#64748B'
    },
    {
      tier: 'basic',
      name: 'Basic',
      icon: Check,
      monthlyPrice: 25,
      yearlyPrice: 275,
      description: 'Essential tools for growth',
      popular: false,
      features: [
        '7 video analyses per month',
        'Report download enabled',
        'Basic EP score (4 dimensions)',
        'Limited simulator scenarios',
        'Daily Learning Bytes',
        'Weekly Training modules',
        'Basic analytics dashboard',
        'Email support'
      ],
      limitations: [],
      color: '#D4AF37',
      bgColor: 'rgba(212, 175, 55, 0.05)',
      borderColor: '#D4AF37'
    },
    {
      tier: 'pro',
      name: 'Pro',
      icon: Crown,
      monthlyPrice: 80,
      yearlyPrice: 850,
      description: 'Complete executive presence mastery',
      popular: true,
      features: [
        'Unlimited video analyses',
        'Advanced EP scoring + benchmarks',
        'Full Simulator (all 20 scenarios)',
        'Complete Learning Bytes library',
        'Full Training module access',
        'Advanced analytics + trends',
        'PDF downloads + sharing',
        'Priority support',
        'Early access to features'
      ],
      limitations: [],
      color: '#D4AF37',
      bgColor: 'rgba(212, 175, 55, 0.08)',
      borderColor: '#D4AF37'
    },
    {
      tier: 'enterprise',
      name: 'Enterprise',
      icon: Building2,
      monthlyPrice: null,
      yearlyPrice: null,
      description: 'Custom solutions for teams',
      popular: false,
      features: [
        'Everything in Pro',
        'Custom branding',
        'Bulk user licenses (10+)',
        'Dedicated account manager',
        'Custom integrations',
        'SLA guarantees',
        'Team management dashboard',
        'Advanced reporting'
      ],
      limitations: [],
      color: '#0F172A',
      bgColor: 'rgba(15, 23, 42, 0.05)',
      borderColor: '#0F172A'
    }
  ];

  if (userSubscription?.is_whitelisted) {
    return (
      <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{textAlign: 'center', maxWidth: '600px', padding: '48px'}}>
          <div style={{
            width: '80px', height: '80px', margin: '0 auto 24px',
            backgroundColor: 'rgba(212, 175, 55, 0.15)',
            borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Crown style={{width: '40px', height: '40px', color: '#D4AF37'}} />
          </div>
          <h1 style={{fontSize: '32px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
            Your Subscription: <span style={{color: '#D4AF37'}}>Pro Tier</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B', marginBottom: '32px'}}>
            Enjoy unlimited usage of EP Quotient! You have full access to all premium features.
          </p>
          <Button onClick={() => navigate('/dashboard')} style={{backgroundColor: '#D4AF37', color: '#FFFFFF', padding: '12px 32px'}}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA', paddingTop: '48px', paddingBottom: '64px'}}>
      <div className="container mx-auto px-6">
        <div style={{textAlign: 'center', marginBottom: '48px'}}>
          <h1 style={{fontSize: '48px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
            Choose Your <span style={{color: '#D4AF37'}}>Plan</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B', maxWidth: '600px', margin: '0 auto 32px'}}>
            Select the perfect plan to elevate your executive presence
          </p>

          {/* Billing Toggle */}
          <div style={{display: 'inline-flex', alignItems: 'center', gap: '16px', padding: '8px', backgroundColor: '#FFFFFF', borderRadius: '12px', border: '2px solid #E2E8F0'}}>
            <button
              onClick={() => setBillingCycle('monthly')}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: billingCycle === 'monthly' ? '#D4AF37' : 'transparent',
                color: billingCycle === 'monthly' ? '#FFFFFF' : '#64748B',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: billingCycle === 'yearly' ? '#D4AF37' : 'transparent',
                color: billingCycle === 'yearly' ? '#FFFFFF' : '#64748B',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Yearly
              <span style={{marginLeft: '8px', fontSize: '12px', padding: '2px 8px', backgroundColor: 'rgba(212, 175, 55, 0.2)', borderRadius: '8px', color: '#92400E'}}>
                Save 17%
              </span>
            </button>
          </div>
        </div>

        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', maxWidth: '1400px', margin: '0 auto'}}>
          {plans.map((plan) => {
            const Icon = plan.icon;
            const price = billingCycle === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;
            const isCurrentPlan = userSubscription?.tier === plan.tier;

            return (
              <div
                key={plan.tier}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: plan.popular ? `3px solid ${plan.borderColor}` : `2px solid #E2E8F0`,
                  borderRadius: '16px',
                  padding: '32px',
                  position: 'relative',
                  transition: 'all 0.3s ease',
                  transform: plan.popular ? 'scale(1.05)' : 'scale(1)'
                }}
              >
                {plan.popular && (
                  <div style={{
                    position: 'absolute',
                    top: '-12px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: '#D4AF37',
                    color: '#FFFFFF',
                    padding: '6px 20px',
                    borderRadius: '20px',
                    fontSize: '13px',
                    fontWeight: 700
                  }}>
                    MOST POPULAR
                  </div>
                )}

                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '12px',
                  backgroundColor: plan.bgColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '20px'
                }}>
                  <Icon style={{width: '28px', height: '28px', color: plan.color}} />
                </div>

                <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '8px'}}>
                  {plan.name}
                </h3>
                <p style={{fontSize: '14px', color: '#64748B', marginBottom: '24px'}}>
                  {plan.description}
                </p>

                <div style={{marginBottom: '24px'}}>
                  {price !== null ? (
                    <>
                      <div style={{display: 'flex', alignItems: 'baseline', gap: '8px'}}>
                        <span style={{fontSize: '48px', fontWeight: 700, color: '#0F172A'}}>
                          ${price}
                        </span>
                        <span style={{fontSize: '16px', color: '#64748B'}}>
                          /{billingCycle === 'monthly' ? 'mo' : 'yr'}
                        </span>
                      </div>
                      {billingCycle === 'yearly' && price > 0 && (
                        <p style={{fontSize: '13px', color: '#64748B', marginTop: '4px'}}>
                          ${(price / 12).toFixed(2)}/month billed annually
                        </p>
                      )}
                    </>
                  ) : (
                    <div style={{fontSize: '32px', fontWeight: 700, color: '#0F172A'}}>
                      Custom
                    </div>
                  )}
                </div>

                <div style={{marginBottom: '24px'}}>
                  {plan.features.map((feature, idx) => (
                    <div key={idx} style={{display: 'flex', alignItems: 'start', gap: '12px', marginBottom: '12px'}}>
                      <Check style={{width: '20px', height: '20px', color: '#D4AF37', flexShrink: 0, marginTop: '2px'}} />
                      <span style={{fontSize: '14px', color: '#1E293B', lineHeight: 1.5}}>{feature}</span>
                    </div>
                  ))}
                  {plan.limitations.map((limitation, idx) => (
                    <div key={idx} style={{display: 'flex', alignItems: 'start', gap: '12px', marginBottom: '12px'}}>
                      <X style={{width: '20px', height: '20px', color: '#64748B', flexShrink: 0, marginTop: '2px'}} />
                      <span style={{fontSize: '14px', color: '#64748B', lineHeight: 1.5}}>{limitation}</span>
                    </div>
                  ))}
                </div>

                {isCurrentPlan ? (
                  <Button
                    disabled
                    style={{
                      width: '100%',
                      padding: '14px',
                      backgroundColor: '#E2E8F0',
                      color: '#64748B',
                      fontSize: '16px',
                      fontWeight: 600
                    }}
                  >
                    Current Plan
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleSelectPlan(plan.tier)}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '14px',
                      backgroundColor: plan.tier === 'free' ? '#64748B' : '#D4AF37',
                      color: '#FFFFFF',
                      fontSize: '16px',
                      fontWeight: 600
                    }}
                  >
                    {loading && selectedPlan === plan.tier ? 'Processing...' : 
                     plan.tier === 'free' ? 'Start Free Trial' :
                     plan.tier === 'enterprise' ? 'Contact Sales' : 
                     'Upgrade Now'}
                  </Button>
                )}
              </div>
            );
          })}
        </div>

        <div style={{textAlign: 'center', marginTop: '64px', padding: '32px', backgroundColor: '#FFFFFF', borderRadius: '16px', border: '2px solid #E2E8F0', maxWidth: '800px', margin: '64px auto 0'}}>
          <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A', marginBottom: '16px'}}>
            Not sure which plan is right for you?
          </h3>
          <p style={{fontSize: '16px', color: '#64748B', marginBottom: '24px'}}>
            Start with our 2-day free trial and upgrade anytime to unlock more features.
          </p>
          <Button onClick={() => navigate('/dashboard')} variant="outline" style={{border: '2px solid #D4AF37', color: '#D4AF37'}}>
            Continue to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
