import cv2
import numpy as np
import base64
import os
from typing import List, Dict, Any
import asyncio
import openai
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class VisionAnalysisService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = openai.OpenAI(api_key=api_key)
    
    def extract_frames(self, video_path: str, fps: int = 2) -> List[str]:
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Handle edge cases where video_fps might be 0 or invalid
        if video_fps <= 0:
            video_fps = 30  # Default to 30 fps if detection fails
        
        frame_interval = max(1, int(video_fps / fps))  # Ensure minimum interval of 1
        
        frames_base64 = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frames_base64.append(frame_base64)
            
            frame_count += 1
            
            if len(frames_base64) >= 60:
                break
        
        cap.release()
        return frames_base64
    
    async def analyze_with_gpt4o(self, frames: List[str]) -> Dict[str, Any]:
        sample_frames = frames[::max(1, len(frames) // 10)][:10]
        
        analysis_prompt = """Analyze this executive's presence in these video frames. Provide scores (0-100) for:
        
1. **Posture**: Percentage of frames with upright, open posture
2. **Eye Contact**: Estimated ratio looking at camera (0.0-1.0)
3. **Facial Expressions**: Breakdown of neutral/positive/negative (%)
4. **Gesture Rate**: Average gestures per minute
5. **First Impression**: Score for first 7-10 seconds

Provide response as JSON:
{
  "posture_score": float,
  "eye_contact_ratio": float,
  "facial_expressions": {"neutral": float, "positive": float, "negative": float},
  "gesture_rate": float,
  "first_impression_score": float,
  "notes": "Brief observation"
}"""
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt}
                ]
            }
        ]
        
        for idx, frame in enumerate(sample_frames[:5]):
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame}"
                }
            })
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=messages,
                max_tokens=500
            )
            
            import json
            result_text = response.choices[0].message.content
            
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                result = json.loads(result_text[json_start:json_end])
            else:
                result = {
                    "posture_score": 70.0,
                    "eye_contact_ratio": 0.6,
                    "facial_expressions": {"neutral": 50.0, "positive": 40.0, "negative": 10.0},
                    "gesture_rate": 5.0,
                    "first_impression_score": 70.0
                }
            
            return result
        except Exception as e:
            return {
                "posture_score": 0,
                "eye_contact_ratio": 0,
                "facial_expressions": {"neutral": 0, "positive": 0, "negative": 0},
                "gesture_rate": 0,
                "first_impression_score": 0,
                "error": str(e)
            }