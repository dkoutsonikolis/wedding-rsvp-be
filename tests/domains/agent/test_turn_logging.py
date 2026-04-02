from domains.agent.turn_logging import debug_config_json, summarize_agent_config


def test__summarize_agent_config__includes_hero_and_block_preview():
    # Arrange
    cfg = {
        "theme": {},
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "data": {"partnerOne": "A", "partnerTwo": "B"},
            },
            {"id": "rsvp-1", "type": "rsvp", "data": {}},
        ],
    }
    # Act
    s = summarize_agent_config("raw", cfg)
    # Assert
    assert "hero-1:hero" in s
    assert "rsvp-1:rsvp" in s
    assert "hero='A'/'B'" in s


def test__summarize_agent_config__non_dict():
    # Arrange
    # Act
    s = summarize_agent_config("raw", None)
    # Assert
    assert "non-dict" in s or "<NoneType>" in s


def test__debug_config_json__truncates_large_payload():
    # Arrange
    huge = {"x": "y" * 20_000}
    # Act
    out = debug_config_json(huge)
    # Assert
    assert "truncated" in out
    assert len(out) < 20_000
