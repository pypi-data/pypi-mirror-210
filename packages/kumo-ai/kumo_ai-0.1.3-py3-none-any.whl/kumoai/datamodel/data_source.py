from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic.dataclasses import dataclass


class DataSourceType(str, Enum):
    SNOWFLAKE = "SNOWFLAKE"
    S3 = "S3"


@dataclass
class ResourceTimestamps:
    created_at: datetime
    updated_at: datetime


@dataclass
class SnowflakeConnectorResourceConfig:
    name: str
    account: str
    warehouse: str
    database: str
    schema_name: str
    type: Literal['snowflake'] = 'snowflake'


@dataclass
class ConnectorResponse:
    id: str
    timestamps: ResourceTimestamps
    config: SnowflakeConnectorResourceConfig


@dataclass
class UsernamePassword:
    r"""Basic authentication with username/password

    Attributes:
        username (SecretStr): Account user name
        password (SecretStr): Account password

    """
    username: str
    password: str


@dataclass
class SnowflakeConnectorArgs:
    config: SnowflakeConnectorResourceConfig
    credentials: UsernamePassword
