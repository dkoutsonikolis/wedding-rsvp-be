import re
from uuid import uuid4

import pytest

from domains.wedding_sites.enums import SiteStatus
from domains.wedding_sites.exceptions import (
    InvalidSlugError,
    SlugConflictError,
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
    await wedding_site_factory(slug="owner-a")
    await wedding_site_factory(slug="owner-b")
    await wedding_sites_service.create(owner_user_id=other_user_id, slug="other-only")
    # Act
    mine = await wedding_sites_service.list_for_user(site_owner_user_id)
    theirs = await wedding_sites_service.list_for_user(other_user_id)
    # Assert
    assert len(mine) == 2
    assert {s.slug for s in mine} == {"owner-a", "owner-b"}
    assert len(theirs) == 1
    assert theirs[0].slug == "other-only"


@pytest.mark.asyncio
async def test__create__duplicate_slug_conflict(
    wedding_sites_service: WeddingSitesService, wedding_site_factory
):
    # Arrange
    await wedding_site_factory(slug="dup-slug")
    # Act
    with pytest.raises(SlugConflictError):
        await wedding_site_factory(slug="dup-slug")
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
async def test__create__same_title_gets_incremented_slug(
    wedding_sites_service: WeddingSitesService, site_owner_user_id
):
    # Arrange
    # Act
    first = await wedding_sites_service.create(
        owner_user_id=site_owner_user_id, title="Shared", slug=None
    )
    second = await wedding_sites_service.create(
        owner_user_id=site_owner_user_id, title="Shared", slug=None
    )
    # Assert
    assert first.slug == "shared"
    assert second.slug == "shared-2"


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
    wedding_sites_service: WeddingSitesService, site_owner_user_id, wedding_site_factory
):
    # Arrange
    await wedding_site_factory(slug="taken")
    other = await wedding_site_factory(slug="movable")
    # Act
    with pytest.raises(SlugConflictError):
        await wedding_sites_service.update_for_user(
            site_id=other.id,
            owner_user_id=site_owner_user_id,
            updates={"slug": "taken"},
        )
    # Assert


@pytest.mark.asyncio
async def test__delete_for_user__removes_row(
    wedding_sites_service: WeddingSitesService, site_owner_user_id, wedding_site_factory
):
    # Arrange
    site = await wedding_site_factory(slug="to-delete")
    # Act
    await wedding_sites_service.delete_for_user(site_id=site.id, owner_user_id=site_owner_user_id)
    # Assert
    remaining = await wedding_sites_service.list_for_user(site_owner_user_id)
    assert remaining == []


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
