import os
import sys
import tempfile
import asyncio
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorDatabase
from services.transcription import TranscriptionService
from services.audio_analysis import AudioAnalysisService
from services.vision_analysis import VisionAnalysisService
from services.nlp_analysis import NLPAnalysisService
from utils.gridfs_helper import get_video_from_gridfs
import uuid
from datetime import datetime, timezone

class VideoProcessorService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.transcription_service = TranscriptionService()
        self.audio_service = AudioAnalysisService()
        self.vision_service = VisionAnalysisService()
        self.nlp_service = NLPAnalysisService()
    
    async def update_job_status(self, job_id: str, status: str, progress: float, step: str, extra_fields: dict | None = None):
        update = {
            "status": status,
            "progress": progress,
            "current_step": step,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if extra_fields:
            update.update(extra_fields)
        await self.db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": update}
        )
    
    async def process_video(self, job_id: str, video_id: str, user_id: str):
        try:
            await self.update_job_status(job_id, "transcribing", 10, "Extracting audio...")
            
            video_data = await get_video_from_gridfs(self.db, video_id)
            
            # Get video metadata to determine actual format
            metadata = await self.db.video_metadata.find_one({"video_id": video_id}, {"_id": 0})
            content_type = metadata.get("format", "video/mp4") if metadata else "video/mp4"
            filename = metadata.get("filename", "video.mp4") if metadata else "video.mp4"
            
            # Determine file extension based on content type or filename
            if "webm" in content_type.lower() or filename.lower().endswith(".webm"):
                suffix = ".webm"
            elif "quicktime" in content_type.lower() or filename.lower().endswith(".mov"):
                suffix = ".mov"
            elif "avi" in content_type.lower() or filename.lower().endswith(".avi"):
                suffix = ".avi"
            else:
                suffix = ".mp4"
            
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_video:
                temp_video.write(video_data)
                video_path = temp_video.name
            
            print(f"Processing video: {video_path}, content_type: {content_type}, filename: {filename}")
            
            audio_path = await self.transcription_service.extract_audio_from_video(video_path)
            
            await self.update_job_status(job_id, "transcribing", 20, "Transcribing speech...")
            transcription_result = await self.transcription_service.transcribe_audio(audio_path)
            
            transcript = transcription_result["text"]
            words = transcription_result.get("words", [])
            duration = transcription_result.get("duration", 180)
            
            await self.update_job_status(job_id, "audio_analysis", 35, "Analyzing speech patterns...")
            
            speaking_rate = self.audio_service.analyze_speaking_rate(transcript, duration)
            pauses = self.audio_service.detect_pauses(words)
            filler_analysis = self.audio_service.detect_filler_words(transcript, words)
            vocal_metrics = await self.audio_service.analyze_vocal_metrics(audio_path)
            sentence_clarity = self.audio_service.analyze_sentence_clarity(transcript)
            
            communication_metrics = {
                "speaking_rate": speaking_rate,
                "pauses": pauses,
                "filler_words": filler_analysis,
                "vocal_metrics": vocal_metrics,
                "sentence_clarity": sentence_clarity
            }
            
            await self.update_job_status(job_id, "video_analysis", 50, "Analyzing visual presence...")
            
            frames = self.vision_service.extract_frames(video_path, fps=2)
            vision_result = await self.vision_service.analyze_with_gpt4o(frames)
            
            presence_metrics = {
                "posture_score": vision_result.get("posture_score", 0),
                "eye_contact_ratio": vision_result.get("eye_contact_ratio", 0),
                "facial_expressions": vision_result.get("facial_expressions", {}),
                "gesture_rate": vision_result.get("gesture_rate", 0),
                "first_impression_score": vision_result.get("first_impression_score", 0)
            }
            
            await self.update_job_status(job_id, "nlp_analysis", 70, "Analyzing leadership signals...")
            
            user_profile = await self.db.user_profiles.find_one({"user_id": user_id}, {"_id": 0})
            
            gravitas_analysis = await self.nlp_service.analyze_gravitas(transcript, user_profile)
            storytelling_analysis = await self.nlp_service.analyze_storytelling(transcript, user_profile)
            
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
            
            coaching_tips = await self.nlp_service.generate_coaching_tips(all_metrics)
            
            report_id = f"report_{uuid.uuid4().hex}"
            report_doc = {
                "report_id": report_id,
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
            
            await self.db.ep_reports.insert_one(report_doc)
            
            await self.update_job_status(job_id, "completed", 100, "Report generated", extra_fields={"report_id": report_id})
            
            os.unlink(video_path)
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            return report_id
            
        except Exception as e:
            await self.db.video_jobs.update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            raise e
    
    def _calculate_scores(self, comm_metrics, presence_metrics, gravitas_analysis, storytelling_analysis):
        comm_score = self._calculate_communication_score(comm_metrics)
        presence_score = self._calculate_presence_score(presence_metrics)
        gravitas_score = gravitas_analysis.get("overall_gravitas", 60)
        storytelling_score = self._calculate_storytelling_score(storytelling_analysis)
        
        weights = {
            "gravitas": 0.25,
            "communication": 0.35,
            "presence": 0.25,
            "storytelling": 0.15
        }
        
        if storytelling_score is None:
            weights = {
                "gravitas": 0.30,
                "communication": 0.40,
                "presence": 0.30
            }
            overall = (gravitas_score * weights["gravitas"] +
                      comm_score * weights["communication"] +
                      presence_score * weights["presence"])
        else:
            overall = (gravitas_score * weights["gravitas"] +
                      comm_score * weights["communication"] +
                      presence_score * weights["presence"] +
                      storytelling_score * weights["storytelling"])
        
        return {
            "overall": round(overall, 1),
            "gravitas": round(gravitas_score, 1),
            "communication": round(comm_score, 1),
            "presence": round(presence_score, 1),
            "storytelling": round(storytelling_score, 1) if storytelling_score else None
        }
    
    def _calculate_communication_score(self, metrics):
        wpm = metrics["speaking_rate"]["wpm"]
        wpm_score = max(0, 100 - abs(wpm - 150) * 2)
        
        filler_rate = metrics["filler_words"]["rate_per_minute"]
        filler_score = max(0, 100 - filler_rate * 20)
        
        pause_count = len(metrics["pauses"])
        pause_score = min(100, 60 + pause_count * 2)
        
        return (wpm_score * 0.4 + filler_score * 0.3 + pause_score * 0.3)
    
    def _calculate_presence_score(self, metrics):
        posture = metrics.get("posture_score", 50)
        eye_contact = metrics.get("eye_contact_ratio", 0.5) * 100
        
        facial = metrics.get("facial_expressions", {})
        facial_score = facial.get("positive", 40) + facial.get("neutral", 30) * 0.5
        
        return (posture * 0.35 + eye_contact * 0.35 + facial_score * 0.30)
    
    def _calculate_storytelling_score(self, analysis):
        if not analysis.get("has_story", False):
            return None
        
        structure = analysis.get("narrative_structure", 60)
        authenticity = analysis.get("authenticity", 60)
        concreteness = analysis.get("concreteness", 60)
        pacing = analysis.get("pacing", 60)
        
        return (structure * 0.3 + authenticity * 0.3 + concreteness * 0.25 + pacing * 0.15)