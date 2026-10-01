"""Configuration loaded from environment variables / .env file."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration is missing or malformed."""


def guid_from_crn(crn: str) -> str:
    """Extract the service instance GUID from a CRN.

    CRN format: crn:v1:bluemix:public:cloud-object-storage:global:a/<acct>:<GUID>::
    """
    parts = crn.split(":")
    if len(parts) < 8 or not parts[7]:
        raise ConfigError(f"Invalid COS_INSTANCE_CRN: {crn!r}")
    return parts[7]


@dataclass(frozen=True)
class Settings:
    admin_api_key: str
    account_id: str
    instance_crn: str
    endpoint: str
    bucket: str
    prefix: str = "cosdemo"

    @property
    def instance_guid(self) -> str:
        return guid_from_crn(self.instance_crn)

    @property
    def readers_group(self) -> str:
        return f"{self.prefix}-cos-readers"

    @property
    def writers_group(self) -> str:
        return f"{self.prefix}-cos-writers"

    @property
    def reader_service_id(self) -> str:
        return f"{self.prefix}-reader-sid"

    @property
    def writer_service_id(self) -> str:
        return f"{self.prefix}-writer-sid"


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def get_settings() -> Settings:
    return Settings(
        admin_api_key=_require("IBMCLOUD_API_KEY"),
        account_id=_require("IBM_ACCOUNT_ID"),
        instance_crn=_require("COS_INSTANCE_CRN"),
        endpoint=_require("COS_ENDPOINT"),
        bucket=_require("COS_BUCKET"),
        prefix=os.getenv("NAME_PREFIX", "cosdemo").strip() or "cosdemo",
    )
