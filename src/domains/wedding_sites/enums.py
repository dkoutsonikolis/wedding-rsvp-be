from enum import StrEnum


class SiteStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class AgentMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
