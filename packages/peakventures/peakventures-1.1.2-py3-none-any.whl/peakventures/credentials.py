import json
import os
from typing import Any

S3_CREDENTIALS_NAME = "db-s3"
AZURE_CREDENTIALS_NAME = "db-azure-storage"
API_CREDENTIALS_NAME = "db-api"


def _get_dbutils() -> Any:
    from pyspark.sql import SparkSession
    from pyspark.dbutils import DBUtils
    return DBUtils(SparkSession.getActiveSession())


def _get_credential(name: str) -> str:
    if os.getenv("DEVELOPMENT"):
        result = {
            S3_CREDENTIALS_NAME: os.getenv("S3_CREDENTIALS"),
            AZURE_CREDENTIALS_NAME: os.getenv("AZURE_CREDENTIALS"),
            API_CREDENTIALS_NAME: os.getenv("API_CREDENTIALS")
        }.get(name)
    else:
        dbutils = _get_dbutils()
        result = dbutils.secrets.get("credentials", name)

    if not result:
        raise ValueError(f"Credentials {name} not found.")

    return result


def get_credentials(name: str) -> str:
    """Get credentials from the remote storage."""
    return _get_credential(name)


def get_credentials_json(name: str) -> Any:
    """Get credentials from the remote storage."""
    return json.loads(get_credentials(name))


__all__ = [
    "get_credentials",
    "get_credentials_json",
]
