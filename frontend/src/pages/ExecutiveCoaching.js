import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { ArrowLeft, ExternalLink, Link as LinkIcon, Calendar, MessageSquare } from 'lucide-react';
import { coachingAPI, reportAPI } from '../lib/api';
import { toast } from 'sonner';

const ExecutiveCoaching = () => {
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);
  const [selectedReportId, setSelectedReportId] = useState('');
  const [shareLink, setShareLink] = useState('');
  const [creatingLink, setCreatingLink] = useState(false);

  const [form, setForm] = useState({
    name: '',
    email: '',
    goal: '',
    preferred_times: '',
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await reportAPI.listReports();
        const list = res.data?.reports || [];
        setReports(list);
        if (list[0]?.report_id) setSelectedReportId(list[0].report_id);
      } catch (e) {
        // stay silent; page still usable without reports
      }
    };
    load();
  }, []);

  const handleCreateShare = async () => {
    if (!selectedReportId) {
      toast.error('Create a report first');
      return;
    }

    setCreatingLink(true);
    try {
      const res = await reportAPI.createShareLink(selectedReportId);
      const shareId = res.data?.share_id;
      if (!shareId) throw new Error('No share_id');
      const url = `${window.location.origin}/shared/${shareId}`;
      setShareLink(url);
      try {
        await navigator.clipboard.writeText(url);
        toast.success('Share link copied to clipboard');
      } catch {
        toast.success('Share link generated');
      }
    } catch (e) {
      toast.error('Failed to generate share link');
    } finally {
      setCreatingLink(false);
    }
  };

  const handleSubmitRequest = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await coachingAPI.createRequest({
        ...form,
        report_id: selectedReportId || null,
      });
      toast.success('Request sent. A coach will reach out.');
      setForm({ name: '', email: '', goal: '', preferred_times: '', notes: '' });
    } catch (e) {
      toast.error('Failed to submit request');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{minHeight: '100vh', backgroundColor: '#FAFAFA'}}>
      <nav style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '16px 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50
      }}>
        <Button variant="ghost" onClick={() => navigate('/dashboard')} data-testid="back-to-dashboard">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>
      </nav>

      <div className="container mx-auto px-6 py-12 max-w-5xl">
        <div style={{marginBottom: '40px'}}>
          <h1 style={{fontSize: '42px', fontWeight: 700, color: '#0F172A', marginBottom: '12px'}}>
            Executive <span style={{color: '#D4AF37'}}>Coaching</span>
          </h1>
          <p style={{fontSize: '18px', color: '#64748B'}}>
            Book a session and send your EP report to a coach for targeted feedback.
          </p>
        </div>

        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px'}}>
          {/* Book a Session Card */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #D4AF37',
            borderRadius: '16px',
            padding: '32px'
          }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px'}}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                backgroundColor: 'rgba(212, 175, 55, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Calendar style={{width: '24px', height: '24px', color: '#D4AF37'}} />
              </div>
              <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A'}}>
                Book a Coaching Session
              </h3>
            </div>
            <p style={{fontSize: '15px', color: '#64748B', marginBottom: '24px', lineHeight: 1.6}}>
              Use the booking link (Calendly, etc.) or submit a request form and we'll follow up.
            </p>

            <a
              href="https://calendly.com"
              target="_blank"
              rel="noopener noreferrer"
              style={{display: 'inline-block', marginBottom: '32px'}}
            >
              <Button size="lg" style={{backgroundColor: '#D4AF37', color: '#FFFFFF'}} data-testid="open-booking-link">
                Open Booking Link <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
            </a>

            <div style={{borderTop: '1px solid #E2E8F0', paddingTop: '24px'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px'}}>
                <MessageSquare style={{width: '20px', height: '20px', color: '#D4AF37'}} />
                <h4 style={{fontSize: '18px', fontWeight: 600, color: '#0F172A'}}>Request a Coach (internal)</h4>
              </div>
              <form onSubmit={handleSubmitRequest} style={{display: 'flex', flexDirection: 'column', gap: '16px'}} data-testid="coaching-request-form">
                <div>
                  <Label htmlFor="coach-name" style={{color: '#0F172A', fontWeight: 500}}>Name</Label>
                  <Input 
                    id="coach-name" 
                    value={form.name} 
                    onChange={(e) => setForm(f => ({...f, name: e.target.value}))} 
                    required 
                    style={{marginTop: '6px', border: '2px solid #E2E8F0'}}
                  />
                </div>
                <div>
                  <Label htmlFor="coach-email" style={{color: '#0F172A', fontWeight: 500}}>Email</Label>
                  <Input 
                    id="coach-email" 
                    type="email" 
                    value={form.email} 
                    onChange={(e) => setForm(f => ({...f, email: e.target.value}))} 
                    required 
                    style={{marginTop: '6px', border: '2px solid #E2E8F0'}}
                  />
                </div>
                <div>
                  <Label htmlFor="coach-goal" style={{color: '#0F172A', fontWeight: 500}}>Primary goal</Label>
                  <Input 
                    id="coach-goal" 
                    value={form.goal} 
                    onChange={(e) => setForm(f => ({...f, goal: e.target.value}))} 
                    placeholder="e.g., gravitas in board meetings" 
                    required 
                    style={{marginTop: '6px', border: '2px solid #E2E8F0'}}
                  />
                </div>
                <div>
                  <Label htmlFor="coach-times" style={{color: '#0F172A', fontWeight: 500}}>Preferred times</Label>
                  <Input 
                    id="coach-times" 
                    value={form.preferred_times} 
                    onChange={(e) => setForm(f => ({...f, preferred_times: e.target.value}))} 
                    placeholder="e.g., Tue/Thu mornings" 
                    style={{marginTop: '6px', border: '2px solid #E2E8F0'}}
                  />
                </div>
                <div>
                  <Label htmlFor="coach-notes" style={{color: '#0F172A', fontWeight: 500}}>Notes</Label>
                  <Input 
                    id="coach-notes" 
                    value={form.notes} 
                    onChange={(e) => setForm(f => ({...f, notes: e.target.value}))} 
                    placeholder="Anything the coach should know" 
                    style={{marginTop: '6px', border: '2px solid #E2E8F0'}}
                  />
                </div>

                <Button 
                  type="submit" 
                  disabled={submitting} 
                  style={{backgroundColor: '#D4AF37', color: '#FFFFFF', marginTop: '8px'}}
                  data-testid="submit-coaching-request"
                >
                  {submitting ? 'Sending...' : 'Send Request'}
                </Button>
              </form>
            </div>
          </div>

          {/* Share Reports Card */}
          <div className="card-3d" style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #E2E8F0',
            borderRadius: '16px',
            padding: '32px'
          }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px'}}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                backgroundColor: 'rgba(212, 175, 55, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <LinkIcon style={{width: '24px', height: '24px', color: '#D4AF37'}} />
              </div>
              <h3 style={{fontSize: '24px', fontWeight: 700, color: '#0F172A'}}>
                Share Reports
              </h3>
            </div>
            <p style={{fontSize: '15px', color: '#64748B', marginBottom: '24px', lineHeight: 1.6}}>
              Generate a time-limited share link (7 days). You can paste it into email or messaging.
            </p>

            <div style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
              <div>
                <Label style={{color: '#0F172A', fontWeight: 500}}>Choose report</Label>
                <select
                  value={selectedReportId}
                  onChange={(e) => setSelectedReportId(e.target.value)}
                  style={{
                    marginTop: '8px',
                    width: '100%',
                    border: '2px solid #E2E8F0',
                    borderRadius: '8px',
                    backgroundColor: '#FFFFFF',
                    padding: '10px 12px',
                    fontSize: '14px',
                    color: '#0F172A'
                  }}
                  data-testid="report-select"
                >
                  {reports.length === 0 ? (
                    <option value="">No reports yet</option>
                  ) : (
                    reports.map((r) => (
                      <option key={r.report_id} value={r.report_id}>
                        {new Date(r.created_at).toLocaleDateString()} — Score {r.overall_score}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <Button
                variant="outline"
                size="lg"
                onClick={handleCreateShare}
                disabled={creatingLink}
                style={{border: '2px solid #D4AF37', color: '#D4AF37'}}
                data-testid="generate-share-link"
              >
                <LinkIcon className="mr-2 h-4 w-4" /> {creatingLink ? 'Generating...' : 'Generate Share Link'}
              </Button>

              {shareLink && (
                <div style={{
                  border: '2px solid #D4AF37',
                  borderRadius: '12px',
                  padding: '16px',
                  backgroundColor: 'rgba(212, 175, 55, 0.05)'
                }} data-testid="share-link-box">
                  <div style={{fontSize: '13px', color: '#64748B', marginBottom: '8px', fontWeight: 500}}>Share link (copied)</div>
                  <div style={{fontFamily: 'monospace', fontSize: '13px', color: '#0F172A', wordBreak: 'break-all'}}>{shareLink}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveCoaching;
