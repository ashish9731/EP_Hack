import librosa
import numpy as np
from typing import List, Dict, Any
import re

class AudioAnalysisService:
    def __init__(self):
        self.filler_patterns = [
            r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b',
            r'\bactually\b', r'\bbasically\b', r'\bliterally\b',
            r'\bso\b', r'\bI mean\b', r'\bright\b'
        ]
    
    def analyze_speaking_rate(self, transcript: str, duration: float) -> Dict[str, Any]:
        words = transcript.split()
        word_count = len(words)
        minutes = duration / 60.0
        
        wpm = word_count / minutes if minutes > 0 else 0
        
        calculation = f"{word_count} words ÷ {minutes:.2f} minutes = {wpm:.0f} WPM"
        
        ideal_min, ideal_max = 140, 160
        benchmark = f"Ideal presentation pace: {ideal_min}-{ideal_max} WPM (based on public speaking research)"
        
        return {
            "wpm": round(wpm, 1),
            "calculation": calculation,
            "benchmark": benchmark,
            "word_count": word_count,
            "duration_minutes": round(minutes, 2)
        }
    
    def detect_pauses(self, words: List[Dict]) -> List[Dict[str, Any]]:
        pauses = []
        
        for i in range(len(words) - 1):
            current_end = words[i].get('end', 0)
            next_start = words[i + 1].get('start', 0)
            
            gap = next_start - current_end
            
            if gap > 0.3:
                pause_type = "brief" if gap < 1.0 else "strategic" if gap < 2.0 else "long"
                pauses.append({
                    "start": round(current_end, 2),
                    "end": round(next_start, 2),
                    "duration": round(gap, 2),
                    "type": pause_type
                })
        
        return pauses
    
    def detect_filler_words(self, transcript: str, words: List[Dict]) -> Dict[str, Any]:
        fillers = []
        transcript_lower = transcript.lower()
        
        for word_data in words:
            word = word_data.get('word', '').strip().lower()
            
            for pattern in self.filler_patterns:
                if re.match(pattern, word):
                    fillers.append({
                        "timestamp": round(word_data.get('start', 0), 2),
                        "word": word,
                        "type": "filler"
                    })
                    break
        
        duration_minutes = words[-1].get('end', 0) / 60.0 if words else 1
        filler_rate = len(fillers) / duration_minutes if duration_minutes > 0 else 0
        
        return {
            "fillers": fillers,
            "count": len(fillers),
            "rate_per_minute": round(filler_rate, 2),
            "benchmark": "Ideal: <2 fillers per minute for executive presence"
        }
    
    async def analyze_vocal_metrics(self, audio_path: str) -> Dict[str, Any]:
        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                pitch_mean = np.mean(pitch_values)
                pitch_std = np.std(pitch_values)
            else:
                pitch_mean = 0
                pitch_std = 0
            
            rms = librosa.feature.rms(y=y)[0]
            loudness_mean = np.mean(rms)
            loudness_std = np.std(rms)
            
            return {
                "pitch_mean_hz": round(float(pitch_mean), 2),
                "pitch_variability": round(float(pitch_std), 2),
                "loudness_stability": round(float(loudness_std), 4),
                "benchmark": "Optimal pitch variability: 20-40 Hz for engaging delivery"
            }
        except Exception as e:
            return {
                "pitch_mean_hz": 0,
                "pitch_variability": 0,
                "loudness_stability": 0,
                "error": str(e),
                "benchmark": "Unavailable"
            }
    
    def analyze_sentence_clarity(self, transcript: str) -> List[Dict[str, Any]]:
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        clarity_analysis = []
        
        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)
            
            if word_count < 10:
                clarity_rating = "concise"
                suggestion = "Good - concise and clear"
            elif word_count < 20:
                clarity_rating = "ok"
                suggestion = "Consider breaking into shorter sentences for impact"
            else:
                clarity_rating = "long"
                suggestion = "Break this into 2-3 shorter sentences for better clarity"
            
            clarity_analysis.append({
                "sentence": sentence,
                "word_count": word_count,
                "clarity_rating": clarity_rating,
                "suggestion": suggestion
            })
        
        return clarity_analysis[:10]