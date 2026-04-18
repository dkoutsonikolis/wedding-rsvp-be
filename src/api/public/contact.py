from fastapi import Depends, HTTPException, Request, Response, status

from api.common.dependencies import get_current_user_optional
from api.public.schemas import ContactSubmitRequest
from config import settings
from domains.contact.dependencies import get_contact_service
from domains.contact.service import ContactService
from domains.users.models import User
from middleware.limiter import limiter


@limiter.limit(settings.RATE_LIMIT_PUBLIC_CONTACT)
async def submit_contact_message(
    request: Request,
    body: ContactSubmitRequest,
    user: User | None = Depends(get_current_user_optional),
    contact_service: ContactService = Depends(get_contact_service),
) -> Response:
    sender_email = user.email if user is not None else body.email
    if sender_email is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="email: Field required",
        )

    await contact_service.submit_message(
        name=body.name,
        email=sender_email,
        subject=body.subject,
        message=body.message,
        user_id=user.id if user is not None else None,
        is_authenticated=user is not None,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
