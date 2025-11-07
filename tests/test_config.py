from unittest.mock import patch

from gac.config import load_config


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
        monkeypatch.setenv("GAC_NO_TIKTOKEN", "true")
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


def test_load_config_project_env_fallback(tmp_path, monkeypatch):
    """Test that .env file is used when .gac.env doesn't exist."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)

    # Create only a .env file (no .gac.env)
    env_file = tmp_path / ".env"
    env_file.write_text("GAC_MODEL=env-file-model\nGAC_TEMPERATURE=0.6\n")

    # Mock home directory to ensure it doesn't interfere
    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "nonexistent_home"

        config = load_config()
        # Should use .env file
        assert config["model"] == "env-file-model"
        assert config["temperature"] == 0.6


def test_load_config_precedence(tmp_path, monkeypatch):
    """Test that .gac.env takes precedence over .env when both exist."""
    # Change to tmp directory
    monkeypatch.chdir(tmp_path)

    # Create both .gac.env and .env files
    gac_env = tmp_path / ".gac.env"
    gac_env.write_text("GAC_MODEL=gac-env-model\n")

    env_file = tmp_path / ".env"
    env_file.write_text("GAC_MODEL=env-model\n")

    # Mock home directory to ensure it doesn't interfere
    with patch("gac.config.Path.home") as mock_home:
        mock_home.return_value = tmp_path / "nonexistent_home"

        config = load_config()
        # .gac.env should take precedence
        assert config["model"] == "gac-env-model"


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
