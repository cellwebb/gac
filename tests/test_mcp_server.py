"""Tests for gac.mcp.server helpers."""

from gac.mcp.server import _stderr_console_redirect


def test_stderr_console_redirect_patches_and_restores():
    """_stderr_console_redirect swaps module-level consoles to stderr and restores them."""
    import gac.commit_executor as _ce
    import gac.grouped_commit_workflow as _gcw
    import gac.workflow_utils as _wu

    orig_ce = _ce.console
    orig_gcw = _gcw.console
    orig_wu = _wu.console

    with _stderr_console_redirect():
        assert _ce.console is not orig_ce
        assert _gcw.console is not orig_gcw
        assert _wu.console is not orig_wu
        assert _ce.console.stderr is True

    assert _ce.console is orig_ce
    assert _gcw.console is orig_gcw
    assert _wu.console is orig_wu
