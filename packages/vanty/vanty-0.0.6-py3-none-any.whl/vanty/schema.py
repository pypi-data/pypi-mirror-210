from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    NOT_FETCHED = "not_fetched"


class LicenseVerifiedHttpResponse(BaseModel):
    license_id: str
    token_id: str | None
    token_secret: str | None
    is_valid: bool

    @classmethod
    def error(cls):
        return cls(license_id="", token_id="", token_secret="", is_valid=False)


class DownloadProjectHttpResponse(BaseModel):
    url: str | None
    project_id: str | None
    version: str | None
    is_valid: bool | None
    profile_id: str | None
    profile_status: ProfileStatus | None

    @classmethod
    def error(cls):
        return cls(
            url="",
            project_id="",
            version="",
            is_valid=False,
            profile_id="",
            profile_status=ProfileStatus.NOT_FETCHED,
        )
