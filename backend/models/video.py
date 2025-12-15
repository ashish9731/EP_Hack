from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    AUDIO_ANALYSIS = "audio_analysis"
    VIDEO_ANALYSIS = "video_analysis"
    NLP_ANALYSIS = "nlp_analysis"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"

class VideJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    job_id: str
    user_id: str
    video_id: str
    status: JobStatus
    progress: float = 0.0
    current_step: str = ""
    report_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class VideoMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")
    video_id: str
    user_id: str
    filename: str
    file_size: int
    duration: Optional[float] = None
    format: str
    uploaded_at: datetime

class EPReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    report_id: str
    user_id: str
    video_id: str
    job_id: str
    overall_score: float
    gravitas_score: float
    communication_score: float
    presence_score: float
    storytelling_score: Optional[float] = None
    detailed_metrics: Dict[str, Any]
    coaching_tips: List[str]
    created_at: datetime

class FillerWord(BaseModel):
    timestamp: float
    word: str
    type: str

class Pause(BaseModel):
    start: float
    end: float
    duration: float
    type: str

class SentenceClarity(BaseModel):
    sentence: str
    word_count: int
    clarity_rating: str
    suggestion: str

class CommunicationMetrics(BaseModel):
    speaking_rate: float
    speaking_rate_calculation: str
    pauses: List[Pause]
    filler_words: List[FillerWord]
    filler_rate: float
    pitch_mean: Optional[float] = None
    pitch_variability: Optional[float] = None
    sentence_clarity: List[SentenceClarity]

class PresenceMetrics(BaseModel):
    posture_score: float
    eye_contact_ratio: float
    facial_expression_balance: Dict[str, float]
    gesture_rate: float

class GravitasMetrics(BaseModel):
    commanding_presence: float
    decisiveness: float
    poise_under_pressure: float
    emotional_intelligence: float
    vision_articulation: float

class StorytellingMetrics(BaseModel):
    has_story: bool
    narrative_structure: Optional[float] = None
    authenticity: Optional[float] = None
    concreteness: Optional[float] = None
    pacing: Optional[float] = None