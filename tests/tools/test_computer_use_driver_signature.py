"""Contracts for selecting and validating signed CuaDriver.app bundles."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tools.computer_use import cua_backend as cb


def _codesign_result(*, team: str):
    return SimpleNamespace(
        returncode=0,
        stdout="",
        stderr=f"Identifier=com.trycua.driver\nTeamIdentifier={team}\n",
    )


def test_official_driver_team_identity_is_accepted(monkeypatch):
    monkeypatch.setattr(cb.shutil, "which", lambda command: "/usr/bin/codesign")
    monkeypatch.setattr(
        cb.subprocess,
        "run",
        lambda *args, **kwargs: _codesign_result(team="YCK386LBJ7"),
    )

    cb._validate_cua_driver_app_signature("/Applications/CuaDriver.app")


def test_previous_driver_team_identity_is_rejected(monkeypatch):
    monkeypatch.setattr(cb.shutil, "which", lambda command: "/usr/bin/codesign")
    monkeypatch.setattr(
        cb.subprocess,
        "run",
        lambda *args, **kwargs: _codesign_result(team="4YEC26S9KF"),
    )

    with pytest.raises(RuntimeError, match="team"):
        cb._validate_cua_driver_app_signature("/Applications/CuaDriver.app")


def test_app_path_resolution_follows_selected_driver_symlink(tmp_path):
    app = tmp_path / "CuaDriver.app"
    executable = app / "Contents" / "MacOS" / "cua-driver"
    executable.parent.mkdir(parents=True)
    executable.write_text("driver", encoding="utf-8")
    executable.chmod(0o755)
    link = tmp_path / "bin" / "cua-driver"
    link.parent.mkdir()
    link.symlink_to(executable)

    assert cb._resolve_cua_driver_app_path(str(link)) == str(app)
