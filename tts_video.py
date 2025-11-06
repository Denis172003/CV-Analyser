"""
Text-to-speech and video generation module.

This module handles audio synthesis using edge-tts
and video composition using moviepy.
"""

import os
import asyncio
import logging
from typing import Dict, List
import edge_tts
from moviepy import (
    VideoFileClip, TextClip, CompositeVideoClip, 
    AudioFileClip, ColorClip, concatenate_videoclips
)
import moviepy.video.fx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def synthesize_audio(text: str, output_path: str, language: str = "en") -> None:
    """
    Generate audio from text using edge-tts.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        language: Language code ("en" or "ro")
        
    Raises:
        Exception: If audio synthesis fails
    """
    try:
        # Validate input parameters
        if not text:
            raise ValueError("Text cannot be None or empty")
        if not output_path:
            raise ValueError("Output path cannot be None or empty")
        
        # Select voice based on language
        if language.lower() == "ro":
            voice = "ro-RO-AlinaNeural"  # Romanian female voice
        else:
            voice = "en-US-AriaNeural"   # English female voice
        
        logger.info(f"Synthesizing audio with voice: {voice}")
        
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Run async TTS synthesis
        asyncio.run(_synthesize_audio_async(text, output_path, voice))
        
        logger.info(f"Audio synthesized successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Audio synthesis failed: {str(e)}")
        raise Exception(f"Failed to synthesize audio: {str(e)}")


async def _synthesize_audio_async(text: str, output_path: str, voice: str) -> None:
    """
    Async helper function for TTS synthesis.
    
    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice: Voice identifier for edge-tts
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def create_animated_slides(script_parts: Dict, duration: float = 10.0) -> List:
    """
    Create animated text slides for video composition.
    
    Args:
        script_parts: Dictionary with intro, skills, achievement, closing segments
        duration: Total video duration in seconds
        
    Returns:
        List of moviepy clips for video composition
        
    Raises:
        Exception: If slide creation fails
    """
    try:
        clips = []
        
        # Calculate timing distribution
        timing = _calculate_timing_distribution(script_parts, duration)
        
        # Create background
        background = ColorClip(size=(1280, 720), color=(30, 30, 50), duration=duration)
        clips.append(background)
        
        # Create text clips for each segment
        for segment_name, segment_data in script_parts.items():
            if segment_name in timing:
                start_time = timing[segment_name]['start_time']
                segment_duration = timing[segment_name]['duration']
                text = segment_data.get('text', '')
                
                if text:
                    # Create text clip with animations
                    text_clip = _create_animated_text_clip(
                        text, segment_duration, start_time, segment_name
                    )
                    clips.append(text_clip)
        
        logger.info(f"Created {len(clips)} animated clips")
        return clips
        
    except Exception as e:
        logger.error(f"Slide creation failed: {str(e)}")
        raise Exception(f"Failed to create animated slides: {str(e)}")


def _calculate_timing_distribution(script_parts: Dict, total_duration: float) -> Dict:
    """
    Calculate timing distribution for script segments with dynamic adjustment.
    
    Args:
        script_parts: Dictionary with script segments
        total_duration: Total video duration
        
    Returns:
        Dictionary with timing information for each segment
    """
    # Calculate content lengths for dynamic timing
    content_lengths = {}
    total_content_length = 0
    
    for segment_name, segment_data in script_parts.items():
        text = segment_data.get('text', '')
        length = len(text.split()) if text else 0
        content_lengths[segment_name] = length
        total_content_length += length
    
    # Default timing weights (relative importance)
    timing_weights = {
        'intro': 0.25,      # 25% of time
        'skills': 0.40,     # 40% of time  
        'achievement': 0.25, # 25% of time
        'closing': 0.10     # 10% of time
    }
    
    # Available segments
    available_segments = list(script_parts.keys())
    timing = {}
    
    if len(available_segments) == 1:
        # Single segment gets full duration
        segment = available_segments[0]
        timing[segment] = {'start_time': 0.0, 'duration': total_duration}
    else:
        # Calculate dynamic timing based on content length and weights
        current_time = 0.0
        
        # Normalize weights for available segments
        total_weight = sum(timing_weights.get(seg, 0.25) for seg in available_segments)
        
        for segment in ['intro', 'skills', 'achievement', 'closing']:
            if segment in available_segments:
                # Base duration from weight
                weight = timing_weights.get(segment, 0.25)
                base_duration = (weight / total_weight) * total_duration
                
                # Adjust based on content length if we have content
                if total_content_length > 0:
                    content_ratio = content_lengths.get(segment, 0) / total_content_length
                    # Blend weight-based and content-based timing (70% weight, 30% content)
                    adjusted_duration = (0.7 * base_duration) + (0.3 * content_ratio * total_duration)
                else:
                    adjusted_duration = base_duration
                
                # Ensure minimum duration of 0.5 seconds
                adjusted_duration = max(0.5, adjusted_duration)
                
                timing[segment] = {
                    'start_time': current_time,
                    'duration': adjusted_duration
                }
                current_time += adjusted_duration
        
        # Normalize to fit exact total duration
        actual_total = sum(t['duration'] for t in timing.values())
        if actual_total != total_duration:
            scale_factor = total_duration / actual_total
            current_time = 0.0
            for segment in timing:
                timing[segment]['duration'] *= scale_factor
                timing[segment]['start_time'] = current_time
                current_time += timing[segment]['duration']
    
    return timing


def calculate_optimal_duration(script_parts: Dict, target_duration: float = 10.0) -> float:
    """
    Calculate optimal video duration based on content length.
    
    Args:
        script_parts: Dictionary with script segments
        target_duration: Target duration in seconds
        
    Returns:
        Optimal duration in seconds
    """
    # Calculate total word count
    total_words = 0
    for segment_data in script_parts.values():
        text = segment_data.get('text', '')
        total_words += len(text.split()) if text else 0
    
    # Average speaking rate: 150-160 words per minute for clear speech
    # For pitch videos, we want slightly faster: ~180 words per minute
    words_per_minute = 180
    content_based_duration = (total_words / words_per_minute) * 60
    
    # Ensure duration is within reasonable bounds (5-15 seconds)
    min_duration = 5.0
    max_duration = 15.0
    
    optimal_duration = max(min_duration, min(max_duration, content_based_duration))
    
    # If target duration is specified and reasonable, blend with content-based duration
    if 5.0 <= target_duration <= 15.0:
        # 60% content-based, 40% target-based
        optimal_duration = (0.6 * optimal_duration) + (0.4 * target_duration)
    
    return round(optimal_duration, 1)


def _create_animated_text_clip(text: str, duration: float, start_time: float, segment_type: str) -> TextClip:
    """
    Create an animated text clip with fade effects and smooth transitions.
    
    Args:
        text: Text content
        duration: Clip duration
        start_time: Start time in video
        segment_type: Type of segment (intro, skills, etc.)
        
    Returns:
        Animated TextClip
    """
    # Font and style settings based on segment type
    font_settings = {
        'intro': {'fontsize': 60, 'color': 'white'},
        'skills': {'fontsize': 45, 'color': '#4CAF50'},
        'achievement': {'fontsize': 50, 'color': '#FF9800'},
        'closing': {'fontsize': 55, 'color': '#2196F3'}
    }
    
    settings = font_settings.get(segment_type, font_settings['intro'])
    
    # Create text clip with MoviePy 2.x compatible parameters
    try:
        # Use the correct parameter names for MoviePy 2.x
        text_clip = TextClip(
            text=text,
            font_size=settings['fontsize'],  # Changed from fontsize to font_size
            color=settings['color'],
            size=(1200, None),
            method='caption'
        ).with_duration(duration).with_start(start_time)  # Changed from set_duration/set_start
    except Exception as e:
        logger.warning(f"TextClip creation failed with method='caption', trying basic: {e}")
        # Fallback to basic text clip
        try:
            text_clip = TextClip(
                text=text,
                font_size=settings['fontsize'],
                color=settings['color']
            ).with_duration(duration).with_start(start_time)
        except Exception as e2:
            logger.warning(f"Basic TextClip creation failed, using minimal: {e2}")
            # Minimal fallback
            text_clip = TextClip(text).with_duration(duration).with_start(start_time)
    
    # Center the text
    text_clip = text_clip.with_position('center')
    
    # Add smooth transitions with variable fade duration
    fade_duration = _calculate_fade_duration(duration, segment_type)
    
    text_clip = text_clip.with_effects([
        moviepy.video.fx.FadeIn(fade_duration),
        moviepy.video.fx.FadeOut(fade_duration)
    ])
    
    return text_clip


def _calculate_fade_duration(clip_duration: float, segment_type: str) -> float:
    """
    Calculate optimal fade duration for smooth transitions.
    
    Args:
        clip_duration: Duration of the clip
        segment_type: Type of segment
        
    Returns:
        Optimal fade duration in seconds
    """
    # Base fade duration as percentage of clip duration
    base_fade_ratio = {
        'intro': 0.3,      # Slower fade-in for intro
        'skills': 0.2,     # Quick transitions for skills
        'achievement': 0.25, # Medium fade for achievement
        'closing': 0.4     # Longer fade-out for closing
    }
    
    ratio = base_fade_ratio.get(segment_type, 0.25)
    fade_duration = clip_duration * ratio
    
    # Ensure fade duration is within reasonable bounds
    min_fade = 0.2
    max_fade = 1.0
    
    return max(min_fade, min(max_fade, fade_duration))


def create_transition_effects(clips: List, total_duration: float) -> List:
    """
    Add transition effects between video segments for smooth flow.
    
    Args:
        clips: List of video clips
        total_duration: Total video duration
        
    Returns:
        List of clips with transition effects
    """
    if len(clips) <= 1:
        return clips
    
    enhanced_clips = []
    
    # Add background first
    if clips:
        enhanced_clips.append(clips[0])  # Background clip
    
    # Add text clips with enhanced transitions
    text_clips = clips[1:] if len(clips) > 1 else []
    
    for i, clip in enumerate(text_clips):
        # Add subtle slide-in effect for non-intro segments
        if hasattr(clip, 'start') and clip.start > 0:
            # Slide in from right for skills, left for achievement, center for closing
            if 'skills' in str(clip):
                clip = clip.set_position(lambda t: ('center' if t > 0.3 else (1280 + 200 - t * 1000, 'center')))
            elif 'achievement' in str(clip):
                clip = clip.set_position(lambda t: ('center' if t > 0.3 else (-200 + t * 1000, 'center')))
        
        enhanced_clips.append(clip)
    
    return enhanced_clips


def make_video(audio_path: str, script_parts: Dict, output_path: str) -> None:
    """
    Compose final video with audio and animated slides.
    
    Args:
        audio_path: Path to the synthesized audio file
        script_parts: Script segments with timing information
        output_path: Path to save the final video
        
    Raises:
        Exception: If video composition fails
    """
    try:
        logger.info("Starting video composition...")
        
        # Validate input parameters
        if not audio_path:
            raise ValueError("Audio path cannot be None or empty")
        if not output_path:
            raise ValueError("Output path cannot be None or empty")
        if not script_parts:
            raise ValueError("Script parts cannot be None or empty")
        
        # Load audio file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        logger.info(f"Audio duration: {audio_duration:.2f} seconds")
        
        # Create animated slides
        video_clips = create_animated_slides(script_parts, audio_duration)
        
        # Compose final video
        final_video = CompositeVideoClip(video_clips, size=(1280, 720))
        
        # Set audio
        final_video = final_video.with_audio(audio_clip)
        
        # Ensure output directory exists
        if output_path and os.path.dirname(output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write video file with H.264 encoding for browser compatibility
        logger.info(f"Writing video to: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        audio_clip.close()
        final_video.close()
        
        logger.info("Video composition completed successfully")
        
    except Exception as e:
        logger.error(f"Video composition failed: {str(e)}")
        raise Exception(f"Failed to compose video: {str(e)}")


def generate_pitch_video(script_data: Dict, output_dir: str = "temp", language: str = "en", target_duration: float = 10.0) -> str:
    """
    Generate complete pitch video from script data with optimized timing.
    
    Args:
        script_data: Dictionary containing script segments
        output_dir: Directory to save temporary and output files
        language: Language for TTS ("en" or "ro")
        target_duration: Target video duration in seconds
        
    Returns:
        Path to the generated video file
        
    Raises:
        Exception: If video generation fails
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Calculate optimal duration based on content
        optimal_duration = calculate_optimal_duration(script_data, target_duration)
        logger.info(f"Optimal video duration: {optimal_duration} seconds")
        
        # Generate full script text with proper pacing
        full_script = _combine_script_parts_with_pacing(script_data)
        
        # Generate audio
        audio_path = os.path.join(output_dir, "pitch_audio.wav")
        synthesize_audio(full_script, audio_path, language)
        
        # Generate video with optimized timing
        video_path = os.path.join(output_dir, "pitch_video.mp4")
        make_video(audio_path, script_data, video_path)
        
        return video_path
        
    except Exception as e:
        logger.error(f"Pitch video generation failed: {str(e)}")
        raise Exception(f"Failed to generate pitch video: {str(e)}")


def _combine_script_parts(script_data: Dict) -> str:
    """
    Combine script parts into full text for TTS.
    
    Args:
        script_data: Dictionary with script segments
        
    Returns:
        Combined script text
    """
    parts = []
    
    # Order segments properly
    segment_order = ['intro', 'skills', 'achievement', 'closing']
    
    for segment in segment_order:
        if segment in script_data and 'text' in script_data[segment]:
            text = script_data[segment]['text'].strip()
            if text:
                parts.append(text)
    
    # Join with short pauses
    return ". ".join(parts) + "."


def _combine_script_parts_with_pacing(script_data: Dict) -> str:
    """
    Combine script parts with natural pacing for TTS (no SSML tags).
    
    Args:
        script_data: Dictionary with script segments
        
    Returns:
        Combined script text with natural pacing
    """
    parts = []
    
    # Order segments properly
    segment_order = ['intro', 'skills', 'achievement', 'closing']
    available_segments = [s for s in segment_order if s in script_data and 'text' in script_data[s]]
    
    for i, segment in enumerate(available_segments):
        text = script_data[segment]['text'].strip()
        if text:
            # Clean the text to avoid any encoding issues
            text = _clean_text_for_tts(text)
            
            # Add natural pauses using periods and commas (no SSML)
            if segment == 'intro':
                # Ensure intro ends with a period for natural pause
                if not text.endswith('.'):
                    text += '.'
            elif segment == 'skills':
                # Ensure skills section ends with a period
                if not text.endswith('.'):
                    text += '.'
            elif segment == 'achievement':
                # Ensure achievement ends with a period
                if not text.endswith('.'):
                    text += '.'
            elif segment == 'closing':
                # Ensure closing ends with exclamation or period
                if not text.endswith(('!', '.')):
                    text += '!'
            
            parts.append(text)
    
    # Join with natural pauses (double spaces create natural TTS pauses)
    return "  ".join(parts)


def _clean_text_for_tts(text: str) -> str:
    """
    Clean text for TTS to avoid encoding issues and strange characters.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text safe for TTS
    """
    if not text:
        return ""
    
    # Remove any problematic characters that might cause TTS issues
    import string
    
    # Keep only safe characters for TTS
    allowed_chars = string.ascii_letters + string.digits + ' .,!?-\''
    cleaned = ''.join(char for char in text if char in allowed_chars)
    
    # Remove multiple spaces and clean up
    cleaned = ' '.join(cleaned.split())
    
    # Ensure the text is not empty after cleaning
    if not cleaned.strip():
        return "professional content"
    
    return cleaned.strip()