import os
import tempfile
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

class TranscriptionService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.api_key = api_key
    
    def detect_video_format(self, video_path: str) -> str:
        """Detect the actual video format using ffprobe"""
        try:
            result = subprocess.run(
                ['/usr/bin/ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                 '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1',
                 video_path],
                capture_output=True, text=True, timeout=10
            )
            codec = result.stdout.strip()
            
            # Also check container format
            result2 = subprocess.run(
                ['/usr/bin/ffprobe', '-v', 'error', '-show_entries', 
                 'format=format_name', '-of', 'default=noprint_wrappers=1:nokey=1',
                 video_path],
                capture_output=True, text=True, timeout=10
            )
            format_name = result2.stdout.strip()
            
            return format_name, codec
        except Exception as e:
            print(f"Error detecting format: {e}")
            return "unknown", "unknown"
    
    async def extract_audio_from_video(self, video_path: str, original_format: str = None) -> str:
        """Extract audio from video, handling various formats including WebM"""
        
        # Generate audio output path
        audio_path = tempfile.mktemp(suffix=".wav")
        
        # Detect actual format if not provided
        format_name, codec = self.detect_video_format(video_path)
        print(f"Detected format: {format_name}, codec: {codec}")
        
        # Build FFmpeg command with format-specific options
        command = ['/usr/bin/ffmpeg']
        
        # For WebM files, we need specific input options
        if 'webm' in format_name.lower() or 'matroska' in format_name.lower():
            # WebM/Matroska container
            command.extend(['-f', 'webm'])
        elif 'mp4' in format_name.lower() or 'mov' in format_name.lower():
            # MP4/MOV container
            pass  # FFmpeg auto-detects
        
        command.extend([
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',  # Overwrite output file
            audio_path
        ])
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                stderr_text = stderr.decode()
                print(f"FFmpeg failed with return code {process.returncode}")
                print(f"STDERR: {stderr_text}")
                
                # Try alternative approach for problematic files
                audio_path = await self._extract_audio_fallback(video_path)
                if audio_path:
                    return audio_path
                    
                raise RuntimeError(f"FFmpeg failed: {stderr_text}")
            
            # Check if audio file was created and has content
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file was not created: {audio_path}")
            
            if os.path.getsize(audio_path) < 1000:
                print(f"Warning: Audio file is very small ({os.path.getsize(audio_path)} bytes)")
                # Try fallback
                fallback_path = await self._extract_audio_fallback(video_path)
                if fallback_path and os.path.getsize(fallback_path) > os.path.getsize(audio_path):
                    os.remove(audio_path)
                    return fallback_path
                
            return audio_path
            
        except Exception as e:
            print(f"Error in extract_audio_from_video: {e}")
            # Try fallback
            fallback_path = await self._extract_audio_fallback(video_path)
            if fallback_path:
                return fallback_path
            raise
    
    async def _extract_audio_fallback(self, video_path: str) -> str:
        """Fallback method using different FFmpeg options"""
        audio_path = tempfile.mktemp(suffix=".wav")
        
        # Try with more permissive options
        commands_to_try = [
            # Try 1: Force WebM input format
            ['/usr/bin/ffmpeg', '-f', 'webm', '-i', video_path, 
             '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', audio_path],
            # Try 2: Copy audio codec first then convert
            ['/usr/bin/ffmpeg', '-i', video_path, 
             '-vn', '-c:a', 'copy', '-y', video_path + '.audio'],
            # Try 3: Use raw demuxer
            ['/usr/bin/ffmpeg', '-f', 'lavfi', '-i', f'amovie={video_path}', 
             '-ar', '16000', '-ac', '1', '-y', audio_path],
            # Try 4: Simple extraction ignoring errors
            ['/usr/bin/ffmpeg', '-err_detect', 'ignore_err', '-i', video_path,
             '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', audio_path],
        ]
        
        for cmd in commands_to_try:
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                    print(f"Fallback succeeded with command: {' '.join(cmd[:3])}")
                    return audio_path
            except Exception as e:
                print(f"Fallback command failed: {e}")
                continue
        
        return None
    
    async def transcribe_audio(self, audio_path: str) -> dict:
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        
        with open(audio_path, "rb") as audio_file:
            response = await asyncio.to_thread(
                client.audio.transcriptions.create,
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )
        
        words_list = []
        if hasattr(response, 'words') and response.words:
            words_list = [{"word": w.word, "start": w.start, "end": w.end} for w in response.words]
        
        segments_list = []
        if hasattr(response, 'segments') and response.segments:
            segments_list = [{"text": s.text, "start": s.start, "end": s.end} for s in response.segments]
        
        duration = response.duration if hasattr(response, 'duration') else 180
        
        return {
            "text": response.text,
            "words": words_list,
            "segments": segments_list,
            "duration": duration
        }
