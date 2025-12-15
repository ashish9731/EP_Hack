import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import axios from 'axios';

const ProfileModal = ({ onComplete, onClose }) => {
  const [formData, setFormData] = useState({
    role: '',
    seniority_level: '',
    years_experience: '',
    industry: '',
    company_size: '',
    primary_goal: ''
  });
  const [loading, setLoading] = useState(false);
  
  const roles = [
    'Chief Executive Officer (CEO)',
    'Chief Technology Officer (CTO)',
    'Chief Operating Officer (COO)',
    'Chief Financial Officer (CFO)',
    'Vice President',
    'Director',
    'Senior Manager',
    'Manager',
    'Team Lead',
    'Senior Individual Contributor',
    'Other'
  ];
  
  const seniority = [
    'C-Suite',
    'VP / Senior VP',
    'Director / Senior Director',
    'Manager / Senior Manager',
    'Mid-Level',
    'Entry-Level'
  ];
  
  const industries = [
    'Technology',
    'Finance & Banking',
    'Healthcare',
    'Consulting',
    'Manufacturing',
    'Retail',
    'Education',
    'Government',
    'Non-Profit',
    'Other'
  ];
  
  const companySizes = [
    'Startup (1-50)',
    'Small (51-200)',
    'Medium (201-1000)',
    'Large (1001-5000)',
    'Enterprise (5000+)'
  ];
  
  const goals = [
    'Prepare for promotion to executive role',
    'Improve board presentation skills',
    'Enhance team leadership presence',
    'Refine investor pitch delivery',
    'Strengthen stakeholder communication',
    'Build executive gravitas',
    'Other'
  ];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const token = localStorage.getItem('session_token');
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      // Prepare data - convert empty strings to null
      const submitData = {
        ...formData,
        years_experience: formData.years_experience ? parseInt(formData.years_experience) : null,
        industry: formData.industry || null,
        company_size: formData.company_size || null,
        primary_goal: formData.primary_goal || null
      };
      
      await axios.post(`${API_URL}/api/profile/`, submitData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });
      
      onComplete();
    } catch (error) {
      console.error('Profile creation error:', error);
      alert('Failed to save profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 50,
      padding: '16px'
    }}>
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        maxWidth: '650px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto'
      }}>
        <div style={{
          padding: '32px',
          borderBottom: '1px solid #E2E8F0'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: 600,
            color: '#0F172A',
            marginBottom: '8px'
          }}>
            Complete Your Profile
          </h2>
          <p style={{
            fontSize: '15px',
            color: '#64748B',
            lineHeight: 1.5
          }}>
            Help us tailor your Executive Presence analysis to your specific role and leadership level.
          </p>
        </div>
        
        <form onSubmit={handleSubmit} style={{padding: '32px'}}>
          <div style={{display: 'flex', flexDirection: 'column', gap: '24px'}}>
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Current Role / Title <span style={{color: '#EF4444'}}>*</span>
              </label>
              <select
                required
                value={formData.role}
                onChange={(e) => setFormData({...formData, role: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '15px',
                  color: '#1E293B',
                  backgroundColor: '#FFFFFF'
                }}
              >
                <option value="">Select your role</option>
                {roles.map(role => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Seniority Level <span style={{color: '#EF4444'}}>*</span>
              </label>
              <select
                required
                value={formData.seniority_level}
                onChange={(e) => setFormData({...formData, seniority_level: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '15px',
                  color: '#1E293B',
                  backgroundColor: '#FFFFFF'
                }}
              >
                <option value="">Select seniority level</option>
                {seniority.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Years of Professional Experience <span style={{color: '#EF4444'}}>*</span>
              </label>
              <input
                type="number"
                min="0"
                max="50"
                required
                value={formData.years_experience}
                onChange={(e) => setFormData({...formData, years_experience: parseInt(e.target.value)})}
                placeholder="e.g., 15"
                style={{
                  width: '100%',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  padding: '10px 12px',
                  fontSize: '15px'
                }}
              />
            </div>
            
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Industry
              </label>
              <select
                value={formData.industry}
                onChange={(e) => setFormData({...formData, industry: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '15px',
                  color: '#1E293B',
                  backgroundColor: '#FFFFFF'
                }}
              >
                <option value="">Select industry (optional)</option>
                {industries.map(ind => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Company Size
              </label>
              <select
                value={formData.company_size}
                onChange={(e) => setFormData({...formData, company_size: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '15px',
                  color: '#1E293B',
                  backgroundColor: '#FFFFFF'
                }}
              >
                <option value="">Select company size (optional)</option>
                {companySizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label style={{color: '#1E293B', fontWeight: 500, marginBottom: '8px', display: 'block', fontSize: '14px'}}>
                Primary Goal
              </label>
              <select
                value={formData.primary_goal}
                onChange={(e) => setFormData({...formData, primary_goal: e.target.value})}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '6px',
                  fontSize: '15px',
                  color: '#1E293B',
                  backgroundColor: '#FFFFFF'
                }}
              >
                <option value="">Select your primary goal (optional)</option>
                {goals.map(goal => (
                  <option key={goal} value={goal}>{goal}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div style={{
            marginTop: '32px',
            paddingTop: '24px',
            borderTop: '1px solid #E2E8F0',
            display: 'flex',
            gap: '12px',
            justifyContent: 'flex-end'
          }}>
            <Button
              type="button"
              onClick={onClose}
              variant="ghost"
              style={{
                color: '#64748B',
                fontWeight: 500,
                padding: '10px 24px'
              }}
            >
              Skip for Now
            </Button>
            <Button
              type="submit"
              disabled={loading}
              style={{
                backgroundColor: '#D4AF37',
                color: '#FFFFFF',
                fontWeight: 500,
                padding: '10px 24px'
              }}
            >
              {loading ? 'Saving...' : 'Complete Profile'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileModal;
