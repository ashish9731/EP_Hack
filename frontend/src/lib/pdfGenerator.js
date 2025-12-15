import jsPDF from 'jspdf';

/**
 * Generates a professional PDF report for Executive Presence analysis
 */
export const generateEPReportPDF = (report) => {
  const pdf = new jsPDF('p', 'mm', 'a4');
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - 2 * margin;
  let yPos = margin;
  
  // Colors
  const gold = [212, 175, 55];
  const darkText = [15, 23, 42];
  const grayText = [100, 116, 139];
  const lightBg = [248, 250, 252];
  
  // Helper functions
  const addText = (text, x, y, options = {}) => {
    const {
      fontSize = 12,
      color = darkText,
      fontStyle = 'normal',
      maxWidth = contentWidth,
      align = 'left'
    } = options;
    
    pdf.setFontSize(fontSize);
    pdf.setTextColor(...color);
    pdf.setFont('helvetica', fontStyle);
    
    if (align === 'center') {
      pdf.text(text, pageWidth / 2, y, { align: 'center', maxWidth });
    } else if (align === 'right') {
      pdf.text(text, pageWidth - margin, y, { align: 'right', maxWidth });
    } else {
      pdf.text(text, x, y, { maxWidth });
    }
  };
  
  const addSection = (title, y) => {
    pdf.setFillColor(...lightBg);
    pdf.rect(margin, y - 5, contentWidth, 12, 'F');
    pdf.setDrawColor(...gold);
    pdf.setLineWidth(0.5);
    pdf.line(margin, y - 5, margin + 3, y - 5);
    pdf.line(margin, y - 5, margin, y + 7);
    addText(title, margin + 5, y + 3, { fontSize: 14, fontStyle: 'bold', color: darkText });
    return y + 18;
  };
  
  const addScoreBox = (label, score, x, y, width = 40) => {
    pdf.setFillColor(255, 255, 255);
    pdf.setDrawColor(...gold);
    pdf.setLineWidth(0.5);
    pdf.roundedRect(x, y, width, 25, 3, 3, 'FD');
    
    addText(label, x + width/2, y + 8, { fontSize: 9, color: grayText, align: 'center' });
    addText(score !== null ? Math.round(score).toString() : 'N/A', x + width/2, y + 18, { 
      fontSize: 16, 
      fontStyle: 'bold', 
      color: score >= 70 ? [34, 197, 94] : score >= 50 ? gold : [239, 68, 68],
      align: 'center'
    });
  };
  
  const getScoreLabel = (score) => {
    if (score >= 90) return { label: 'Exceptional', color: [34, 197, 94] };
    if (score >= 80) return { label: 'Excellent', color: [34, 197, 94] };
    if (score >= 70) return { label: 'Strong', color: gold };
    if (score >= 60) return { label: 'Developing', color: gold };
    if (score >= 50) return { label: 'Emerging', color: [245, 158, 11] };
    return { label: 'Needs Focus', color: [239, 68, 68] };
  };
  
  // ===== PAGE 1: HEADER & OVERALL SCORE =====
  
  // Header bar
  pdf.setFillColor(...gold);
  pdf.rect(0, 0, pageWidth, 35, 'F');
  
  addText('EXECUTIVE PRESENCE QUOTIENT', margin, 15, { fontSize: 18, fontStyle: 'bold', color: [255, 255, 255] });
  addText('AI-Powered Leadership Assessment Report', margin, 25, { fontSize: 11, color: [255, 255, 255] });
  
  // Date
  const reportDate = report.created_at ? new Date(report.created_at).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric'
  }) : new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  addText(reportDate, 0, 25, { fontSize: 10, color: [255, 255, 255], align: 'right' });
  
  yPos = 55;
  
  // Overall Score Section
  const scoreInfo = getScoreLabel(report.overall_score);
  
  pdf.setFillColor(...lightBg);
  pdf.roundedRect(margin, yPos, contentWidth, 50, 5, 5, 'F');
  pdf.setDrawColor(...gold);
  pdf.setLineWidth(1);
  pdf.roundedRect(margin, yPos, contentWidth, 50, 5, 5, 'S');
  
  // Large score
  addText(report.overall_score?.toString() || 'N/A', margin + 30, yPos + 32, { 
    fontSize: 42, 
    fontStyle: 'bold', 
    color: gold 
  });
  addText('Overall EP Score', margin + 30, yPos + 42, { fontSize: 10, color: grayText });
  
  // Score interpretation
  addText(scoreInfo.label, margin + 100, yPos + 20, { fontSize: 24, fontStyle: 'bold', color: scoreInfo.color });
  addText('Performance Level', margin + 100, yPos + 30, { fontSize: 10, color: grayText });
  
  const benchmarkText = report.overall_score >= 60 ? 
    'Above industry average for executive communication' : 
    'Opportunities identified for improvement';
  addText(benchmarkText, margin + 100, yPos + 42, { fontSize: 10, color: grayText });
  
  yPos += 65;
  
  // Dimension Scores
  addText('DIMENSION BREAKDOWN', margin, yPos, { fontSize: 12, fontStyle: 'bold', color: darkText });
  yPos += 10;
  
  const scoreBoxWidth = (contentWidth - 30) / 4;
  addScoreBox('Gravitas (25%)', report.gravitas_score, margin, yPos, scoreBoxWidth);
  addScoreBox('Communication (35%)', report.communication_score, margin + scoreBoxWidth + 10, yPos, scoreBoxWidth);
  addScoreBox('Presence (25%)', report.presence_score, margin + 2 * (scoreBoxWidth + 10), yPos, scoreBoxWidth);
  addScoreBox('Storytelling (15%)', report.storytelling_score, margin + 3 * (scoreBoxWidth + 10), yPos, scoreBoxWidth);
  
  yPos += 40;
  
  // ===== COMMUNICATION DETAILS =====
  yPos = addSection('Communication Analysis', yPos);
  
  const metrics = report.detailed_metrics || {};
  const commMetrics = metrics.communication || {};
  
  addText(`Speaking Rate: ${commMetrics.speaking_rate?.wpm || 'N/A'} WPM`, margin + 5, yPos, { fontSize: 11 });
  addText('Benchmark: 120-150 WPM ideal for executive communication', margin + 5, yPos + 6, { fontSize: 9, color: grayText });
  yPos += 15;
  
  addText(`Filler Words: ${commMetrics.filler_words?.count || 0} detected (${commMetrics.filler_words?.rate_per_minute || 0}/min)`, margin + 5, yPos, { fontSize: 11 });
  addText('Research: Excessive fillers reduce perceived competence by up to 35% (Journal of Communication)', margin + 5, yPos + 6, { fontSize: 9, color: grayText });
  yPos += 15;
  
  addText(`Strategic Pauses: ${commMetrics.pauses?.length || 0} detected`, margin + 5, yPos, { fontSize: 11 });
  addText('Benchmark: Well-placed pauses increase message retention and authority', margin + 5, yPos + 6, { fontSize: 9, color: grayText });
  yPos += 20;
  
  // ===== PRESENCE DETAILS =====
  yPos = addSection('Presence Analysis', yPos);
  
  const presMetrics = metrics.presence || {};
  
  const presenceItems = [
    { label: 'Posture Score', value: `${presMetrics.posture_score || 0}%`, benchmark: 'Upright posture correlates with authority perception' },
    { label: 'Eye Contact Ratio', value: `${presMetrics.eye_contact_ratio || 0}%`, benchmark: '60-70% eye contact is optimal for trust (MIT Sloan)' },
    { label: 'Gesture Rate', value: `${presMetrics.gesture_rate || 0}/min`, benchmark: 'Natural gestures enhance message delivery' },
    { label: 'First Impression', value: presMetrics.first_impression_score || 'N/A', benchmark: 'First 7 seconds are critical for perception' },
  ];
  
  presenceItems.forEach((item, idx) => {
    addText(`${item.label}: ${item.value}`, margin + 5, yPos, { fontSize: 11 });
    addText(item.benchmark, margin + 5, yPos + 6, { fontSize: 9, color: grayText });
    yPos += 15;
  });
  
  yPos += 5;
  
  // ===== GRAVITAS DETAILS =====
  yPos = addSection('Gravitas Analysis', yPos);
  
  const gravMetrics = metrics.gravitas || {};
  
  const gravitasItems = [
    { label: 'Commanding Presence', score: gravMetrics.commanding_presence },
    { label: 'Decisiveness', score: gravMetrics.decisiveness },
    { label: 'Poise Under Pressure', score: gravMetrics.poise_under_pressure },
    { label: 'Emotional Intelligence', score: gravMetrics.emotional_intelligence },
    { label: 'Vision Articulation', score: gravMetrics.vision_articulation },
  ];
  
  gravitasItems.forEach((item, idx) => {
    const scoreText = item.score ? Math.round(item.score).toString() : 'N/A';
    addText(`${item.label}: ${scoreText}`, margin + 5 + (idx % 2) * 85, yPos + Math.floor(idx / 2) * 12, { fontSize: 11 });
  });
  
  yPos += 40;
  
  // Check if we need a new page
  if (yPos > pageHeight - 80) {
    pdf.addPage();
    yPos = margin;
  }
  
  // ===== STORYTELLING DETAILS =====
  yPos = addSection('Storytelling Analysis', yPos);
  
  const storyMetrics = metrics.storytelling || {};
  
  if (!storyMetrics.has_story) {
    addText('No clear story structure detected in this video.', margin + 5, yPos, { fontSize: 11, color: [245, 158, 11] });
    addText('Recommendation: Include personal anecdotes or challenge-resolution narratives', margin + 5, yPos + 8, { fontSize: 9, color: grayText });
    yPos += 20;
  } else {
    const storyItems = [
      { label: 'Narrative Structure', score: storyMetrics.narrative_structure },
      { label: 'Authenticity', score: storyMetrics.authenticity },
      { label: 'Concreteness', score: storyMetrics.concreteness },
      { label: 'Pacing', score: storyMetrics.pacing },
    ];
    
    storyItems.forEach((item, idx) => {
      const scoreText = item.score ? Math.round(item.score).toString() : 'N/A';
      addText(`${item.label}: ${scoreText}`, margin + 5 + (idx % 2) * 85, yPos + Math.floor(idx / 2) * 12, { fontSize: 11 });
    });
    yPos += 30;
  }
  
  // ===== COACHING RECOMMENDATIONS =====
  if (yPos > pageHeight - 60) {
    pdf.addPage();
    yPos = margin;
  }
  
  yPos = addSection('Coaching Recommendations', yPos);
  
  const tips = report.coaching_tips || [
    'Practice strategic pauses before key points to build anticipation',
    'Reduce filler words by pausing instead of using "um" or "uh"',
    'Maintain consistent eye contact with the camera to build connection',
    'Include more concrete examples and data to strengthen your narrative'
  ];
  
  tips.forEach((tip, idx) => {
    addText(`${idx + 1}. ${tip}`, margin + 5, yPos, { fontSize: 10, maxWidth: contentWidth - 10 });
    yPos += pdf.getTextDimensions(tip, { maxWidth: contentWidth - 10 }).h + 8;
  });
  
  // ===== FOOTER =====
  const addFooter = (pageNum) => {
    pdf.setFillColor(...gold);
    pdf.rect(0, pageHeight - 15, pageWidth, 15, 'F');
    addText('EP Quotient | AI-Powered Executive Presence Assessment', margin, pageHeight - 6, { 
      fontSize: 9, 
      color: [255, 255, 255] 
    });
    addText(`Page ${pageNum}`, 0, pageHeight - 6, { fontSize: 9, color: [255, 255, 255], align: 'right' });
  };
  
  // Add footers to all pages
  const totalPages = pdf.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    pdf.setPage(i);
    addFooter(i);
  }
  
  // Save PDF
  const fileName = `EP_Report_${reportDate.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
  pdf.save(fileName);
  
  return fileName;
};

export default generateEPReportPDF;
