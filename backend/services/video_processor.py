import os
import sys
import tempfile
import asyncio
sys.path.append('/app/backend')

from supabase import create_client, Client
from services.transcription import TranscriptionService
from services.audio_analysis import AudioAnalysisService
from services.vision_analysis import VisionAnalysisService
from services.nlp_analysis import NLPAnalysisService
from utils.gridfs_helper import get_video_from_storage
import uuid
from datetime import datetime, timezone

class VideoProcessorService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
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
        
        try:
            self.supabase.table("processing_jobs").update(update).eq("id", job_id).execute()
        except Exception as e:
            print(f"Failed to update job status: {str(e)}")
    
    async def process_video(self, job_id: str, video_id: str, user_id: str):
        try:
            await self.update_job_status(job_id, "transcribing", 10, "Extracting audio...")
            
            video_data = await get_video_from_storage(video_id)
            
            # Get video metadata to determine actual format
            try:
                metadata_response = self.supabase.table("video_metadata").select("*").eq("id", video_id).execute()
                metadata = metadata_response.data[0] if metadata_response.data else {}
                content_type = metadata.get("format", "video/mp4") if metadata else "video/mp4"
                filename = metadata.get("filename", "video.mp4") if metadata else "video.mp4"
            except Exception as e:
                print(f"Failed to get video metadata: {str(e)}")
                content_type = "video/mp4"
                filename = "video.mp4"
            
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
            
            # Get user profile
            try:
                profile_response = self.supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
                user_profile = profile_response.data[0] if profile_response.data else {}
            except Exception as e:
                print(f"Failed to get user profile: {str(e)}")
                user_profile = {}
            
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
            
            try:
                self.supabase.table("ep_reports").insert(report_doc).execute()
            except Exception as e:
                print(f"Failed to insert report: {str(e)}")
            
            await self.update_job_status(job_id, "completed", 100, "Report generated", extra_fields={"report_id": report_id})
            
            os.unlink(video_path)
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            return report_id
            
        except Exception as e:
            try:
                self.supabase.table("processing_jobs").update(
                    {
                        "status": "failed",
                        "error": str(e),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                ).eq("id", job_id).execute()
            except Exception as update_error:
                print(f"Failed to update job status to failed: {str(update_error)}")
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
        # Simple scoring algorithm - can be improved
        rate_score = min(100, max(0, 100 - abs(metrics["speaking_rate"] - 150) / 2))
        clarity_score = metrics["sentence_clarity"].get("clarity_score", 50)
        filler_score = 100 - (metrics["filler_words"].get("count", 0) * 5)
        pause_score = metrics["pauses"].get("pause_balance_score", 50)
        
        return (rate_score * 0.3 + clarity_score * 0.3 + filler_score * 0.2 + pause_score * 0.2)
    
    def _calculate_presence_score(self, metrics):
        # Simple scoring algorithm - can be improved
        posture_score = metrics.get("posture_score", 50)
        eye_contact_score = metrics.get("eye_contact_ratio", 0) * 100
        gesture_score = min(100, metrics.get("gesture_rate", 0) * 20)  # Normalize to 0-100
        first_impression_score = metrics.get("first_impression_score", 50)
        
        return (posture_score * 0.3 + eye_contact_score * 0.3 + gesture_score * 0.2 + first_impression_score * 0.2)
    
    def _calculate_storytelling_score(self, analysis):
        if not analysis:
            return None
        
        # Simple scoring algorithm - can be improved
        structure_score = analysis.get("structure_score", 50)
        emotional_score = analysis.get("emotional_engagement_score", 50)
        clarity_score = analysis.get("clarity_score", 50)
        
        return (structure_score * 0.4 + emotional_score * 0.3 + clarity_score * 0.3)