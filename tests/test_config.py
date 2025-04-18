from gac.config import load_config


def test_load_config_env(monkeypatch):
    monkeypatch.setenv("GAC_MODEL", "env-model")
    monkeypatch.setenv("GAC_BACKUP_MODEL", "env-backup")
    monkeypatch.setenv("GAC_FORMAT_FILES", "false")
    monkeypatch.setenv("GAC_TEMPERATURE", "0.5")
    monkeypatch.setenv("GAC_MAX_OUTPUT_TOKENS", "1234")
    monkeypatch.setenv("GAC_RETRIES", "7")
    monkeypatch.setenv("GAC_LOG_LEVEL", "DEBUG")
    config = load_config()
    assert config["model"] == "env-model"
    assert config["backup_model"] == "env-backup"
    assert config["format_files"] is False
    assert config["temperature"] == 0.5
    assert config["max_output_tokens"] == 1234
    assert config["max_retries"] == 7
    assert config["log_level"] == "DEBUG"
