"""Approval-bypass contracts for desktop computer_use actions."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_approval_state():
    from tools.computer_use import tool as computer_use

    computer_use.set_approval_callback(None)
    computer_use._session_auto_approve.clear()
    computer_use._always_allow.clear()
    yield
    computer_use.set_approval_callback(None)
    computer_use._session_auto_approve.clear()
    computer_use._always_allow.clear()


def test_without_yolo_desktop_action_uses_approval_callback():
    from tools.computer_use import tool as computer_use

    seen = []
    computer_use.set_approval_callback(
        lambda action, args, summary: seen.append((action, summary)) or "timeout"
    )

    result = computer_use._request_approval("click", {"element": 1}, "normal-session")

    assert seen == [("click", "click element #1")]
    assert result is not None
    assert "timed out" in result


def test_yolo_desktop_action_skips_approval_callback():
    from tools.approval import disable_session_yolo, enable_session_yolo
    from tools.computer_use import tool as computer_use

    session_id = "yolo-session"
    seen = []
    computer_use.set_approval_callback(
        lambda action, args, summary: seen.append(action) or "timeout"
    )
    enable_session_yolo(session_id)
    try:
        result = computer_use._request_approval(
            "click", {"element": 1}, session_id
        )
    finally:
        disable_session_yolo(session_id)

    assert result is None
    assert seen == []


def test_empty_session_id_honors_process_yolo(monkeypatch):
    import tools.approval as approval
    from tools.computer_use import tool as computer_use

    seen = []
    computer_use.set_approval_callback(
        lambda action, args, summary: seen.append(action) or "timeout"
    )
    monkeypatch.setattr(approval, "_YOLO_MODE_FROZEN", True)

    assert computer_use._request_approval("click", {"element": 1}, "") is None
    assert seen == []
