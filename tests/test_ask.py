import sys
from types import SimpleNamespace

import app.ask as ask_module


def test_main_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    questions = []

    class FakeChat:
        def send_message(self, question):
            questions.append(question)
            return SimpleNamespace(text=f"answer: {question}", usage_metadata=None)

    chat = FakeChat()
    client = SimpleNamespace(chats=SimpleNamespace(create=lambda **kwargs: chat))
    answers = iter(["follow-up", ""])
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    monkeypatch.setattr(sys, "argv", ["app.ask", "first question"])

    ask_module.main()

    assert questions == ["first question", "follow-up"]
    output = capsys.readouterr().out
    assert "answer: first question" in output
    assert "answer: follow-up" in output
