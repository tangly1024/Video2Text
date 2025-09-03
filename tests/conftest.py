import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a mock audio file for testing."""
    audio_file = temp_dir / "sample.wav"
    audio_file.touch()
    return audio_file


@pytest.fixture
def sample_video_file(temp_dir):
    """Create a mock video file for testing."""
    video_file = temp_dir / "sample.mp4"
    video_file.touch()
    return video_file


@pytest.fixture
def mock_logger():
    """Mock logger for testing logging functionality."""
    return Mock()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        'output_dir': '/tmp/output',
        'log_level': 'INFO',
        'supported_formats': ['.wav', '.mp3', '.m4a', '.mp4']
    }


@pytest.fixture
def mock_pydub_audio():
    """Mock pydub AudioSegment for testing."""
    mock_audio = MagicMock()
    mock_audio.duration_seconds = 10.0
    mock_audio.frame_rate = 44100
    mock_audio.channels = 2
    return mock_audio


@pytest.fixture
def mock_speech_recognition():
    """Mock speech recognition for testing."""
    mock_recognizer = MagicMock()
    mock_recognizer.recognize_google.return_value = "test transcription"
    return mock_recognizer


@pytest.fixture
def sample_file_paths(temp_dir):
    """Create sample file paths for testing."""
    files = {
        'audio': temp_dir / "audio.wav",
        'video': temp_dir / "video.mp4", 
        'text': temp_dir / "text.txt",
        'log': temp_dir / "test.log"
    }
    
    for file_path in files.values():
        file_path.touch()
    
    return files


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test."""
    yield