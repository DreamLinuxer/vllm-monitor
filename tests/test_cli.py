"""CLI tests."""

from __future__ import annotations

from typer.testing import CliRunner

from vllm_monitor.app import VllmMonitorApp
from vllm_monitor.cli import app


def test_env_vars_configure_monitor(monkeypatch):
    """VLLM_URL / VLLM_MONITOR_INTERVAL / VLLM_API_KEY configure the run
    (the Docker image relies on this env-only configuration path)."""
    captured = {}

    def fake_run(self):  # don't launch the blocking TUI
        captured["url"] = self._poller.base_url
        captured["interval"] = self._interval

    monkeypatch.setattr(VllmMonitorApp, "run", fake_run)

    result = CliRunner().invoke(
        app,
        [],
        env={"VLLM_URL": "http://envhost:9999", "VLLM_MONITOR_INTERVAL": "1"},
    )

    assert result.exit_code == 0, result.output
    assert captured["url"] == "http://envhost:9999"
    assert captured["interval"] == 1.0


def test_flags_override(monkeypatch):
    """Explicit flags still work (and win over the defaults)."""
    captured = {}
    monkeypatch.setattr(
        VllmMonitorApp, "run", lambda self: captured.update(url=self._poller.base_url)
    )

    result = CliRunner().invoke(app, ["--url", "http://flag:8000"])

    assert result.exit_code == 0, result.output
    assert captured["url"] == "http://flag:8000"
