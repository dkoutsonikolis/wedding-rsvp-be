from domains.agent.agent_config_summary import summarize_wedding_site_config_for_agent


def test__summarize_wedding_site_config_for_agent__hero_and_counts():
    # Arrange
    cfg = {
        "id": "site-1",
        "slug": "a-b",
        "theme": {"id": "classic-elegant", "name": "X"},
        "metadata": {"published": False},
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "visible": True,
                "order": 0,
                "data": {"partnerOne": "A", "partnerTwo": "B", "tagline": "Hi"},
            },
            {
                "id": "gallery-1",
                "type": "gallery",
                "visible": False,
                "order": 2,
                "data": {"title": "Photos", "photos": [{"id": "1"}, {"id": "2"}]},
            },
        ],
    }
    # Act
    summary = summarize_wedding_site_config_for_agent(cfg)
    # Assert
    assert summary["id"] == "site-1"
    assert summary["slug"] == "a-b"
    assert summary["theme"] == {"id": "classic-elegant"}
    assert summary["metadata"] == {"published": False}
    assert len(summary["blocks"]) == 2
    by_id = {row["id"]: row for row in summary["blocks"]}
    assert by_id["hero-1"]["summary"] == "A & B"
    assert by_id["hero-1"]["visible"] is True
    assert by_id["gallery-1"]["photo_count"] == 2
    assert by_id["gallery-1"]["summary"] == "Photos"
    for row in summary["blocks"]:
        assert "data" not in row


def test__summarize_wedding_site_config_for_agent__orders_blocks():
    # Arrange
    cfg = {
        "blocks": [
            {"id": "b", "type": "rsvp", "order": 1, "data": {"title": "RSVP"}},
            {"id": "a", "type": "hero", "order": 0, "data": {"partnerOne": "X", "partnerTwo": "Y"}},
        ],
    }
    # Act
    summary = summarize_wedding_site_config_for_agent(cfg)
    # Assert
    assert [row["id"] for row in summary["blocks"]] == ["a", "b"]


def test__summarize_wedding_site_config_for_agent__empty_blocks():
    # Arrange
    cfg: dict = {"blocks": []}
    # Act
    summary = summarize_wedding_site_config_for_agent(cfg)
    # Assert
    assert summary["blocks"] == []
