from domains.agent.chat_history import (
    format_history_for_prompt,
    trim_for_model,
    trim_to_max_turn_pairs,
)


def test__trim_to_max_turn_pairs__keeps_last_pairs():
    # Arrange
    hist = [
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
        {"role": "user", "content": "c"},
        {"role": "assistant", "content": "d"},
        {"role": "user", "content": "e"},
        {"role": "assistant", "content": "f"},
    ]
    # Act
    out = trim_to_max_turn_pairs(hist, max_turns=2)
    # Assert
    assert out == hist[-4:]


def test__trim_for_model__delegates_to_pair_limit():
    # Arrange
    hist = [{"role": "user", "content": "x"}, {"role": "assistant", "content": "y"}]
    # Act
    out = trim_for_model(hist, max_turns=1)
    # Assert
    assert out == hist


def test__format_history_for_prompt__labels_roles():
    # Arrange
    hist = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
    # Act
    text = format_history_for_prompt(hist)
    # Assert
    assert "User: hello" in text
    assert "Assistant: hi" in text
