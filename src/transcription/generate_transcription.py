import os
import whisper
import tempfile
from typing import Dict
from pathlib import Path
from moviepy.editor import VideoFileClip


def transcribe_audio(video_path: Path, model_size: str = "base") -> Dict:
    """Extract audio and transcribe with detailed information"""
    
    temp_audio = None
    try:
        # Extract audio
        video = VideoFileClip(str(video_path))
        temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        
        # Extract audio with details
        audio_duration = video.duration
        audio_fps = video.audio.fps if video.audio else None
        
        video.audio.write_audiofile(
            temp_audio.name, 
            codec='mp3', 
            bitrate='192k',
            verbose=False, 
            logger=None
        )
        video.close()
        
        # Load Whisper model
        model = whisper.load_model(model_size)
        
        # Transcribe with detailed output
        result = model.transcribe(
            temp_audio.name,
            verbose=False,
            language=None,  # Auto-detect language
            task='transcribe'
        )
        
        # Extract segments for timing information
        segments = []
        for segment in result.get('segments', []):
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        transcription_data = {
            'full_text': result['text'].strip(),
            'language': result.get('language', 'unknown'),
            'duration': audio_duration,
            'audio_fps': audio_fps,
            'segments': segments[:5],  # First 5 segments for preview
            'total_segments': len(result.get('segments', []))
        }

        # Close the file before trying to delete it
        temp_audio.close()
        
        # Try to delete with error handling for Windows file locking
        try:
            os.unlink(temp_audio.name)
        except PermissionError:
            pass  # File will be cleaned up by system temp cleanup
        return transcription_data
        
    finally:
        if temp_audio and os.path.exists(temp_audio.name):
            os.unlink(temp_audio.name)
