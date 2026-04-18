from uuid import UUID

from domains.contact.models import ContactSubmission
from domains.contact.repository import ContactRepository
from utils.logging import get_logger

logger = get_logger(__name__)


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def submit_message(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
        user_id: UUID | None,
        is_authenticated: bool,
    ) -> ContactSubmission:
        submission = ContactSubmission(
            user_id=user_id,
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        created = await self.repository.create(submission)
        logger.info(
            "Contact form submission stored (id=%s, authenticated=%s, user_id=%s, message_length=%s)",
            created.id,
            is_authenticated,
            user_id,
            len(message),
        )
        return created
