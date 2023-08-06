import logging
import time
from dataclasses import dataclass
from os import path

import requests

from edge_addons_api.exceptions import UploadException

logger = logging.getLogger(__name__)


class ResponseStatus:
    SUCCEEDED = "Succeeded"
    IN_PROGRESS = "InProgress"
    FAILED = "Failed"


@dataclass
class Options:
    product_id: str
    client_id: str
    client_secret: str
    access_token_url: str


class Client:

    BASE_URL = "https://api.addons.microsoftedge.microsoft.com"

    def __init__(self, options: Options):
        self.options = options

    def submit(self, file_path: str, notes: str) -> str:
        if not path.exists(file_path):
            raise FileNotFoundError(f"Unable to locate file at {file_path}")

        access_token = self._get_access_token()
        operation_id = self._upload(file_path, access_token)
        self._check_upload(operation_id, access_token)
        return self._publish(notes, access_token)

    def fetch_publish_status(self, operation_id: str) -> dict:
        access_token = self._get_access_token()
        response = requests.get(
            self._publish_status_endpoint(operation_id),
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        response.raise_for_status()
        return response.json()

    def _publish(self, notes: str, access_token: str) -> str:
        response = requests.post(
            self._publish_endpoint(),
            data={"notes": notes},
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        response.raise_for_status()

        logger.debug(f"Publish response: {response.content.decode()}")

        return response.headers["Location"]

    def _upload(self, file_path: str, access_token: str) -> str:
        with open(file_path, "rb") as f:
            response = requests.post(
                self._upload_endpoint(),
                data=f,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/zip",
                },
            )

        response.raise_for_status()

        return response.headers["Location"]

    def _check_upload(
        self,
        operation_id,
        access_token: str,
        retry_count: int = 5,
        sleep_seconds: int = 3,
    ) -> str:
        upload_status = ""
        attempts = 0

        while upload_status != ResponseStatus.SUCCEEDED and attempts < retry_count:
            response = requests.get(
                self._status_endpoint(operation_id),
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

            response.raise_for_status()
            response_json = response.json()

            logger.debug(f"Status response: {response_json}")
            upload_status = response_json["status"]
            if upload_status == ResponseStatus.FAILED:
                raise UploadException(
                    response_json["status"],
                    response_json["message"],
                    response_json["errorCode"],
                    response_json["errors"],
                )
            elif upload_status == ResponseStatus.IN_PROGRESS:
                time.sleep(sleep_seconds)

        return upload_status

    def _get_access_token(self) -> str:
        response = requests.post(
            self.options.access_token_url,
            data={
                "client_id": self.options.client_id,
                "scope": f"{self.BASE_URL}/.default",
                "client_secret": self.options.client_secret,
                "grant_type": "client_credentials",
            },
        )

        response.raise_for_status()

        json = response.json()

        return json["access_token"]

    def _product_endpoint(self) -> str:
        return f"{self.BASE_URL}/v1/products/{self.options.product_id}"

    def _publish_endpoint(self) -> str:
        return f"{self._product_endpoint()}/submissions"

    def _upload_endpoint(self) -> str:
        return f"{self._publish_endpoint()}/draft/package"

    def _status_endpoint(self, operation_id: str) -> str:
        return f"{self._upload_endpoint()}/operations/{operation_id}"

    def _publish_status_endpoint(self, operation_id: str) -> str:
        return f"{self._publish_endpoint()}/operations/{operation_id}"
