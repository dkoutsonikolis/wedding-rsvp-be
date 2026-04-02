from domains.agent.turn_logging import (
    debug_config_json,
    summarize_agent_config,
    summarize_llm_usage,
    summarize_tools_used,
)


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


def test__summarize_llm_usage__formats_sorted_key_values():
    # Arrange
    usage = {"output_tokens": 5, "input_tokens": 100, "requests": 2, "tool_calls": 1}
    # Act
    s = summarize_llm_usage(usage)
    # Assert
    assert s.startswith("llm_usage[")
    assert "input_tokens=100" in s
    assert "output_tokens=5" in s
    assert "requests=2" in s
    assert "tool_calls=1" in s


def test__summarize_llm_usage__none_means_not_available():
    # Arrange
    # Act
    s = summarize_llm_usage(None)
    # Assert
    assert s == "llm_usage=n/a"


def test__summarize_tools_used__none_empty_and_sequence():
    # Arrange
    # Act
    none_s = summarize_tools_used(None)
    empty_s = summarize_tools_used([])
    seq_s = summarize_tools_used(["get_full_site_config", "reorder_blocks"])
    # Assert
    assert none_s == "tools=n/a"
    assert empty_s == "tools=[]"
    assert seq_s == "tools[get_full_site_config;reorder_blocks]"


def test__debug_config_json__truncates_large_payload():
    # Arrange
    huge = {"x": "y" * 20_000}
    # Act
    out = debug_config_json(huge)
    # Assert
    assert "truncated" in out
    assert len(out) < 20_000
