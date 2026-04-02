import pytest

from domains.agent.tools.mutations.site_surface import mutate_apply_theme, mutate_reorder_blocks


def test__mutate_reorder_blocks__permutes_and_assigns_order():
    # Arrange
    cfg = {
        "blocks": [
            {"id": "a", "order": 0},
            {"id": "b", "order": 1},
            {"id": "c", "order": 2},
        ]
    }
    # Act
    msg = mutate_reorder_blocks(cfg, ["c", "a", "b"])
    # Assert
    assert "order" in msg.lower()
    assert [b["id"] for b in cfg["blocks"]] == ["c", "a", "b"]
    assert [b["order"] for b in cfg["blocks"]] == [0, 1, 2]


def test__mutate_reorder_blocks__rejects_incomplete_id_list():
    # Arrange
    cfg = {"blocks": [{"id": "a"}, {"id": "b"}]}
    # Act
    msg = mutate_reorder_blocks(cfg, ["a"])
    # Assert
    assert "exactly once" in msg


def test__mutate_apply_theme__replaces_theme_object():
    # Arrange
    cfg = {"theme": {"id": "old"}}
    # Act
    msg = mutate_apply_theme(cfg, "garden-romance")
    # Assert
    assert "garden-romance" in msg
    assert cfg["theme"]["id"] == "garden-romance"
    assert cfg["theme"]["colors"]["primary"] == "#2D5A27"


def test__mutate_apply_theme__unknown_id_raises():
    # Arrange
    cfg: dict = {"theme": {}}
    # Act / Assert
    with pytest.raises(ValueError, match="Unknown theme_id"):
        mutate_apply_theme(cfg, "not-a-theme")
