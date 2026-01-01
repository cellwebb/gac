from unittest.mock import patch

import pytest

from gac.config import load_config, validate_config
from gac.errors import ConfigError


def test_load_config_env(tmp_path, monkeypatch):
    # Change to a temp directory to avoid picking up local config files
    monkeypatch.chdir(tmp_path)

    # Mock home directory to ensure it doesn't interfere
    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "nonexistent_home"

        monkeypatch.setenv("GAC_MODEL", "env-model")
        monkeypatch.setenv("GAC_TEMPERATURE", "0.5")
        monkeypatch.setenv("GAC_MAX_OUTPUT_TOKENS", "1234")
        monkeypatch.setenv("GAC_RETRIES", "7")
        monkeypatch.setenv("GAC_LOG_LEVEL", "DEBUG")
        config = load_config()
        assert config["model"] == "env-model"
        assert config["temperature"] == 0.5
        assert config["max_output_tokens"] == 1234
        assert config["max_retries"] == 7
        assert config["log_level"] == "DEBUG"
        assert config["no_tiktoken"] is True


def test_load_config_project_gac_env(tmp_path, monkeypatch):
    """Test that project .gac.env file is loaded and overrides user config."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)

    # Create a .gac.env file in the project directory
    gac_env = tmp_path / ".gac.env"
    gac_env.write_text("GAC_MODEL=project-model\nGAC_TEMPERATURE=0.8\n")

    # Mock home directory config
    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "home"
        home_config = mock_home.return_value / ".gac.env"
        home_config.parent.mkdir(exist_ok=True)
        home_config.write_text("GAC_MODEL=home-model\nGAC_TEMPERATURE=0.3\n")

        config = load_config()
        # Project config should override home config
        assert config["model"] == "project-model"
        assert config["temperature"] == 0.8


def test_load_config_ignores_plain_env_file(tmp_path, monkeypatch):
    """Ensure .env files are ignored when loading configuration."""
    monkeypatch.chdir(tmp_path)

    env_file = tmp_path / ".env"
    env_file.write_text("GAC_MODEL=env-file-model\n")

    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "nonexistent_home"
        monkeypatch.delenv("GAC_MODEL", raising=False)

        config = load_config()
        assert config["model"] is None


def test_load_config_verbose(tmp_path, monkeypatch):
    """Test that GAC_VERBOSE config option works correctly."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)

    # Mock home directory to ensure it doesn't interfere
    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "nonexistent_home"

        # Test default (should be False)
        config = load_config()
        assert config["verbose"] is False

        # Test with verbose=true
        monkeypatch.setenv("GAC_VERBOSE", "true")
        config = load_config()
        assert config["verbose"] is True

        # Test with verbose=false
        monkeypatch.setenv("GAC_VERBOSE", "false")
        config = load_config()
        assert config["verbose"] is False

        # Test with verbose=1
        monkeypatch.setenv("GAC_VERBOSE", "1")
        config = load_config()
        assert config["verbose"] is True

        # Test with verbose=yes
        monkeypatch.setenv("GAC_VERBOSE", "yes")
        config = load_config()
        assert config["verbose"] is True


# Tests for validate_config()
class TestValidateConfig:
    """Test suite for configuration validation."""

    def test_valid_config_passes(self):
        """Test that a valid configuration passes validation."""
        valid_config = {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 1.0,
            "max_output_tokens": 8192,
            "max_retries": 3,
            "warning_limit_tokens": 5000,
            "hook_timeout": 30,
        }
        # Should not raise any exception
        validate_config(valid_config)

    def test_valid_config_with_none_values(self):
        """Test that None values are allowed and skip validation."""
        config_with_nones = {
            "model": None,
            "temperature": None,
            "max_output_tokens": None,
            "max_retries": None,
            "warning_limit_tokens": None,
            "hook_timeout": None,
        }
        # Should not raise any exception
        validate_config(config_with_nones)

    # Temperature validation tests
    def test_temperature_too_low(self):
        """Test that temperature below 0.0 raises ConfigError."""
        config = {"temperature": -0.1}
        with pytest.raises(ConfigError, match=r"temperature must be between 0\.0 and 2\.0, got -0\.1"):
            validate_config(config)

    def test_temperature_too_high(self):
        """Test that temperature above 2.0 raises ConfigError."""
        config = {"temperature": 2.1}
        with pytest.raises(ConfigError, match=r"temperature must be between 0\.0 and 2\.0, got 2\.1"):
            validate_config(config)

    def test_temperature_boundary_values(self):
        """Test that temperature boundary values (0.0, 2.0) are valid."""
        validate_config({"temperature": 0.0})
        validate_config({"temperature": 2.0})

    def test_temperature_accepts_int(self):
        """Test that temperature accepts integer values."""
        validate_config({"temperature": 1})  # Should be treated as float

    def test_temperature_wrong_type(self):
        """Test that temperature with wrong type raises ConfigError."""
        config = {"temperature": "hot"}  # String instead of number
        with pytest.raises(ConfigError, match=r"temperature must be a number, got str"):
            validate_config(config)

    # max_output_tokens validation tests
    def test_max_output_tokens_too_low(self):
        """Test that max_output_tokens below 1 raises ConfigError."""
        config = {"max_output_tokens": 0}
        with pytest.raises(ConfigError, match=r"max_output_tokens must be between 1 and 100000, got 0"):
            validate_config(config)

    def test_max_output_tokens_negative(self):
        """Test that negative max_output_tokens raises ConfigError."""
        config = {"max_output_tokens": -100}
        with pytest.raises(ConfigError, match=r"max_output_tokens must be between 1 and 100000, got -100"):
            validate_config(config)

    def test_max_output_tokens_too_high(self):
        """Test that max_output_tokens above 100000 raises ConfigError."""
        config = {"max_output_tokens": 100001}
        with pytest.raises(ConfigError, match=r"max_output_tokens must be between 1 and 100000, got 100001"):
            validate_config(config)

    def test_max_output_tokens_boundary_values(self):
        """Test that max_output_tokens boundary values (1, 100000) are valid."""
        validate_config({"max_output_tokens": 1})
        validate_config({"max_output_tokens": 100000})

    def test_max_output_tokens_wrong_type(self):
        """Test that max_output_tokens with wrong type raises ConfigError."""
        config = {"max_output_tokens": "8192"}  # String instead of int
        with pytest.raises(ConfigError, match=r"max_output_tokens must be an integer, got str"):
            validate_config(config)

    # max_retries validation tests
    def test_max_retries_too_low(self):
        """Test that max_retries below 1 raises ConfigError."""
        config = {"max_retries": 0}
        with pytest.raises(ConfigError, match=r"max_retries must be between 1 and 10, got 0"):
            validate_config(config)

    def test_max_retries_too_high(self):
        """Test that max_retries above 10 raises ConfigError."""
        config = {"max_retries": 11}
        with pytest.raises(ConfigError, match=r"max_retries must be between 1 and 10, got 11"):
            validate_config(config)

    def test_max_retries_boundary_values(self):
        """Test that max_retries boundary values (1, 10) are valid."""
        validate_config({"max_retries": 1})
        validate_config({"max_retries": 10})

    def test_max_retries_wrong_type(self):
        """Test that max_retries with wrong type raises ConfigError."""
        config = {"max_retries": 3.5}  # Float instead of int
        with pytest.raises(ConfigError, match=r"max_retries must be an integer, got float"):
            validate_config(config)

    # warning_limit_tokens validation tests
    def test_warning_limit_tokens_zero(self):
        """Test that warning_limit_tokens of 0 raises ConfigError."""
        config = {"warning_limit_tokens": 0}
        with pytest.raises(ConfigError, match=r"warning_limit_tokens must be positive, got 0"):
            validate_config(config)

    def test_warning_limit_tokens_negative(self):
        """Test that negative warning_limit_tokens raises ConfigError."""
        config = {"warning_limit_tokens": -500}
        with pytest.raises(ConfigError, match=r"warning_limit_tokens must be positive, got -500"):
            validate_config(config)

    def test_warning_limit_tokens_positive(self):
        """Test that positive warning_limit_tokens is valid."""
        validate_config({"warning_limit_tokens": 1})
        validate_config({"warning_limit_tokens": 100000})

    def test_warning_limit_tokens_wrong_type(self):
        """Test that warning_limit_tokens with wrong type raises ConfigError."""
        config = {"warning_limit_tokens": "5000"}  # String instead of int
        with pytest.raises(ConfigError, match=r"warning_limit_tokens must be an integer, got str"):
            validate_config(config)

    # hook_timeout validation tests
    def test_hook_timeout_zero(self):
        """Test that hook_timeout of 0 raises ConfigError."""
        config = {"hook_timeout": 0}
        with pytest.raises(ConfigError, match=r"hook_timeout must be positive, got 0"):
            validate_config(config)

    def test_hook_timeout_negative(self):
        """Test that negative hook_timeout raises ConfigError."""
        config = {"hook_timeout": -30}
        with pytest.raises(ConfigError, match=r"hook_timeout must be positive, got -30"):
            validate_config(config)

    def test_hook_timeout_positive(self):
        """Test that positive hook_timeout is valid."""
        validate_config({"hook_timeout": 1})
        validate_config({"hook_timeout": 300})

    def test_hook_timeout_wrong_type(self):
        """Test that hook_timeout with wrong type raises ConfigError."""
        config = {"hook_timeout": "30"}  # String instead of int
        with pytest.raises(ConfigError, match=r"hook_timeout must be an integer, got str"):
            validate_config(config)

    # Integration test with load_config
    def test_load_config_validates(self, tmp_path, monkeypatch):
        """Test that load_config() calls validate_config() and raises on invalid values."""
        monkeypatch.chdir(tmp_path)

        # Create a .gac.env file with invalid temperature
        gac_env = tmp_path / ".gac.env"
        gac_env.write_text("GAC_TEMPERATURE=3.0\n")  # Invalid: > 2.0

        with patch("gac.config.Path.home") as mock_home:
            mock_home.return_value = tmp_path / "nonexistent_home"

            with pytest.raises(ConfigError, match=r"temperature must be between 0\.0 and 2\.0, got 3\.0"):
                load_config()
