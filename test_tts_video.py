"""
Unit tests for TTS video generation module.

Tests cover audio synthesis, animated slide generation,
video composition, and timing distribution.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import tempfile
import shutil
from tts_video import (
    synthesize_audio,
    create_animated_slides,
    make_video,
    generate_pitch_video,
    calculate_optimal_duration,
    _calculate_timing_distribution,
    _calculate_fade_duration,
    _combine_script_parts,
    _combine_script_parts_with_pacing
)


class TestAudioSynthesis(unittest.TestCase):
    """Test text-to-speech audio generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.audio_path = os.path.join(self.temp_dir, "test_audio.wav")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('tts_video.asyncio.run')
    @patch('tts_video._synthesize_audio_async')
    def test_synthesize_audio_english(self, mock_async, mock_run):
        """Test English audio synthesis."""
        test_text = "Hello, I am a software developer."
        
        # Mock the async function
        mock_run.return_value = None
        
        # Test synthesis
        synthesize_audio(test_text, self.audio_path, "en")
        
        # Verify async function was called with correct parameters
        mock_run.assert_called_once()
        
    @patch('tts_video.asyncio.run')
    @patch('tts_video._synthesize_audio_async')
    def test_synthesize_audio_romanian(self, mock_async, mock_run):
        """Test Romanian audio synthesis."""
        test_text = "Salut, sunt un dezvoltator software."
        
        # Mock the async function
        mock_run.return_value = None
        
        # Test synthesis
        synthesize_audio(test_text, self.audio_path, "ro")
        
        # Verify async function was called
        mock_run.assert_called_once()
    
    @patch('tts_video.asyncio.run')
    def test_synthesize_audio_error_handling(self, mock_run):
        """Test error handling in audio synthesis."""
        mock_run.side_effect = Exception("TTS failed")
        
        with self.assertRaises(Exception) as context:
            synthesize_audio("test", self.audio_path, "en")
        
        self.assertIn("Failed to synthesize audio", str(context.exception))


class TestTimingDistribution(unittest.TestCase):
    """Test video timing and segment distribution."""
    
    def test_calculate_timing_distribution_all_segments(self):
        """Test timing calculation with all segments."""
        script_parts = {
            'intro': {'text': 'Hi, I am John Smith'},
            'skills': {'text': 'Python, JavaScript, Machine Learning'},
            'achievement': {'text': 'Led team of 15 developers'},
            'closing': {'text': 'Let\'s connect!'}
        }
        
        timing = _calculate_timing_distribution(script_parts, 10.0)
        
        # Check all segments are present
        self.assertIn('intro', timing)
        self.assertIn('skills', timing)
        self.assertIn('achievement', timing)
        self.assertIn('closing', timing)
        
        # Check timing structure
        for segment, data in timing.items():
            self.assertIn('start_time', data)
            self.assertIn('duration', data)
            self.assertGreaterEqual(data['duration'], 0.5)  # Minimum duration
        
        # Check total duration matches
        total_duration = sum(data['duration'] for data in timing.values())
        self.assertAlmostEqual(total_duration, 10.0, places=1)
    
    def test_calculate_timing_distribution_single_segment(self):
        """Test timing calculation with single segment."""
        script_parts = {
            'intro': {'text': 'Hi, I am John Smith, a software developer'}
        }
        
        timing = _calculate_timing_distribution(script_parts, 10.0)
        
        # Single segment should get full duration
        self.assertEqual(len(timing), 1)
        self.assertEqual(timing['intro']['start_time'], 0.0)
        self.assertEqual(timing['intro']['duration'], 10.0)
    
    def test_calculate_optimal_duration(self):
        """Test optimal duration calculation based on content."""
        # Short content
        short_script = {
            'intro': {'text': 'Hi John'},
            'skills': {'text': 'Python'},
            'closing': {'text': 'Thanks'}
        }
        
        duration = calculate_optimal_duration(short_script, 10.0)
        self.assertGreaterEqual(duration, 5.0)  # Minimum duration
        self.assertLessEqual(duration, 15.0)    # Maximum duration
        
        # Long content
        long_script = {
            'intro': {'text': 'Hi, I am John Smith, a senior software developer'},
            'skills': {'text': 'Python, JavaScript, React, Node.js, Machine Learning, Data Science'},
            'achievement': {'text': 'Led a team of 15 developers on a major project that increased productivity by 40%'},
            'closing': {'text': 'I would love to discuss how I can contribute to your team'}
        }
        
        long_duration = calculate_optimal_duration(long_script, 10.0)
        self.assertGreater(long_duration, duration)  # Should be longer than short content
    
    def test_calculate_fade_duration(self):
        """Test fade duration calculation."""
        # Test different segment types
        intro_fade = _calculate_fade_duration(3.0, 'intro')
        skills_fade = _calculate_fade_duration(3.0, 'skills')
        closing_fade = _calculate_fade_duration(3.0, 'closing')
        
        # Intro should have longer fade than skills
        self.assertGreater(intro_fade, skills_fade)
        
        # Closing should have longest fade
        self.assertGreater(closing_fade, skills_fade)
        
        # All fades should be within bounds
        for fade in [intro_fade, skills_fade, closing_fade]:
            self.assertGreaterEqual(fade, 0.2)
            self.assertLessEqual(fade, 1.0)


class TestScriptCombination(unittest.TestCase):
    """Test script text combination functions."""
    
    def test_combine_script_parts(self):
        """Test basic script combination."""
        script_data = {
            'intro': {'text': 'Hi, I am John'},
            'skills': {'text': 'Python developer'},
            'achievement': {'text': 'Led major project'},
            'closing': {'text': 'Let\'s connect'}
        }
        
        combined = _combine_script_parts(script_data)
        
        # Check all parts are included
        self.assertIn('Hi, I am John', combined)
        self.assertIn('Python developer', combined)
        self.assertIn('Led major project', combined)
        self.assertIn('Let\'s connect', combined)
        
        # Check proper joining
        self.assertTrue(combined.endswith('.'))
    
    def test_combine_script_parts_with_pacing(self):
        """Test script combination with pacing markers."""
        script_data = {
            'intro': {'text': 'Hi, I am John Smith'},
            'skills': {'text': 'Python, JavaScript'},
            'closing': {'text': 'Thank you'}
        }
        
        combined = _combine_script_parts_with_pacing(script_data)
        
        # Check pacing markers are added
        self.assertIn('<break time=', combined)
        
        # Check all content is preserved (accounting for pacing modifications)
        self.assertIn('Hi', combined)
        self.assertIn('John Smith', combined)
        self.assertIn('Python', combined)
        self.assertIn('JavaScript', combined)
        self.assertIn('Thank you', combined)
    
    def test_combine_script_parts_missing_segments(self):
        """Test script combination with missing segments."""
        script_data = {
            'intro': {'text': 'Hi, I am John'},
            'closing': {'text': 'Thank you'}
            # Missing skills and achievement
        }
        
        combined = _combine_script_parts(script_data)
        
        # Should only include available segments
        self.assertIn('Hi, I am John', combined)
        self.assertIn('Thank you', combined)
        self.assertTrue(combined.endswith('.'))


class TestVideoGeneration(unittest.TestCase):
    """Test video generation functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.script_data = {
            'intro': {'text': 'Hi, I am John Smith'},
            'skills': {'text': 'Python developer with 5 years experience'},
            'achievement': {'text': 'Led team of 10 developers'},
            'closing': {'text': 'Let\'s connect and discuss opportunities'}
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('tts_video.ColorClip')
    @patch('tts_video.TextClip')
    def test_create_animated_slides(self, mock_text_clip, mock_color_clip):
        """Test animated slide creation."""
        # Mock moviepy components
        mock_background = MagicMock()
        mock_color_clip.return_value = mock_background
        
        mock_text = MagicMock()
        mock_text.set_duration.return_value = mock_text
        mock_text.set_start.return_value = mock_text
        mock_text.set_position.return_value = mock_text
        mock_text.fadein.return_value = mock_text
        mock_text.fadeout.return_value = mock_text
        mock_text_clip.return_value = mock_text
        
        # Test slide creation
        clips = create_animated_slides(self.script_data, 10.0)
        
        # Should return list of clips
        self.assertIsInstance(clips, list)
        self.assertGreater(len(clips), 0)
        
        # Background should be created
        mock_color_clip.assert_called_once()
    
    @patch('tts_video.create_animated_slides')
    @patch('tts_video.CompositeVideoClip')
    @patch('tts_video.AudioFileClip')
    @patch('os.path.exists')
    def test_make_video(self, mock_exists, mock_audio_clip, mock_composite, mock_slides):
        """Test video composition."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock audio clip
        mock_audio = MagicMock()
        mock_audio.duration = 10.0
        mock_audio_clip.return_value = mock_audio
        
        # Mock video clips
        mock_slides.return_value = [MagicMock(), MagicMock()]
        
        # Mock composite video
        mock_video = MagicMock()
        mock_composite.return_value = mock_video
        mock_video.set_audio.return_value = mock_video
        
        audio_path = os.path.join(self.temp_dir, "test_audio.wav")
        video_path = os.path.join(self.temp_dir, "test_video.mp4")
        
        # Test video creation
        make_video(audio_path, self.script_data, video_path)
        
        # Verify components were called
        mock_audio_clip.assert_called_once_with(audio_path)
        mock_slides.assert_called_once()
        mock_composite.assert_called_once()
        mock_video.write_videofile.assert_called_once()
    
    @patch('tts_video.make_video')
    @patch('tts_video.synthesize_audio')
    @patch('tts_video.calculate_optimal_duration')
    def test_generate_pitch_video(self, mock_duration, mock_audio, mock_video):
        """Test complete pitch video generation."""
        # Mock optimal duration calculation
        mock_duration.return_value = 10.0
        
        # Mock audio synthesis
        mock_audio.return_value = None
        
        # Mock video creation
        mock_video.return_value = None
        
        # Test video generation
        result_path = generate_pitch_video(
            self.script_data, 
            self.temp_dir, 
            "en", 
            10.0
        )
        
        # Verify result path
        self.assertTrue(result_path.endswith("pitch_video.mp4"))
        self.assertIn(self.temp_dir, result_path)
        
        # Verify functions were called
        mock_duration.assert_called_once()
        mock_audio.assert_called_once()
        mock_video.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """Test error handling in video generation."""
    
    def test_make_video_missing_audio(self):
        """Test video creation with missing audio file."""
        script_data = {'intro': {'text': 'Test'}}
        
        with self.assertRaises(Exception) as context:
            make_video("nonexistent_audio.wav", script_data, "output.mp4")
        
        self.assertIn("Audio file not found", str(context.exception))
    
    @patch('tts_video.synthesize_audio')
    def test_generate_pitch_video_audio_error(self, mock_audio):
        """Test pitch video generation with audio synthesis error."""
        mock_audio.side_effect = Exception("Audio synthesis failed")
        
        script_data = {'intro': {'text': 'Test'}}
        
        with self.assertRaises(Exception) as context:
            generate_pitch_video(script_data, "temp", "en")
        
        self.assertIn("Failed to generate pitch video", str(context.exception))


if __name__ == '__main__':
    unittest.main()