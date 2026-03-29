from typing import cast
from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.common.dependencies import get_current_user
from domains.users.models import User
from domains.wedding_sites.dependencies import get_wedding_sites_service
from domains.wedding_sites.exceptions import (
    InvalidSlugError,
    SlugConflictError,
    WeddingSiteNotFoundError,
)
from domains.wedding_sites.service import WeddingSitePartialUpdate, WeddingSitesService

from .schemas import WeddingSiteRead, WeddingSiteUpdate


async def patch_wedding_site(
    site_id: UUID,
    body: WeddingSiteUpdate,
    current_user: User = Depends(get_current_user),
    service: WeddingSitesService = Depends(get_wedding_sites_service),
) -> WeddingSiteRead:
    raw_updates = body.model_dump(exclude_unset=True)
    updates = cast(WeddingSitePartialUpdate, raw_updates)
    try:
        site = await service.update_for_user(
            site_id=site_id,
            owner_user_id=current_user.id,
            updates=updates,
        )
    except WeddingSiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except InvalidSlugError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e
    except SlugConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    return WeddingSiteRead.model_validate(site)
