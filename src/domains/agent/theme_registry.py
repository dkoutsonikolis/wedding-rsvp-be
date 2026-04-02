"""Curated wedding themes (ids + full objects aligned with the frontend registry)."""

from typing import Any, Literal

# Keep in sync with v0-wedding-rsvp-website/lib/wedding-config/themes.ts
CURATED_THEME: dict[str, dict[str, Any]] = {
    "classic-elegant": {
        "id": "classic-elegant",
        "name": "Classic Elegant",
        "description": (
            "Timeless sophistication with rich ivory, champagne gold, and graceful serif typography."
        ),
        "colors": {
            "primary": "#B8860B",
            "secondary": "#F5E6D3",
            "background": "#FFFEF9",
            "surface": "#FFFFFF",
            "text": "#2C1810",
            "textMuted": "#6B5344",
            "accent": "#D4AF37",
        },
        "fonts": {"heading": "Cormorant Garamond", "body": "Inter"},
        "borders": {"radius": "rounded", "style": "ornate"},
        "decorations": {
            "enabled": True,
            "style": "ornate",
            "elements": ["rose-corner", "heart-divider", "peony-cluster"],
            "dividerStyle": "ornate",
            "opacity": 0.25,
        },
    },
    "garden-romance": {
        "id": "garden-romance",
        "name": "Garden Romance",
        "description": (
            "A lush botanical paradise with rich greens, blooming florals, and romantic pink accents."
        ),
        "colors": {
            "primary": "#2D5A27",
            "secondary": "#F8E8E0",
            "background": "#F0F7EC",
            "surface": "#FFFFFF",
            "text": "#1A3318",
            "textMuted": "#4A6B47",
            "accent": "#E07B9A",
        },
        "fonts": {"heading": "Cormorant Garamond", "body": "Inter"},
        "borders": {"radius": "rounded", "style": "none"},
        "decorations": {
            "enabled": True,
            "style": "botanical",
            "elements": [
                "eucalyptus-corner",
                "wildflower-divider",
                "fern-accent",
                "peony-cluster",
            ],
            "dividerStyle": "botanical",
            "opacity": 0.4,
        },
    },
}

CuratedThemeId = Literal["classic-elegant", "garden-romance"]
