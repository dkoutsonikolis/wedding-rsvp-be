from pydantic import BaseModel, EmailStr, Field


class ContactSubmitRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr | None = Field(
        default=None,
        description="Preferred reply-to email for anonymous users; ignored when authenticated",
    )
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
