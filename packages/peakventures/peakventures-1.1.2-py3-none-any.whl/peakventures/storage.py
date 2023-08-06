import json
from io import BytesIO
from typing import Any

import boto3
from azure.storage.blob import BlobClient, BlobServiceClient

from peakventures.credentials import get_credentials, get_credentials_json, AZURE_CREDENTIALS_NAME, S3_CREDENTIALS_NAME

CONTAINER_NAME = "models"


def _store_model_azure(name: str, payload: str) -> None:
    connection_string = get_credentials(AZURE_CREDENTIALS_NAME)

    blob_client: BlobClient = (
        BlobServiceClient.from_connection_string(connection_string)
        .get_container_client(CONTAINER_NAME)
        .get_blob_client(name)
    )

    blob_client.upload_blob(payload, overwrite=True)


def _store_model_s3(name: str, payload: str) -> None:
    credentials = get_credentials_json(S3_CREDENTIALS_NAME)

    s3 = boto3.client(
        "s3",
        endpoint_url=credentials["endpoint_url"],
        aws_access_key_id=credentials["access_key_id"],
        aws_secret_access_key=credentials["secret_access_key"],
    )

    with BytesIO(payload.encode("utf-8")) as buffer:
        s3.upload_fileobj(buffer, CONTAINER_NAME, name)


def store_model(name: str, payload: Any) -> None:
    """Store model on the remote storage."""
    json_payload = json.dumps(payload)

    _store_model_azure(name, json_payload)
    _store_model_s3(name, json_payload)


__all__ = [
    "store_model"
]
