from uuid import UUID

from fastapi import Depends, HTTPException, status

from api.common.dependencies import get_current_user
from domains.users.models import User
from domains.wedding_sites.dependencies import get_wedding_sites_service
from domains.wedding_sites.exceptions import WeddingSiteNotFoundError
from domains.wedding_sites.service import WeddingSitesService

from .schemas import WeddingSiteRead


async def get_wedding_site(
    site_id: UUID,
    current_user: User = Depends(get_current_user),
    service: WeddingSitesService = Depends(get_wedding_sites_service),
) -> WeddingSiteRead:
    try:
        site = await service.get_by_id_for_user(
            site_id=site_id,
            owner_user_id=current_user.id,
        )
    except WeddingSiteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return WeddingSiteRead.model_validate(site)
