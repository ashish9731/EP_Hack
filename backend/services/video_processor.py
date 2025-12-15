import os
import sys
import tempfile
import asyncio
sys.path.append('/app/backend')

from services.transcription import TranscriptionService
from services.audio_analysis import AudioAnalysisService
from services.vision_analysis import VisionAnalysisService
from services.nlp_analysis import NLPAnalysisService
from utils.gridfs_helper import get_video_from_storage
import uuid
from datetime import datetime, timezone

class VideoProcessorService:
    def __init__(self):
        self.transcription_service = TranscriptionService()
        self.audio_service = AudioAnalysisService()
        self.vision_service = VisionAnalysisService()
        self.nlp_service = NLPAnalysisService()
    
    async def update_job_status(self, job_id: str, status: str, progress: float, step: str, extra_fields: dict | None = None):
        # Mock implementation - in a real application, you would update a database
        print(f"Updating job {job_id} status: {status}, progress: {progress}%, step: {step}")
    
    async def process_video(self, job_id: str, video_id: str, user_id: str):
        try:
            await self.update_job_status(job_id, "transcribing", 10, "Extracting audio...")
            
            video_data = get_video_from_storage(video_id)
            
            # Mock video metadata
            content_type = video_data.get("content_type", "video/mp4")
            filename = video_data.get("filename", "video.mp4")
            
            # Determine file extension based on content type or filename
            if "webm" in content_type.lower() or filename.lower().endswith(".webm"):
                suffix = ".webm"
            elif "quicktime" in content_type.lower() or filename.lower().endswith(".mov"):
                suffix = ".mov"
            elif "avi" in content_type.lower() or filename.lower().endswith(".avi"):
                suffix = ".avi"
            else:
                suffix = ".mp4"
            
            # Create temporary files for processing
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_video:
                temp_video.write(video_data["content"])
                video_path = temp_video.name
            
            print(f"Processing video: {video_path}, content_type: {content_type}, filename: {filename}")
            
            # Mock audio extraction
            audio_path = video_path.replace(suffix, ".wav")
            with open(audio_path, "w") as f:
                f.write("mock audio content")
            
            await self.update_job_status(job_id, "transcribing", 20, "Transcribing speech...")
            # Mock transcription result
            transcription_result = {
                "text": "This is a mock transcription of the video content.",
                "words": [],
                "duration": 180
            }
            
            transcript = transcription_result["text"]
            words = transcription_result.get("words", [])
            duration = transcription_result.get("duration", 180)
            
            await self.update_job_status(job_id, "audio_analysis", 35, "Analyzing speech patterns...")
            
            # Mock audio analysis
            communication_metrics = {
                "speaking_rate": {"rate": 150, "assessment": "good"},
                "pauses": {"count": 5, "distribution": "even"},
                "filler_words": {"count": 3, "types": ["um", "uh"]},
                "vocal_metrics": {"pitch_variation": "moderate", "volume_consistency": "good"},
                "sentence_clarity": {"score": 85, "feedback": "Clear articulation"}
            }
            
            await self.update_job_status(job_id, "video_analysis", 50, "Analyzing visual presence...")
            
            # Mock vision analysis
            presence_metrics = {
                "posture_score": 80,
                "eye_contact_ratio": 0.75,
                "facial_expressions": {"smile_frequency": 0.3, "expression_variety": "moderate"},
                "gesture_rate": 12,
                "first_impression_score": 82
            }
            
            await self.update_job_status(job_id, "nlp_analysis", 70, "Analyzing leadership signals...")
            
            # Mock user profile
            user_profile = {}
            
            # Mock NLP analysis
            gravitas_analysis = {
                "overall_gravitas": 78,
                "confidence_indicators": ["clear tone", "measured pace"],
                "authority_indicators": ["declarative statements", "expert vocabulary"]
            }
            
            storytelling_analysis = {
                "narrative_structure": "present",
                "emotional_engagement": "moderate",
                "memorable_elements": ["key_points", "conclusion"]
            }
            
            await self.update_job_status(job_id, "scoring", 85, "Calculating scores...")
            
            scores = self._calculate_scores(
                communication_metrics,
                presence_metrics,
                gravitas_analysis,
                storytelling_analysis
            )
            
            all_metrics = {
                "communication": communication_metrics,
                "presence": presence_metrics,
                "gravitas": gravitas_analysis,
                "storytelling": storytelling_analysis,
                "scores": scores
            }
            
            # Mock coaching tips
            coaching_tips = [
                "Work on maintaining consistent eye contact throughout your presentation",
                "Try to reduce filler words by pausing instead of saying 'um' or 'uh'",
                "Consider varying your vocal tone to maintain audience engagement"
            ]
            
            report_id = f"report_{uuid.uuid4().hex}"
            report_doc = {
                "id": report_id,
                "user_id": user_id,
                "video_id": video_id,
                "job_id": job_id,
                "transcript": transcript,
                "overall_score": scores["overall"],
                "gravitas_score": scores["gravitas"],
                "communication_score": scores["communication"],
                "presence_score": scores["presence"],
                "storytelling_score": scores.get("storytelling"),
                "detailed_metrics": all_metrics,
                "coaching_tips": coaching_tips,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.update_job_status(job_id, "completed", 100, "Report generated", extra_fields={"report_id": report_id})
            
            # Clean up temporary files
            os.unlink(video_path)
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            return report_id
            
        except Exception as e:
            print(f"Video processing failed: {str(e)}")
            raise e
    
    def _calculate_scores(self, comm_metrics, presence_metrics, gravitas_analysis, storytelling_analysis):
        comm_score = 80  # Mock score
        presence_score = 75  # Mock score
        gravitas_score = gravitas_analysis.get("overall_gravitas", 60)
        storytelling_score = 85  # Mock score
        
        weights = {
            "gravitas": 0.25,
            "communication": 0.35,
            "presence": 0.25,
            "storytelling": 0.15
        }
        
        overall = (
            gravitas_score * weights["gravitas"] +
            comm_score * weights["communication"] +
            presence_score * weights["presence"] +
            storytelling_score * weights["storytelling"]
        )
        
        return {
            "overall": round(overall, 1),
            "gravitas": gravitas_score,
            "communication": comm_score,
            "presence": presence_score,
            "storytelling": storytelling_score
        }