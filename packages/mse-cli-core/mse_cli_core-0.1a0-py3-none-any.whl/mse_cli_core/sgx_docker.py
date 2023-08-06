"""mse_cli_core.sgx_docker module."""

from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple
from uuid import UUID

from pydantic import BaseModel


class SgxDockerConfig(BaseModel):
    """Definition of an mse docker running on a SGX hardware."""

    size: int
    host: str
    port: int
    app_id: UUID
    expiration_date: int
    code: Path
    application: str
    healthcheck: str
    signer_key: Path

    signer_key_mountpoint: ClassVar[str] = "/root/.config/gramine/enclave-key.pem"
    code_mountpoint: ClassVar[str] = "/tmp/app.tar"
    docker_label: ClassVar[str] = "mse-home"
    entrypoint: ClassVar[str] = "mse-run"

    def cmd(self) -> List[str]:
        """Serialize the docker command args."""
        return [
            "--size",
            f"{self.size}M",
            "--code",
            SgxDockerConfig.code_mountpoint,
            "--san",
            str(self.host),
            "--id",
            str(self.app_id),
            "--application",
            self.application,
            "--ratls",
            str(self.expiration_date),
        ]

    def ports(self) -> Dict[str, Tuple[str, str]]:
        """Define the docker ports."""
        return {"443/tcp": ("127.0.0.1", str(self.port))}

    def labels(self) -> Dict[str, str]:
        """Define the docker labels."""
        return {
            SgxDockerConfig.docker_label: "1",
            "healthcheck_endpoint": self.healthcheck,
        }

    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Define the docker volumes."""
        return {
            f"{self.code.resolve()}": {
                "bind": SgxDockerConfig.code_mountpoint,
                "mode": "rw",
            },
            "/var/run/aesmd": {"bind": "/var/run/aesmd", "mode": "rw"},
            f"{self.signer_key.resolve()}": {
                "bind": SgxDockerConfig.signer_key_mountpoint,
                "mode": "rw",
            },
        }

    @staticmethod
    def devices() -> List[str]:
        """Define the docker devices."""
        return [
            "/dev/sgx_enclave:/dev/sgx_enclave:rw",
            "/dev/sgx_provision:/dev/sgx_provision:rw",
            "/dev/sgx/enclave:/dev/sgx/enclave:rw",
            "/dev/sgx/provision:/dev/sgx/provision:rw",
        ]

    @staticmethod
    def load(docker_attrs: Dict[str, Any], docker_labels: Any):
        """Load the the docker configuration from the container."""
        dataMap: Dict[str, Any] = {}

        cmd = docker_attrs["Config"]["Cmd"]
        port = docker_attrs["HostConfig"]["PortBindings"]
        signer_key = next(
            filter(
                lambda mount: mount["Destination"]
                == SgxDockerConfig.signer_key_mountpoint,
                docker_attrs["Mounts"],
            )
        )
        code = next(
            filter(
                lambda mount: mount["Destination"] == SgxDockerConfig.code_mountpoint,
                docker_attrs["Mounts"],
            )
        )

        i = 0
        while i < len(cmd):
            key = cmd[i][2:]
            if i + 1 == len(cmd):
                dataMap[key] = True
                i += 1
                break

            if cmd[i + 1].startswith("--"):
                dataMap[key] = True
                i += 1
                continue

            dataMap[key] = cmd[i + 1]
            i += 2

        return SgxDockerConfig(
            size=int(dataMap["size"][:-1]),
            host=dataMap["san"],
            app_id=UUID(dataMap["id"]),
            expiration_date=int(dataMap["ratls"]),
            code=Path(code["Source"]),
            application=dataMap["application"],
            port=int(port["443/tcp"][0]["HostPort"]),
            healthcheck=docker_labels["healthcheck_endpoint"],
            signer_key=Path(signer_key["Source"]),
        )
