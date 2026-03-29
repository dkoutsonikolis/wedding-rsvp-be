from fastapi import Depends

from api.common.dependencies import get_current_user
from domains.users.models import User
from domains.wedding_sites.dependencies import get_wedding_sites_service
from domains.wedding_sites.service import WeddingSitesService

from .schemas import WeddingSiteRead


async def list_wedding_sites(
    current_user: User = Depends(get_current_user),
    service: WeddingSitesService = Depends(get_wedding_sites_service),
) -> list[WeddingSiteRead]:
    sites = await service.list_for_user(current_user.id)
    return [WeddingSiteRead.model_validate(s) for s in sites]
