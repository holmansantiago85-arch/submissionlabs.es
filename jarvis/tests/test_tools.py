import json
from pathlib import Path

import pytest

from jarvis import memory as mem_mod
from jarvis.tools import registry
from jarvis.tools.system import run_shell


def test_schemas_are_strict_and_sorted():
    schemas = registry.schemas()
    names = [s["name"] for s in schemas]
    assert names == sorted(names)
    for s in schemas:
        assert s["strict"] is True
        assert s["input_schema"]["additionalProperties"] is False
        assert set(s["input_schema"]["required"]) == set(s["input_schema"]["properties"])


def test_get_datetime_format():
    out, err = registry.call("get_datetime", {})
    assert not err
    # e.g. "Sunday 27/09/2026 10:15:02 CEST (Europe/Madrid)"
    assert "/" in out and ":" in out


def test_shell_allowlist_blocks_unknown():
    out = run_shell("rm -rf /tmp/never")
    assert out.startswith("Error:")


def test_shell_allowlist_allows_prefix():
    out = run_shell("pwd")
    assert "exit code: 0" in out


def test_registry_rejects_bad_input():
    out, err = registry.call("read_file", "not json")
    assert err
    out, err = registry.call("nope", {})
    assert err


def test_memory_roundtrip(tmp_path: Path):
    m = mem_mod.Memory(db_path=tmp_path / "t.db", notes_path=tmp_path / "n.md")
    m.append("s", "user", "hello")
    m.append("s", "assistant", [{"type": "text", "text": "hi"}])
    hist = m.history("s")
    assert hist[0] == {"role": "user", "content": "hello"}
    assert hist[1]["content"][0]["text"] == "hi"
    m.add_note("Kids class Tuesday 17:30")
    assert "Kids class" in m.read_notes()


def test_history_trims_orphan_tool_results(tmp_path: Path):
    m = mem_mod.Memory(db_path=tmp_path / "t.db", notes_path=tmp_path / "n.md")
    m.append("s", "assistant", [{"type": "text", "text": "old"}])
    m.append("s", "user", [{"type": "tool_result", "tool_use_id": "x", "content": "r"}])
    m.append("s", "user", "fresh question")
    hist = m.history("s")
    assert hist[0] == {"role": "user", "content": "fresh question"}
