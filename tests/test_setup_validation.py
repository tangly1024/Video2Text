"""
Validation tests to ensure testing infrastructure is properly set up.
These tests verify that the testing environment works correctly.
"""
import pytest
from pathlib import Path
import video_converter


class TestSetupValidation:
    """Tests to validate the testing setup is working correctly."""

    def test_pytest_is_working(self):
        """Test that pytest is functioning."""
        assert True

    def test_can_import_package(self):
        """Test that the main package can be imported."""
        assert video_converter is not None

    def test_coverage_is_enabled(self, pytestconfig):
        """Test that coverage reporting is enabled."""
        plugins = [plugin.__class__.__name__ for plugin in pytestconfig.pluginmanager.get_plugins()]
        # Coverage plugin should be loaded
        assert any('cov' in plugin.lower() for plugin in plugins)

    def test_temp_dir_fixture(self, temp_dir):
        """Test that temp_dir fixture works."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_mock_logger_fixture(self, mock_logger):
        """Test that mock_logger fixture works."""
        mock_logger.info("test message")
        mock_logger.info.assert_called_once_with("test message")

    def test_sample_file_fixtures(self, sample_audio_file, sample_video_file):
        """Test that sample file fixtures work."""
        assert sample_audio_file.exists()
        assert sample_video_file.exists()
        assert sample_audio_file.suffix == '.wav'
        assert sample_video_file.suffix == '.mp4'

    def test_project_structure_exists(self):
        """Test that expected project structure exists."""
        project_root = Path(__file__).parent.parent
        
        expected_files = [
            'main.py',
            'requirements.txt',
            'pyproject.toml',
            'video_converter/__init__.py',
            'video_converter/file_utils.py',
            'video_converter/log_utils.py', 
            'video_converter/voice_utils.py'
        ]
        
        for file_path in expected_files:
            assert (project_root / file_path).exists(), f"Missing: {file_path}"

    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Test that unit test marker works."""
        assert True

    @pytest.mark.integration  
    def test_integration_marker_works(self):
        """Test that integration test marker works."""
        assert True

    @pytest.mark.slow
    def test_slow_marker_works(self):
        """Test that slow test marker works."""
        assert True