import os
import asyncio
import openai
from typing import Dict, Any
import json
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class NLPAnalysisService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = openai.OpenAI(api_key=api_key)
    
    async def analyze_gravitas(self, transcript: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        profile_context = ""
        if user_profile:
            profile_context = f"\n\n**Speaker Profile:**\n- Role: {user_profile.get('role', 'Executive')}\n- Seniority: {user_profile.get('seniority_level', 'Senior')}\n- Experience: {user_profile.get('years_experience', 5)} years\n- Industry: {user_profile.get('industry', 'Technology')}\n\nIMPORTANT: Evaluate this speaker against the standards expected for their specific role and seniority level. A {user_profile.get('role', 'Executive')} at {user_profile.get('seniority_level', 'Senior')} level should demonstrate authority, strategic thinking, and leadership appropriate to this position.\n"
        
        prompt = f"""Analyze this executive's transcript for GRAVITAS indicators. Score each dimension 0-100:{profile_context}

**Transcript:**
{transcript}

**Gravitas Dimensions:**
1. **Commanding Presence**: Directness, confident language, reduced hedging
2. **Decisiveness**: Clear decisions, reasoning with 'because/therefore', closure statements
3. **Poise Under Pressure**: Calm framing, problem decomposition when discussing challenges
4. **Emotional Intelligence**: Empathy markers, stakeholder framing, ownership, respectful language
5. **Vision Articulation**: Clear why/what/how, outcomes, strategic alignment

Provide JSON response:
{{
  "commanding_presence": float,
  "decisiveness": float,
  "poise_under_pressure": float,
  "emotional_intelligence": float,
  "vision_articulation": float,
  "overall_gravitas": float,
  "key_observations": ["point 1", "point 2"]
}}"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            
            result_text = response.choices[0].message.content
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                result = json.loads(result_text[json_start:json_end])
            else:
                result = self._default_gravitas()
            
            return result
        except Exception as e:
            return self._default_gravitas(error=str(e))
    
    async def analyze_storytelling(self, transcript: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        profile_context = ""
        if user_profile:
            profile_context = f"\n\n**Speaker Profile:** {user_profile.get('role', 'Executive')} ({user_profile.get('seniority_level', 'Senior')} level). Evaluate storytelling effectiveness appropriate for this leadership level.\n"
        
        prompt = f"""Analyze this transcript for STORYTELLING quality:{profile_context}

**Transcript:**
{transcript}

**Analysis:**
1. Does it contain a story with setup → conflict → resolution?
2. If YES, score these (0-100):
   - Narrative Structure: Clear beginning/middle/end
   - Authenticity: First-person lessons, reflections, responsibility
   - Concreteness: Specific details and examples
   - Pacing: Story portion as % of total
3. If NO story detected, return has_story: false

JSON response:
{{
  "has_story": bool,
  "narrative_structure": float or null,
  "authenticity": float or null,
  "concreteness": float or null,
  "pacing": float or null,
  "story_excerpt": "brief excerpt" or null,
  "observations": ["point 1", "point 2"]
}}"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                result = json.loads(result_text[json_start:json_end])
            else:
                result = {"has_story": False}
            
            return result
        except Exception as e:
            return {"has_story": False, "error": str(e)}
    
    async def generate_coaching_tips(self, all_metrics: Dict[str, Any]) -> list:
        prompt = f"""Based on these EP metrics, provide 5-7 actionable coaching tips:

**Metrics Summary:**
{json.dumps(all_metrics, indent=2)}

Generate coaching tips that are:
- Specific and actionable
- Supportive and constructive
- Mapped to weak areas
- Include 1-2 positive reinforcements

Return JSON array: ["tip 1", "tip 2", ...]"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            
            result_text = response.choices[0].message.content
            json_start = result_text.find('[')
            json_end = result_text.rfind(']') + 1
            
            if json_start != -1 and json_end != 0:
                tips = json.loads(result_text[json_start:json_end])
                return tips[:7]
            else:
                return self._default_tips()
        except Exception as e:
            return self._default_tips()
    
    def _default_gravitas(self, error=None):
        return {
            "commanding_presence": 60.0,
            "decisiveness": 60.0,
            "poise_under_pressure": 60.0,
            "emotional_intelligence": 60.0,
            "vision_articulation": 60.0,
            "overall_gravitas": 60.0,
            "key_observations": ["Analysis unavailable"],
            "error": error
        }
    
    def _default_tips(self):
        return [
            "Practice strategic pauses before key points",
            "Reduce filler words with deliberate pacing",
            "Maintain eye contact with the camera lens",
            "Use concrete examples to support your points",
            "Frame challenges as opportunities for growth"
        ]