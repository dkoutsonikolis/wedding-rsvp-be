from sqlmodel.ext.asyncio.session import AsyncSession

from domains.contact.models import ContactSubmission


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, submission: ContactSubmission) -> ContactSubmission:
        self.session.add(submission)
        await self.session.commit()
        await self.session.refresh(submission)
        return submission
