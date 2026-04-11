import copy

from domains.agent.theme_registry import CURATED_THEME
from domains.agent.tools.mutations.site_surface import mutate_revert_stylistic_defaults


def test__mutate_revert_stylistic_defaults__theme_and_css_only():
    # Arrange
    garden = copy.deepcopy(CURATED_THEME["garden-romance"])
    cfg: dict = {
        "theme": garden,
        "customCss": "body { margin: 0; }",
        "blocks": [
            {
                "id": "hero-1",
                "type": "hero",
                "visible": False,
                "order": 2,
                "data": {"partnerOne": "A", "partnerTwo": "B"},
            },
            {
                "id": "rsvp-1",
                "type": "rsvp",
                "visible": True,
                "order": 0,
                "data": {"title": "Reply"},
            },
        ],
    }
    before_blocks = copy.deepcopy(cfg["blocks"])
    # Act
    msg = mutate_revert_stylistic_defaults(cfg)
    # Assert
    assert "default" in msg.lower() or "starter" in msg.lower()
    assert cfg["theme"] == CURATED_THEME["classic-elegant"]
    assert "customCss" not in cfg
    assert cfg["blocks"] == before_blocks
    assert cfg["blocks"][0]["visible"] is False
    assert cfg["blocks"][0]["order"] == 2
    assert cfg["blocks"][0]["data"]["partnerOne"] == "A"
