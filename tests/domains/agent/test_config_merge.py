from domains.agent.config_processing import (
    merge_model_config_into_base,
    merge_stored_config_with_request,
)


def test__merge_model_config_into_base__merges_hero_data_by_block_id():
    # Arrange
    base = {
        "id": "site-1",
        "theme": {"id": "t1", "name": "T", "colors": {"primary": "#111"}},
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "visible": True,
                "order": 0,
                "data": {"partnerOne": "A", "partnerTwo": "B", "tagline": "x"},
            },
            {"id": "rsvp-1", "type": "rsvp", "data": {"title": "RSVP"}},
        ],
    }
    model_config = {"blocks": [{"id": "hero-1", "data": {"partnerOne": "Dimitris"}}]}
    # Act
    out = merge_model_config_into_base(base=base, model_config=model_config)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "Dimitris"
    assert out["blocks"][0]["data"]["partnerTwo"] == "B"
    assert out["blocks"][0]["data"]["tagline"] == "x"


def test__merge_model_config_into_base__merges_hero_by_type_when_id_missing():
    # Arrange
    base = {
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "data": {"partnerOne": "A", "partnerTwo": "B"},
            },
            {"id": "rsvp-1", "type": "rsvp", "data": {"title": "RSVP"}},
        ],
    }
    model_config = {
        "blocks": [{"type": "hero", "data": {"partnerOne": "Dimitris", "partnerTwo": "Avgi"}}],
    }
    # Act
    out = merge_model_config_into_base(base=base, model_config=model_config)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "Dimitris"
    assert out["blocks"][0]["data"]["partnerTwo"] == "Avgi"
    assert out["blocks"][1]["data"]["title"] == "RSVP"


def test__merge_model_config_into_base__skips_ambiguous_type_without_id():
    # Arrange
    base = {
        "blocks": [
            {"id": "h1", "type": "hero", "data": {"partnerOne": "A"}},
            {"id": "h2", "type": "hero", "data": {"partnerOne": "B"}},
        ],
    }
    model_config = {"blocks": [{"type": "hero", "data": {"partnerOne": "Z"}}]}
    # Act
    out = merge_model_config_into_base(base=base, model_config=model_config)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "A"
    assert out["blocks"][1]["data"]["partnerOne"] == "B"


def test__merge_model_config_into_base__removed_block_ids_drops_blocks():
    # Arrange
    base = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "data": {}},
            {"id": "gallery-1", "type": "gallery", "data": {"title": "Our Journey Together"}},
            {"id": "rsvp-1", "type": "rsvp", "data": {}},
        ],
    }
    model_config = {"removed_block_ids": ["gallery-1"]}
    # Act
    out = merge_model_config_into_base(base=base, model_config=model_config)
    # Assert
    assert len(out["blocks"]) == 2
    assert [b["id"] for b in out["blocks"]] == ["hero-1", "rsvp-1"]
    assert "removed_block_ids" not in out


def test__merge_model_config_into_base__non_dict_model_config_returns_base_copy():
    # Arrange
    base = {"blocks": []}
    # Act
    out = merge_model_config_into_base(base=base, model_config=None)
    # Assert
    assert out == {"blocks": []}
    assert out is not base


def test__merge_stored_config_with_request__deep_merges_partial_theme():
    # Arrange
    stored = {
        "theme": {
            "id": "classic-elegant",
            "name": "Classic",
            "colors": {"primary": "#111", "secondary": "#222", "background": "#FFFEF9"},
            "fonts": {"heading": "Serif"},
        },
    }
    request = {"theme": {"colors": {"background": "#E3F2FD"}}}
    # Act
    out = merge_stored_config_with_request(stored=stored, request=request)
    # Assert
    assert out["theme"]["id"] == "classic-elegant"
    assert out["theme"]["fonts"]["heading"] == "Serif"
    assert out["theme"]["colors"]["background"] == "#E3F2FD"
    assert out["theme"]["colors"]["primary"] == "#111"


def test__merge_stored_config_with_request__ignores_empty_blocks_list():
    # Arrange
    stored = {"blocks": [{"id": "hero-1", "type": "hero"}]}
    request: dict = {"blocks": []}
    # Act
    out = merge_stored_config_with_request(stored=stored, request=request)
    # Assert
    assert len(out["blocks"]) == 1


def test__merge_model_config_into_base__deep_merges_theme():
    # Arrange
    base = {"theme": {"id": "t1", "colors": {"primary": "#000", "secondary": "#fff"}}}
    model_config = {"theme": {"colors": {"primary": "#abc"}}}
    # Act
    out = merge_model_config_into_base(base=base, model_config=model_config)
    # Assert
    assert out["theme"]["colors"]["primary"] == "#abc"
    assert out["theme"]["colors"]["secondary"] == "#fff"
