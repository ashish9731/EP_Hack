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
        # In a real application, you would update a database
        # For now, we'll just log the update
        print(f"Updating job {job_id} status: {status}, progress: {progress}%, step: {step}")
        if extra_fields:
            print(f"Extra fields: {extra_fields}")
    
    async def process_video(self, job_id: str, video_id: str, user_id: str):
        try:
            await self.update_job_status(job_id, "transcribing", 10, "Extracting audio...")
            
            # Get video from storage
            video_data = get_video_from_storage(video_id)
            
            # Get video metadata
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
            
            # Extract audio from video
            audio_path = await self.transcription_service.extract_audio_from_video(video_path, content_type)
            
            await self.update_job_status(job_id, "transcribing", 20, "Transcribing speech...")
            
            # Transcribe audio
            transcription_result = await self.transcription_service.transcribe_audio(audio_path)
            
            transcript = transcription_result["text"]
            words = transcription_result.get("words", [])
            duration = transcription_result.get("duration", 180)
            
            await self.update_job_status(job_id, "audio_analysis", 35, "Analyzing speech patterns...")
            
            # Analyze audio metrics
            speaking_rate_analysis = self.audio_service.analyze_speaking_rate(transcript, duration)
            pauses_analysis = self.audio_service.detect_pauses(words)
            filler_words_analysis = self.audio_service.detect_filler_words(transcript, words)
            vocal_metrics_analysis = await self.audio_service.analyze_vocal_metrics(audio_path)
            sentence_clarity_analysis = self.audio_service.analyze_sentence_clarity(transcript)
            
            communication_metrics = {
                "speaking_rate": speaking_rate_analysis,
                "pauses": {
                    "detected": pauses_analysis,
                    "count": len(pauses_analysis),
                    "average_gap": sum(p["duration"] for p in pauses_analysis) / len(pauses_analysis) if pauses_analysis else 0
                },
                "filler_words": filler_words_analysis,
                "vocal_metrics": vocal_metrics_analysis,
                "sentence_clarity": {
                    "analysis": sentence_clarity_analysis,
                    "total_sentences": len(sentence_clarity_analysis)
                }
            }
            
            await self.update_job_status(job_id, "video_analysis", 50, "Analyzing visual presence...")
            
            # Analyze visual presence
            frames = self.vision_service.extract_frames(video_path)
            presence_metrics = await self.vision_service.analyze_with_gpt4o(frames)
            
            await self.update_job_status(job_id, "nlp_analysis", 70, "Analyzing leadership signals...")
            
            # Get user profile (in a real implementation, this would come from the database)
            user_profile = {}
            
            # Analyze gravitas and storytelling
            gravitas_analysis = await self.nlp_service.analyze_gravitas(transcript, user_profile)
            storytelling_analysis = await self.nlp_service.analyze_storytelling(transcript, user_profile)
            
            await self.update_job_status(job_id, "scoring", 85, "Calculating scores...")
            
            # Calculate scores
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
            
            # Generate coaching tips
            coaching_tips = await self.nlp_service.generate_coaching_tips(all_metrics)
            
            # Create report
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
            # Update job status to failed
            await self.update_job_status(job_id, "failed", 0, f"Processing failed: {str(e)}")
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