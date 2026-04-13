from utils.chat_history import append_turn, normalize_history


def test__normalize_history__filters_invalid_entries():
    # Arrange
    raw = [
        {"role": "user", "content": "hi"},
        {"role": "bot", "content": "bad"},
        "not-a-dict",
        {"role": "assistant", "content": "ok"},
    ]
    # Act
    out = normalize_history(raw)
    # Assert
    assert out == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "ok"},
    ]


def test__append_turn__adds_user_then_assistant():
    # Arrange
    base = [{"role": "user", "content": "first"}]
    # Act
    out = append_turn(base, "u", "a")
    # Assert
    assert out[-2:] == [
        {"role": "user", "content": "u"},
        {"role": "assistant", "content": "a"},
    ]
