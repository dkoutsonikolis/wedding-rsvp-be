from domains.agent.config_normalize import (
    apply_hero_names_from_user_message_when_unchanged,
    normalize_misplaced_hero_couple_fields,
    strip_unknown_top_level_site_config_keys,
)


def test__normalize__moves_root_partner_fields_into_hero_and_strips_junk_data():
    # Arrange
    cfg = {
        "id": "site-1",
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "data": {"partnerOne": "Emma", "partnerTwo": "James"},
            },
        ],
        "partnerOne": "Dimitris",
        "partnerTwo": "Avgi",
        "data": "partnerOne",
    }
    # Act
    out = normalize_misplaced_hero_couple_fields(cfg)
    # Assert
    assert "partnerOne" not in out
    assert "partnerTwo" not in out
    assert "data" not in out
    assert out["blocks"][0]["data"]["partnerOne"] == "Dimitris"
    assert out["blocks"][0]["data"]["partnerTwo"] == "Avgi"


def test__normalize__only_partner_two_at_root():
    # Arrange
    cfg = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "data": {"partnerOne": "Emma", "partnerTwo": "James"}},
        ],
        "partnerTwo": "Avgi",
        "data": "partnerOne",
    }
    # Act
    out = normalize_misplaced_hero_couple_fields(cfg)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "Emma"
    assert out["blocks"][0]["data"]["partnerTwo"] == "Avgi"
    assert "data" not in out


def test__normalize__restores_root_when_no_hero_block():
    # Arrange
    cfg = {"blocks": [], "partnerOne": "X"}
    # Act
    out = normalize_misplaced_hero_couple_fields(cfg)
    # Assert
    assert out["partnerOne"] == "X"


def test__strip_unknown_top_level__removes_inverted_model_garbage():
    # Arrange
    cfg = {
        "id": "site-1",
        "slug": "x",
        "blocks": [],
        "Avgi": "id",
        "Dimitris": "partnerTwo",
        "type": "hero",
    }
    # Act
    out = strip_unknown_top_level_site_config_keys(cfg)
    # Assert
    assert set(out.keys()) == {"id", "slug", "blocks"}
    assert "Avgi" not in out


def test__strip_unknown_top_level__preserves_underscore_stub_keys():
    # Arrange
    cfg = {"id": "1", "blocks": [], "_stub_last_user_message": "hi"}
    # Act
    out = strip_unknown_top_level_site_config_keys(cfg)
    # Assert
    assert out["_stub_last_user_message"] == "hi"


def test__apply_hero_names_from_message__when_hero_unchanged_from_base():
    # Arrange
    base = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "data": {"partnerOne": "Emma", "partnerTwo": "James"}},
        ],
    }
    final = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "data": {"partnerOne": "Emma", "partnerTwo": "James"}},
        ],
    }
    msg = "Change the couple names to Dimitris and Avgi"
    # Act
    out = apply_hero_names_from_user_message_when_unchanged(base, final, msg)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "Dimitris"
    assert out["blocks"][0]["data"]["partnerTwo"] == "Avgi"


def test__apply_hero_names_from_message__skips_when_model_changed_hero():
    # Arrange
    base = {
        "blocks": [
            {"type": "hero", "data": {"partnerOne": "Emma", "partnerTwo": "James"}},
        ],
    }
    final = {
        "blocks": [
            {"type": "hero", "data": {"partnerOne": "Anna", "partnerTwo": "Bob"}},
        ],
    }
    msg = "Rename to Dimitris and Avgi"
    # Act
    out = apply_hero_names_from_user_message_when_unchanged(base, final, msg)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "Anna"


def test__apply_hero_names_from_message__skips_without_name_intent():
    # Arrange
    cfg = {
        "blocks": [
            {"type": "hero", "data": {"partnerOne": "A", "partnerTwo": "B"}},
        ],
    }
    msg = "We loved Paris and London on our trip"
    # Act
    out = apply_hero_names_from_user_message_when_unchanged(cfg, cfg, msg)
    # Assert
    assert out["blocks"][0]["data"]["partnerOne"] == "A"
