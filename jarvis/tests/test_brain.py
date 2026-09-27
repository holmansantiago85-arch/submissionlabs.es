"""Brain loop test with a fake Anthropic client - no network."""

from pathlib import Path
from types import SimpleNamespace

from jarvis import brain as brain_mod
from jarvis.memory import Memory


class _Block(SimpleNamespace):
    def model_dump(self, exclude_none=True):
        return {k: v for k, v in vars(self).items() if v is not None}


class FakeMessages:
    def __init__(self):
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return SimpleNamespace(
                stop_reason="tool_use",
                stop_details=None,
                content=[
                    _Block(type="text", text="Checking."),
                    _Block(type="tool_use", id="tu1", name="get_datetime", input={}),
                ],
            )
        # Second round: tool_result must be present in the last user message
        last = kwargs["messages"][-1]
        assert last["role"] == "user"
        assert last["content"][0]["type"] == "tool_result"
        assert last["content"][0]["tool_use_id"] == "tu1"
        return SimpleNamespace(
            stop_reason="end_turn",
            stop_details=None,
            content=[_Block(type="text", text="It is now.")],
        )


def test_tool_loop(tmp_path: Path, monkeypatch):
    fake = FakeMessages()
    monkeypatch.setattr(brain_mod.config, "fallbacks", False)
    monkeypatch.setattr(brain_mod.anthropic, "Anthropic", lambda: SimpleNamespace(messages=fake))
    b = brain_mod.Brain(memory=Memory(db_path=tmp_path / "t.db", notes_path=tmp_path / "n.md"), session="t")
    reply = b.ask("what time is it")
    assert reply == "It is now."
    assert fake.calls == 2
    hist = b.memory.history("t")
    assert [m["role"] for m in hist] == ["user", "assistant", "user", "assistant"]


def test_refusal(tmp_path: Path, monkeypatch):
    class Refuse:
        def create(self, **kwargs):
            return SimpleNamespace(
                stop_reason="refusal",
                stop_details=SimpleNamespace(category="cyber"),
                content=[],
            )

    monkeypatch.setattr(brain_mod.config, "fallbacks", False)
    monkeypatch.setattr(brain_mod.anthropic, "Anthropic", lambda: SimpleNamespace(messages=Refuse()))
    b = brain_mod.Brain(memory=Memory(db_path=tmp_path / "t.db", notes_path=tmp_path / "n.md"), session="t")
    assert "can't help" in b.ask("x")
