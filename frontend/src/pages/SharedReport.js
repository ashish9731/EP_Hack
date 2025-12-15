import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import { reportAPI } from '../lib/api';
import { toast } from 'sonner';
import { ArrowLeft } from 'lucide-react';
import { getScoreLabel, formatTimestamp } from '../lib/utils';

const SharedReport = () => {
  const { shareId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShared = async () => {
      try {
        const res = await reportAPI.getSharedReport(shareId);
        setReport(res.data?.report);
      } catch (e) {
        toast.error('Share link is invalid or expired');
      } finally {
        setLoading(false);
      }
    };
    fetchShared();
  }, [shareId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading shared report...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md px-6">
          <h1 className="font-display text-3xl font-bold mb-2">Link unavailable</h1>
          <p className="text-muted-foreground mb-6">This share link may have expired or been revoked.</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
          </Button>
        </div>
      </div>
    );
  }

  const scoreLabel = getScoreLabel(report.overall_score);
  const metrics = report.detailed_metrics || {};

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate('/') }>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
          </Button>
          <div className="text-sm text-muted-foreground">Shared EP Report</div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="font-display text-5xl font-bold mb-4">EP Report</h1>
          <p className="text-lg text-muted-foreground mb-8">
            Shared view of the assessment across Gravitas, Communication, Presence, and Storytelling.
          </p>

          <div className="inline-flex items-center gap-4 bg-card border-2 border-accent rounded-2xl px-8 py-6">
            <div>
              <div className="font-mono text-6xl font-bold text-accent">{report.overall_score}</div>
              <div className="text-sm text-muted-foreground">Overall EP Score</div>
            </div>
            <div className="h-16 w-px bg-border"></div>
            <div>
              <div className={`text-2xl font-semibold ${scoreLabel.color}`}>{scoreLabel.label}</div>
              <div className="text-sm text-muted-foreground">Performance Level</div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-4 mb-12">
          {[
            { label: 'Gravitas', score: report.gravitas_score, weight: '25%' },
            { label: 'Communication', score: report.communication_score, weight: '35%' },
            { label: 'Presence', score: report.presence_score, weight: '25%' },
            { label: 'Storytelling', score: report.storytelling_score, weight: '15%' },
          ].map((dim, idx) => (
            <Card key={idx} className="p-6 text-center">
              <div className="text-sm text-muted-foreground mb-2">{dim.label}</div>
              <div className="font-mono text-4xl font-bold text-primary mb-1">
                {dim.score ? Math.round(dim.score) : 'N/A'}
              </div>
              <div className="text-xs text-accent">{dim.weight} weight</div>
            </Card>
          ))}
        </div>

        <Accordion type="multiple" className="space-y-4">
          <AccordionItem value="communication" className="bg-card border border-border rounded-xl px-6">
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-center justify-between w-full pr-4">
                <span className="font-display text-xl font-semibold">Communication (35%)</span>
                <span className="font-mono text-2xl font-bold text-accent">{Math.round(report.communication_score)}</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4 space-y-6">
              <div>
                <h4 className="font-semibold mb-2">Speaking Rate</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  {metrics.communication?.speaking_rate?.calculation || 'Calculation unavailable'}
                </p>
                <p className="text-sm italic">{metrics.communication?.speaking_rate?.benchmark || 'No benchmark'}</p>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Filler Words ({metrics.communication?.filler_words?.count || 0} detected)</h4>
                <p className="text-sm text-muted-foreground mb-2">
                  Rate: {metrics.communication?.filler_words?.rate_per_minute || 0} per minute
                </p>
                {metrics.communication?.filler_words?.fillers?.slice(0, 10).map((filler, idx) => (
                  <span key={idx} className="inline-block text-xs bg-secondary px-2 py-1 rounded mr-2 mb-2 font-mono">
                    {formatTimestamp(filler.timestamp)}: {filler.word}
                  </span>
                ))}
              </div>

              <div>
                <h4 className="font-semibold mb-2">Pauses ({metrics.communication?.pauses?.length || 0} detected)</h4>
                <div className="space-y-1">
                  {metrics.communication?.pauses?.slice(0, 5).map((pause, idx) => (
                    <div key={idx} className="text-sm font-mono bg-secondary/50 px-3 py-2 rounded">
                      {formatTimestamp(pause.start)}-{formatTimestamp(pause.end)} ({pause.duration}s, {pause.type})
                    </div>
                  ))}
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="presence" className="bg-card border border-border rounded-xl px-6">
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-center justify-between w-full pr-4">
                <span className="font-display text-xl font-semibold">Presence (25%)</span>
                <span className="font-mono text-2xl font-bold text-accent">{Math.round(report.presence_score)}</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Posture Score</div>
                  <div className="text-2xl font-mono font-bold">{metrics.presence?.posture_score || 0}%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Eye Contact Ratio</div>
                  <div className="text-2xl font-mono font-bold">{metrics.presence?.eye_contact_ratio || 0}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Gesture Rate</div>
                  <div className="text-2xl font-mono font-bold">{metrics.presence?.gesture_rate || 0}/min</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">First Impression</div>
                  <div className="text-2xl font-mono font-bold">{metrics.presence?.first_impression_score || 0}</div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="gravitas" className="bg-card border border-border rounded-xl px-6">
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-center justify-between w-full pr-4">
                <span className="font-display text-xl font-semibold">Gravitas (25%)</span>
                <span className="font-mono text-2xl font-bold text-accent">{Math.round(report.gravitas_score)}</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              <div className="grid md:grid-cols-2 gap-4">
                {[
                  { label: 'Commanding Presence', score: metrics.gravitas?.commanding_presence },
                  { label: 'Decisiveness', score: metrics.gravitas?.decisiveness },
                  { label: 'Poise Under Pressure', score: metrics.gravitas?.poise_under_pressure },
                  { label: 'Emotional Intelligence', score: metrics.gravitas?.emotional_intelligence },
                  { label: 'Vision Articulation', score: metrics.gravitas?.vision_articulation },
                ].map((item, idx) => (
                  <div key={idx} className="bg-secondary/30 p-4 rounded-lg">
                    <div className="text-sm text-muted-foreground mb-1">{item.label}</div>
                    <div className="text-2xl font-mono font-bold">{item.score ? Math.round(item.score) : 'N/A'}</div>
                  </div>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="storytelling" className="bg-card border border-border rounded-xl px-6">
            <AccordionTrigger className="hover:no-underline">
              <div className="flex items-center justify-between w-full pr-4">
                <span className="font-display text-xl font-semibold">Storytelling (15%)</span>
                <span className="font-mono text-2xl font-bold text-accent">
                  {report.storytelling_score ? Math.round(report.storytelling_score) : 'N/A'}
                </span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4">
              {!metrics.storytelling?.has_story ? (
                <p className="text-muted-foreground">No clear story structure detected in this video.</p>
              ) : (
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    { label: 'Narrative Structure', score: metrics.storytelling?.narrative_structure },
                    { label: 'Authenticity', score: metrics.storytelling?.authenticity },
                    { label: 'Concreteness', score: metrics.storytelling?.concreteness },
                    { label: 'Pacing', score: metrics.storytelling?.pacing },
                  ].map((item, idx) => (
                    <div key={idx} className="bg-secondary/30 p-4 rounded-lg">
                      <div className="text-sm text-muted-foreground mb-1">{item.label}</div>
                      <div className="text-2xl font-mono font-bold">{item.score ? Math.round(item.score) : 'N/A'}</div>
                    </div>
                  ))}
                </div>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <Card className="mt-12 p-8 bg-accent/5 border-accent/20">
          <h2 className="font-display text-2xl font-bold mb-6">Coaching Recommendations</h2>
          <div className="space-y-3">
            {(report.coaching_tips || []).map((tip, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-accent flex items-center justify-center text-white text-sm font-bold flex-shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <p className="text-foreground">{tip}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SharedReport;
