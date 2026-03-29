from fastapi import Depends, HTTPException, status

from api.common.dependencies import get_current_user
from domains.users.models import User
from domains.wedding_sites.dependencies import get_wedding_sites_service
from domains.wedding_sites.exceptions import InvalidSlugError, SlugConflictError
from domains.wedding_sites.service import WeddingSitesService

from .schemas import WeddingSiteCreate, WeddingSiteRead


async def create_wedding_site(
    body: WeddingSiteCreate,
    current_user: User = Depends(get_current_user),
    service: WeddingSitesService = Depends(get_wedding_sites_service),
) -> WeddingSiteRead:
    try:
        site = await service.create(
            owner_user_id=current_user.id,
            title=body.title,
            slug=body.slug,
            status=body.status,
            config=body.config,
            schema_version=body.schema_version,
        )
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
