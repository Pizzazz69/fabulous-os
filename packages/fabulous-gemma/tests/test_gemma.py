import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import fabulous_gemma as fg  # noqa: E402

N5105 = os.path.join(HERE, "..", "..", "fabulous-probe", "tests", "fixtures", "n5105_cpuinfo.txt")
RULES = os.path.join(HERE, "..", "..", "..", "rules")


def test_n5105_has_four_cores_and_no_avx():
    cores, flags = fg.read_cpu(N5105)
    assert cores == 4
    assert "sse4_2" in flags
    assert "avx" not in flags and "avx2" not in flags


def test_rules_give_the_beelink_the_small_model_with_a_slow_note(monkeypatch):
    monkeypatch.setattr(fg, "RULES_DIR", RULES)
    _, flags = fg.read_cpu(N5105)
    model, notes = fg.advice(memory_gb=15.4, flags=flags)
    assert model == "e2b"
    assert any("slowly" in n for n in notes)


def test_rules_give_a_small_memory_pc_no_model(monkeypatch):
    monkeypatch.setattr(fg, "RULES_DIR", RULES)
    model, notes = fg.advice(memory_gb=3.8, flags={"avx2"})
    assert model == "none" and notes


def test_advice_without_rules_installed_matches(monkeypatch):
    monkeypatch.setattr(fg, "RULES_DIR", "/nonexistent")
    assert fg.advice(memory_gb=3.8, flags={"avx2"})[0] == "none"
    model, notes = fg.advice(memory_gb=15.4, flags={"sse4_2"})
    assert model == "e2b" and any("slowly" in n for n in notes)


def test_stream_line_text_piece():
    line = 'data: {"choices":[{"delta":{"content":"Paris"}}]}\n'
    assert fg.parse_stream_line(line) == ("Paris", None, False)


def test_stream_line_done_and_noise():
    assert fg.parse_stream_line("data: [DONE]") == (None, None, True)
    assert fg.parse_stream_line("") == (None, None, False)
    assert fg.parse_stream_line(": keep-alive") == (None, None, False)
    assert fg.parse_stream_line("data: {broken") == (None, None, False)


def test_stream_line_timings():
    line = 'data: {"choices":[{"delta":{}}],"timings":{"predicted_per_second":5.0}}'
    piece, timings, done = fg.parse_stream_line(line)
    assert piece is None and timings == {"predicted_per_second": 5.0} and not done


def test_stream_line_error_is_shown_not_hidden():
    with pytest.raises(fg.GemmaError, match="too long"):
        fg.parse_stream_line('data: {"error":{"message":"the request is too long"}}')


def test_history_keeps_everything_when_short():
    msgs = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
            {"role": "user", "content": "c"}]
    assert fg.trim_history(msgs) == msgs


def test_history_drops_oldest_first_and_starts_with_the_user():
    msgs = [{"role": "user", "content": "x" * 60}, {"role": "assistant", "content": "y" * 60},
            {"role": "user", "content": "z" * 60}, {"role": "assistant", "content": "w" * 60},
            {"role": "user", "content": "last"}]
    kept = fg.trim_history(msgs, budget=130)
    assert kept[-1]["content"] == "last"
    assert kept[0]["role"] == "user"
    assert msgs[0] not in kept


def test_history_always_keeps_the_last_message_even_if_huge():
    msgs = [{"role": "user", "content": "q" * 500}]
    assert fg.trim_history(msgs, budget=10) == msgs


def test_missing_model_is_reported_in_plain_words(tmp_path, monkeypatch):
    monkeypatch.delenv("FABULOUS_GEMMA_MODEL", raising=False)
    with pytest.raises(fg.GemmaError, match="missing"):
        fg.find_model(str(tmp_path))


def test_picture_addon_is_not_mistaken_for_the_model(tmp_path, monkeypatch):
    monkeypatch.delenv("FABULOUS_GEMMA_MODEL", raising=False)
    (tmp_path / "gemma-4-E2B-it-mmproj.gguf").write_bytes(b"")
    (tmp_path / "gemma-4-E2B_q4_0-it.gguf").write_bytes(b"")
    assert fg.find_model(str(tmp_path)).endswith("gemma-4-E2B_q4_0-it.gguf")


def test_the_assistant_is_started_without_a_network():
    # The command that starts the model must begin by removing the network.
    assert fg.ISOLATE[0] == "unshare" and "--net" in fg.ISOLATE
