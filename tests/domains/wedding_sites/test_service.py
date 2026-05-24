import re
from uuid import uuid4

import pytest

from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.exceptions import (
    InvalidSlugError,
    SlugConflictError,
    WeddingSiteAlreadyExistsError,
    WeddingSiteNotFoundError,
)
from domains.wedding_sites.models import WeddingSite
from domains.wedding_sites.service import WeddingSitesService


@pytest.mark.asyncio
async def test__list_for_user__empty(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    # Act
    sites = await wedding_sites_service.list_for_user(site_owner_user_id)
    # Assert
    assert sites == []


@pytest.mark.asyncio
async def test__create__persists_normalized_slug(
    wedding_sites_service: WeddingSitesService, site_owner_user_id, wedding_site_factory
):
    # Arrange
    # Act
    site = await wedding_site_factory(slug="  My-Wedding-Day  ")
    # Assert
    assert site.slug == "my-wedding-day"
    loaded = await wedding_sites_service.get_by_id_for_user(
        site_id=site.id, owner_user_id=site_owner_user_id
    )
    assert loaded.slug == "my-wedding-day"


@pytest.mark.asyncio
async def test__list_for_user__returns_owner_sites_only(
    wedding_sites_service: WeddingSitesService,
    site_owner_user_id,
    other_user_id,
    wedding_site_factory,
):
    # Arrange
    await wedding_site_factory(slug="owner-site")
    await wedding_sites_service.create(owner_user_id=other_user_id, slug="other-only")
    # Act
    mine = await wedding_sites_service.list_for_user(site_owner_user_id)
    theirs = await wedding_sites_service.list_for_user(other_user_id)
    # Assert
    assert len(mine) == 1
    assert mine[0].slug == "owner-site"
    assert len(theirs) == 1
    assert theirs[0].slug == "other-only"


@pytest.mark.asyncio
async def test__create__duplicate_slug_conflict(
    wedding_sites_service: WeddingSitesService,
    other_user_id,
    wedding_site_factory,
):
    # Arrange
    await wedding_site_factory(slug="dup-slug")
    # Act
    with pytest.raises(SlugConflictError):
        await wedding_sites_service.create(owner_user_id=other_user_id, slug="dup-slug")
    # Assert


@pytest.mark.asyncio
async def test__create__rejects_invalid_slug(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    # Act
    with pytest.raises(InvalidSlugError):
        await wedding_sites_service.create(owner_user_id=site_owner_user_id, slug="Bad_Slug")
    # Assert


@pytest.mark.asyncio
async def test__create__omit_slug_derives_from_title(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    # Act
    site = await wedding_sites_service.create(
        owner_user_id=site_owner_user_id,
        title="  Our Wedding Day!  ",
        slug=None,
    )
    # Assert
    assert site.slug == "our-wedding-day"


@pytest.mark.asyncio
async def test__create__omit_slug_without_title_uses_site_prefix(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    # Act
    site = await wedding_sites_service.create(
        owner_user_id=site_owner_user_id,
        title=None,
        slug=None,
    )
    # Assert
    assert re.fullmatch(r"site-[0-9a-f]{12}", site.slug)


@pytest.mark.asyncio
async def test__create__rejects_second_site_for_owner(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    await wedding_sites_service.create(owner_user_id=site_owner_user_id, title="Shared", slug=None)
    # Act
    with pytest.raises(WeddingSiteAlreadyExistsError) as exc_info:
        await wedding_sites_service.create(
            owner_user_id=site_owner_user_id, title="Another", slug=None
        )
    # Assert
    assert "already has a wedding site" in str(exc_info.value)


@pytest.mark.asyncio
async def test__get_by_id_for_user__not_found(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    missing_id = uuid4()
    # Act
    with pytest.raises(WeddingSiteNotFoundError):
        await wedding_sites_service.get_by_id_for_user(
            site_id=missing_id, owner_user_id=site_owner_user_id
        )
    # Assert


@pytest.mark.asyncio
async def test__get_by_id_for_user__wrong_owner(
    wedding_sites_service: WeddingSitesService,
    site_owner_user_id,
    other_user_id,
    wedding_site_factory,
):
    # Arrange
    site = await wedding_site_factory(slug="private-site")
    # Act
    with pytest.raises(WeddingSiteNotFoundError):
        await wedding_sites_service.get_by_id_for_user(site_id=site.id, owner_user_id=other_user_id)
    # Assert


@pytest.mark.asyncio
async def test__update_for_user__clears_title(
    wedding_sites_service: WeddingSitesService, site_owner_user_id, wedding_site_factory
):
    # Arrange
    site = await wedding_site_factory(slug="titled", title="Before")
    # Act
    updated = await wedding_sites_service.update_for_user(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        updates={"title": None},
    )
    # Assert
    assert updated.title is None


@pytest.mark.asyncio
async def test__update_for_user__slug_conflict_with_other_site(
    wedding_sites_service: WeddingSitesService,
    site_owner_user_id,
    other_user_id,
    wedding_site_factory,
):
    # Arrange
    await wedding_site_factory(slug="taken", owner_user_id=site_owner_user_id)
    other_site = await wedding_site_factory(slug="movable", owner_user_id=other_user_id)
    # Act
    with pytest.raises(SlugConflictError):
        await wedding_sites_service.update_for_user(
            site_id=other_site.id,
            owner_user_id=other_user_id,
            updates={"slug": "taken"},
        )
    # Assert


@pytest.mark.asyncio
async def test__create__stores_config_and_status(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    payload = {"theme": "forest", "blocks": []}
    # Act
    site = await wedding_sites_service.create(
        owner_user_id=site_owner_user_id,
        slug="with-config",
        status=SiteStatus.PUBLISHED,
        config=payload,
        schema_version=2,
    )
    # Assert
    assert isinstance(site, WeddingSite)
    assert site.status == SiteStatus.PUBLISHED
    assert site.config == payload
    assert site.schema_version == 2


@pytest.mark.asyncio
async def test__list_agent_chat_history_for_site__returns_ordered_history_and_limit_slice(
    wedding_sites_service: WeddingSitesService, site_owner_user_id, wedding_site_factory
):
    # Arrange
    site = await wedding_site_factory(slug="history-site")
    await wedding_sites_service.append_agent_chat_turn(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        user_message="first user",
        assistant_message="first assistant",
    )
    await wedding_sites_service.append_agent_chat_turn(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        user_message="second user",
        assistant_message="second assistant",
    )
    # Act
    full_history = await wedding_sites_service.list_agent_chat_history_for_site(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
    )
    limited_history = await wedding_sites_service.list_agent_chat_history_for_site(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        max_turns=1,
    )
    # Assert
    assert full_history == [
        {"role": "user", "content": "first user"},
        {"role": "assistant", "content": "first assistant"},
        {"role": "user", "content": "second user"},
        {"role": "assistant", "content": "second assistant"},
    ]
    assert limited_history == [
        {"role": "user", "content": "second user"},
        {"role": "assistant", "content": "second assistant"},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("max_turns", "expected_history", "expected_error"),
    [
        (
            0,
            [],
            None,
        ),
        (
            2,
            [
                {"role": "user", "content": "u2"},
                {"role": "assistant", "content": "a2"},
                {"role": "user", "content": "u3"},
                {"role": "assistant", "content": "a3"},
            ],
            None,
        ),
        (
            -1,
            None,
            ValueError,
        ),
    ],
)
async def test__list_agent_chat_history_for_site__max_turns_values(
    wedding_sites_service: WeddingSitesService,
    site_owner_user_id,
    wedding_site_factory,
    max_turns: int,
    expected_history: list[dict[str, str]] | None,
    expected_error: type[Exception] | None,
):
    # Arrange
    slug_suffix = str(max_turns) if max_turns >= 0 else f"neg{-max_turns}"
    site = await wedding_site_factory(slug=f"history-max-turns-{slug_suffix}")
    await wedding_sites_service.append_agent_chat_turn(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        user_message="u1",
        assistant_message="a1",
    )
    await wedding_sites_service.append_agent_chat_turn(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        user_message="u2",
        assistant_message="a2",
    )
    await wedding_sites_service.append_agent_chat_turn(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        user_message="u3",
        assistant_message="a3",
    )
    # Act
    if expected_error is not None:
        with pytest.raises(expected_error):
            await wedding_sites_service.list_agent_chat_history_for_site(
                site_id=site.id,
                owner_user_id=site_owner_user_id,
                max_turns=max_turns,
            )
        return
    history = await wedding_sites_service.list_agent_chat_history_for_site(
        site_id=site.id,
        owner_user_id=site_owner_user_id,
        max_turns=max_turns,
    )
    # Assert
    assert history == expected_history


@pytest.mark.asyncio
async def test__list_agent_chat_history_for_site__missing_site(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    missing_id = uuid4()
    # Act
    with pytest.raises(WeddingSiteNotFoundError):
        await wedding_sites_service.list_agent_chat_history_for_site(
            site_id=missing_id,
            owner_user_id=site_owner_user_id,
        )
    # Assert
