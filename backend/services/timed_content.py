"""
Timed Content Service
Manages content rotation for Simulator (3 days), Learning Bytes (daily), Training (weekly)
"""
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import json

class TimedContentService:
    """Service to manage time-based content rotation"""
    
    ROTATION_PERIODS = {
        "simulator": 3,      # days
        "learning": 1,       # days
        "training": 7,       # days
    }
    
    @staticmethod
    def get_period_info(content_type: str) -> Dict[str, Any]:
        """Get current period info including start, end, and remaining time"""
        period_days = TimedContentService.ROTATION_PERIODS.get(content_type, 1)
        now = datetime.now(timezone.utc)
        
        # Calculate period start based on epoch
        epoch = datetime(2024, 1, 1, tzinfo=timezone.utc)
        days_since_epoch = (now - epoch).days
        period_number = days_since_epoch // period_days
        
        period_start = epoch + timedelta(days=period_number * period_days)
        period_end = period_start + timedelta(days=period_days)
        
        remaining = period_end - now
        remaining_seconds = int(remaining.total_seconds())
        remaining_hours = remaining_seconds // 3600
        remaining_minutes = (remaining_seconds % 3600) // 60
        
        return {
            "period_number": period_number,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "remaining_seconds": remaining_seconds,
            "remaining_hours": remaining_hours,
            "remaining_minutes": remaining_minutes,
            "remaining_days": remaining.days,
            "remaining_formatted": TimedContentService._format_remaining(remaining),
            "refresh_period_days": period_days
        }
    
    @staticmethod
    def _format_remaining(remaining: timedelta) -> str:
        """Format remaining time as human-readable string"""
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    @staticmethod
    def get_seed_for_period(content_type: str) -> int:
        """Get a consistent seed for the current period (for random but consistent content)"""
        period_info = TimedContentService.get_period_info(content_type)
        seed_string = f"{content_type}_{period_info['period_number']}"
        return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)


# Pre-defined content pools for rotation
SIMULATOR_SCENARIOS_POOL = [
    # Pool 1 - Crisis Management
    [
        {
            "id": 1,
            "title": "Board Crisis Response",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "Your company's stock dropped 15% overnight due to a competitor announcement. The board wants immediate answers.",
            "prompt": "Address the board: What is your strategic response? How will you stabilize the situation and regain competitive advantage?",
            "focus": ["Decisiveness", "Strategic Thinking", "Poise Under Pressure"]
        },
        {
            "id": 2,
            "title": "Investor Pitch Under Scrutiny",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "You're pitching to investors who just heard concerns about your burn rate and timeline to profitability.",
            "prompt": "Present your financial strategy and growth projections. Address their concerns with confidence and data.",
            "focus": ["Vision Articulation", "Financial Acumen", "Credibility"]
        },
        {
            "id": 3,
            "title": "Hostile Media Interview",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "A journalist is questioning your company's ethics after a whistleblower leak.",
            "prompt": "Respond to tough questions while protecting company reputation and showing accountability.",
            "focus": ["Composure", "Message Control", "Authenticity"]
        },
        {
            "id": 4,
            "title": "Emergency Shareholder Meeting",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "A major product recall has triggered an emergency shareholder meeting. Shareholders are demanding explanations and accountability.",
            "prompt": "Present your crisis management plan, address liability concerns, and restore shareholder confidence.",
            "focus": ["Transparency", "Risk Management", "Executive Presence"]
        },
        {
            "id": 5,
            "title": "Regulatory Investigation Response",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "Your company faces a regulatory investigation. You must address the executive team about compliance and next steps.",
            "prompt": "Outline your response strategy while maintaining team morale and demonstrating leadership during uncertainty.",
            "focus": ["Legal Awareness", "Team Leadership", "Crisis Communication"]
        },
    ],
    # Pool 2 - Leadership Challenges
    [
        {
            "id": 1,
            "title": "Stakeholder Conflict Resolution",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "Two key departments are in conflict over resource allocation, impacting delivery timelines.",
            "prompt": "Present your resolution approach. How will you balance competing needs while maintaining team morale?",
            "focus": ["Emotional Intelligence", "Diplomacy", "Leadership"]
        },
        {
            "id": 2,
            "title": "Executive Town Hall",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "Company-wide layoffs were just announced. Remaining employees are anxious about job security and direction.",
            "prompt": "Address the company with transparency, empathy, and a clear path forward. Rebuild trust and confidence.",
            "focus": ["Authenticity", "Empathy", "Vision Communication"]
        },
        {
            "id": 3,
            "title": "Performance Review Challenge",
            "difficulty": "Low",
            "duration": "2-3 min",
            "situation": "A high-performing team member is demanding a promotion that isn't aligned with company structure.",
            "prompt": "Deliver constructive feedback while retaining this valuable employee. Balance honesty with encouragement.",
            "focus": ["Coaching", "Honest Communication", "Retention Strategy"]
        },
        {
            "id": 4,
            "title": "Team Morale Crisis",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "Your team's productivity has dropped 30% after a failed project. Team members are demoralized and questioning leadership.",
            "prompt": "Address the team to rebuild morale, acknowledge the failure, and reestablish momentum and trust.",
            "focus": ["Motivational Leadership", "Vulnerability", "Resilience"]
        },
        {
            "id": 5,
            "title": "C-Suite Promotion Pitch",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "You're presenting to the CEO for a promotion to the C-suite. They want to know why you're ready for this level of responsibility.",
            "prompt": "Articulate your leadership journey, strategic vision, and what unique value you'll bring to executive leadership.",
            "focus": ["Self-Promotion", "Strategic Vision", "Executive Readiness"]
        },
    ],
    # Pool 3 - Strategic Communication
    [
        {
            "id": 1,
            "title": "Strategic Pivot Announcement",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "Your company is pivoting strategy after 2 years. Some key stakeholders are skeptical.",
            "prompt": "Announce the pivot with conviction. Explain the reasoning, mitigate concerns, and rally support.",
            "focus": ["Change Management", "Strategic Vision", "Persuasion"]
        },
        {
            "id": 2,
            "title": "Merger Integration Address",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "Your company just acquired a competitor. Teams from both companies are uncertain about their futures.",
            "prompt": "Address combined teams about integration plans, culture, and opportunities. Unite two cultures.",
            "focus": ["Unification", "Vision", "Cultural Leadership"]
        },
        {
            "id": 3,
            "title": "Board Budget Defense",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "The board wants to cut your department's budget by 30%. You need to justify your spending.",
            "prompt": "Present ROI data and strategic importance. Make a compelling case for your resources.",
            "focus": ["Data-Driven Argumentation", "Strategic Value", "Negotiation"]
        },
        {
            "id": 4,
            "title": "Q4 Earnings Call",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "Your company missed Q4 targets by 12%. Analysts on the earnings call are pressing for explanations and future outlook.",
            "prompt": "Address analyst concerns with honesty while maintaining market confidence and presenting the path to recovery.",
            "focus": ["Financial Communication", "Market Confidence", "Forward Vision"]
        },
        {
            "id": 5,
            "title": "Customer Crisis Communication",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "A data breach has affected 50,000 customers. You must address them directly about the breach and remediation.",
            "prompt": "Communicate the breach details, actions taken, and customer protection measures with transparency and accountability.",
            "focus": ["Crisis Communication", "Customer Trust", "Accountability"]
        },
    ],
    # Pool 4 - Innovation & Growth
    [
        {
            "id": 1,
            "title": "Innovation Initiative Launch",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "You're launching a new innovation lab but the executive team is skeptical about ROI.",
            "prompt": "Present your vision for innovation, expected outcomes, and why now is the right time.",
            "focus": ["Visionary Leadership", "Persuasion", "Innovation Mindset"]
        },
        {
            "id": 2,
            "title": "International Expansion Pitch",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "You're proposing expansion into a new international market with significant risks.",
            "prompt": "Present market opportunity, risk mitigation strategies, and resource requirements.",
            "focus": ["Global Thinking", "Risk Assessment", "Strategic Planning"]
        },
        {
            "id": 3,
            "title": "Digital Transformation Address",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "Your organization needs to undergo digital transformation. Many employees fear job losses.",
            "prompt": "Present the transformation roadmap with empathy. Address fears while inspiring change.",
            "focus": ["Change Leadership", "Empathy", "Future Vision"]
        },
        {
            "id": 4,
            "title": "IPO Roadshow Pitch",
            "difficulty": "High",
            "duration": "2-3 min",
            "situation": "Your company is going public. You're presenting to institutional investors who will determine your valuation.",
            "prompt": "Present your company's growth story, competitive advantages, and vision with conviction and clarity.",
            "focus": ["Storytelling", "Market Positioning", "Financial Confidence"]
        },
        {
            "id": 5,
            "title": "Sustainability Initiative Pitch",
            "difficulty": "Medium",
            "duration": "2-3 min",
            "situation": "You're proposing a major sustainability initiative that requires significant investment but uncertain short-term ROI.",
            "prompt": "Make the business case for sustainability, balancing environmental responsibility with stakeholder value.",
            "focus": ["Purpose-Driven Leadership", "Long-term Thinking", "Stakeholder Balance"]
        },
    ],
]

TRAINING_MODULES_POOL = [
    # Week 1 - Communication Fundamentals
    [
        {"id": "strategic-pauses", "title": "Strategic Pauses", "description": "Master the art of using silence to enhance authority", "duration": "8 min", "difficulty": "Beginner", "focus_area": "Communication"},
        {"id": "filler-elimination", "title": "Eliminating Filler Words", "description": "Remove 'um', 'uh', and other verbal fillers", "duration": "10 min", "difficulty": "Beginner", "focus_area": "Communication"},
        {"id": "speaking-rate", "title": "Optimal Speaking Rate", "description": "Find your ideal pace for maximum impact", "duration": "7 min", "difficulty": "Beginner", "focus_area": "Communication"},
        {"id": "vocal-variety", "title": "Vocal Variety & Modulation", "description": "Use pitch, pace, and volume for engagement", "duration": "9 min", "difficulty": "Intermediate", "focus_area": "Communication"},
    ],
    # Week 2 - Presence & Body Language
    [
        {"id": "lens-eye-contact", "title": "Camera Lens Eye Contact", "description": "Develop consistent camera presence", "duration": "6 min", "difficulty": "Beginner", "focus_area": "Presence"},
        {"id": "power-posture", "title": "Power Posture Techniques", "description": "Project confidence through body language", "duration": "8 min", "difficulty": "Beginner", "focus_area": "Presence"},
        {"id": "gesture-mastery", "title": "Gesture Mastery", "description": "Use hand gestures to emphasize key points", "duration": "10 min", "difficulty": "Intermediate", "focus_area": "Presence"},
        {"id": "first-impressions", "title": "First Impressions", "description": "Command attention in the first 7 seconds", "duration": "7 min", "difficulty": "Beginner", "focus_area": "Presence"},
    ],
    # Week 3 - Gravitas Building
    [
        {"id": "decision-framing", "title": "Executive Decision Framing", "description": "Structure decisions with clarity and conviction", "duration": "10 min", "difficulty": "Intermediate", "focus_area": "Gravitas"},
        {"id": "commanding-presence", "title": "Commanding Presence", "description": "Project authority without arrogance", "duration": "12 min", "difficulty": "Advanced", "focus_area": "Gravitas"},
        {"id": "poise-under-pressure", "title": "Poise Under Pressure", "description": "Stay calm when challenged or questioned", "duration": "9 min", "difficulty": "Intermediate", "focus_area": "Gravitas"},
        {"id": "vision-articulation", "title": "Vision Articulation", "description": "Communicate strategic vision clearly", "duration": "11 min", "difficulty": "Advanced", "focus_area": "Gravitas"},
    ],
    # Week 4 - Storytelling & Narrative
    [
        {"id": "story-structure", "title": "Story Structure Basics", "description": "Build compelling narratives with arc", "duration": "10 min", "difficulty": "Beginner", "focus_area": "Storytelling"},
        {"id": "personal-anecdotes", "title": "Personal Anecdotes", "description": "Use your experiences to connect", "duration": "8 min", "difficulty": "Intermediate", "focus_area": "Storytelling"},
        {"id": "data-storytelling", "title": "Data Storytelling", "description": "Make numbers memorable and meaningful", "duration": "12 min", "difficulty": "Advanced", "focus_area": "Storytelling"},
        {"id": "emotional-hooks", "title": "Emotional Hooks", "description": "Create lasting impressions with emotion", "duration": "9 min", "difficulty": "Intermediate", "focus_area": "Storytelling"},
    ],
]

LEARNING_TIPS_POOL = [
    # Different tips for each day cycle
    {"category": "Communication", "tip": "Practice the 'power pause' - a 2-3 second silence before your key message makes it 40% more memorable. Use it before important points in your next presentation."},
    {"category": "Presence", "tip": "The 'triangle gaze' technique: When speaking, shift your eye contact between three points in your audience (or camera lens corners) to appear engaged yet commanding."},
    {"category": "Gravitas", "tip": "Replace 'I think' with 'I believe' or 'My recommendation is' - this single word swap increases perceived confidence by 35% according to leadership studies."},
    {"category": "Storytelling", "tip": "Start your next presentation with 'Let me share what happened...' - stories are 22x more memorable than facts alone."},
    {"category": "Communication", "tip": "The 10-second rule: Your first 10 seconds set the tone. Open with a bold statement, surprising fact, or thought-provoking question."},
    {"category": "Presence", "tip": "Before important meetings, do a 2-minute 'power pose' in private - research shows it increases testosterone and decreases cortisol."},
    {"category": "Gravitas", "tip": "When challenged, pause before responding. This 3-second pause signals thoughtfulness and prevents defensive reactions."},
    {"category": "Storytelling", "tip": "Use the 'hero's journey' mini-version: Challenge → Action → Result. Even a 30-second story following this structure captivates."},
    {"category": "Communication", "tip": "Mirror your audience's speaking pace initially, then gradually slow down. This builds rapport and gives you control of the room."},
    {"category": "Presence", "tip": "Position your camera at eye level and ensure your face fills 60% of the frame. This creates optimal virtual presence."},
    {"category": "Gravitas", "tip": "End meetings with a clear 'next step' statement. Leaders who do this are perceived as 50% more decisive."},
    {"category": "Storytelling", "tip": "Include one specific sensory detail in your stories ('the cold conference room', 'the 3am email'). Specificity creates believability."},
    {"category": "Communication", "tip": "Practice 'bottom-line up front' (BLUF): State your conclusion first, then provide supporting details. Executives prefer this 3:1."},
    {"category": "Presence", "tip": "Keep your chin parallel to the ground - tilting up appears arrogant, tilting down appears submissive. Neutral conveys confidence."},
]


def get_current_simulator_scenarios() -> Dict[str, Any]:
    """Get current simulator scenarios based on 3-day rotation"""
    period_info = TimedContentService.get_period_info("simulator")
    seed = TimedContentService.get_seed_for_period("simulator")
    
    # Select scenarios based on period
    pool_index = period_info["period_number"] % len(SIMULATOR_SCENARIOS_POOL)
    scenarios = SIMULATOR_SCENARIOS_POOL[pool_index]
    
    return {
        "scenarios": scenarios,
        "rotation_info": period_info,
        "pool_name": f"Scenario Set {pool_index + 1}"
    }


def get_current_training_modules() -> Dict[str, Any]:
    """Get current training modules based on weekly rotation"""
    period_info = TimedContentService.get_period_info("training")
    
    # Select modules based on period
    pool_index = period_info["period_number"] % len(TRAINING_MODULES_POOL)
    modules = TRAINING_MODULES_POOL[pool_index]
    
    week_themes = ["Communication Fundamentals", "Presence & Body Language", "Gravitas Building", "Storytelling & Narrative"]
    
    return {
        "modules": modules,
        "rotation_info": period_info,
        "week_theme": week_themes[pool_index],
        "week_number": pool_index + 1
    }


def get_current_daily_tip() -> Dict[str, Any]:
    """Get current daily tip based on daily rotation"""
    period_info = TimedContentService.get_period_info("learning")
    
    # Select tip based on period
    tip_index = period_info["period_number"] % len(LEARNING_TIPS_POOL)
    tip = LEARNING_TIPS_POOL[tip_index]
    
    return {
        "tip": tip["tip"],
        "category": tip["category"],
        "rotation_info": period_info,
        "tip_number": tip_index + 1,
        "total_tips": len(LEARNING_TIPS_POOL)
    }
