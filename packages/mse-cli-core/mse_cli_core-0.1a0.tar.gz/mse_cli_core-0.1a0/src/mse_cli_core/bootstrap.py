"""mse_cli_core.bootstrap module."""

import time
from typing import Any, Dict, Optional, Union
from uuid import UUID

import requests
from pydantic import BaseModel

from mse_cli_core.base64 import base64url_encode


class ConfigurationPayload(BaseModel):
    """Definition of the bootstrap server payload."""

    app_id: UUID
    secrets: Optional[Any]
    sealed_secrets: Optional[bytes]
    code_secret_key: Optional[bytes]

    def payload(self) -> Dict[str, Any]:
        """Build the payload to send to the configuration server."""
        data: Dict[str, Any] = {
            "uuid": str(self.app_id),
        }

        if self.secrets:
            data["app_secrets"] = self.secrets

        if self.sealed_secrets:
            data["app_sealed_secrets"] = base64url_encode(self.sealed_secrets)

        if self.code_secret_key:
            data["code_secret_key"] = self.code_secret_key.hex()

        return data


def send_secrets(url: str, data: Dict[str, Any], verify: Union[bool, str] = True):
    """Send the secrets to the configuration server."""
    r = requests.post(
        url=url,
        json=data,
        headers={"Content-Type": "application/json"},
        verify=verify,
        timeout=60,
    )

    if not r.ok:
        raise Exception(
            f"Fail to send secrets data (Response {r.status_code} {r.text})"
        )


def wait_for_conf_server(url: str, verify: Union[bool, str] = True):
    """Hold on until the configuration server is up and listing."""
    while not is_waiting_for_secrets(url, verify):
        time.sleep(5)


def is_waiting_for_secrets(url: str, verify: Union[bool, str] = True) -> bool:
    """Check whether the configuration server is up."""
    try:
        response = requests.get(url=url, verify=verify, timeout=5)

        if response.status_code == 200 and "Mse-Status" in response.headers:
            return True
    except requests.exceptions.SSLError:
        return False

    return False


def wait_for_app_server(
    url: str,
    healthcheck_endpoint: str,
    verify: Union[bool, str] = True,
):
    """Hold on until the configuration server is stopped and the app starts."""
    while not is_ready(url, healthcheck_endpoint, verify):
        time.sleep(5)


def is_ready(
    url: str, healthcheck_endpoint: str, verify: Union[bool, str] = True
) -> bool:
    """Check whether the app server is up."""
    try:
        response = requests.get(
            url=f"{url}{healthcheck_endpoint}",
            verify=verify,
            timeout=5,
        )

        if response.status_code != 503 and "Mse-Status" not in response.headers:
            return True
    except requests.exceptions.SSLError:
        return False
    except requests.exceptions.ConnectionError:
        return False

    return False
