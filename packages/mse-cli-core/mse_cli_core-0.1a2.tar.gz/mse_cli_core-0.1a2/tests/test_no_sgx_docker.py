"""Test model/args.py."""

import filecmp
from pathlib import Path

from mse_cli_core.no_sgx_docker import NoSgxDockerConfig
from mse_cli_core.sgx_docker import SgxDockerConfig


def test_load():
    """Test `load` function."""
    toml = Path(__file__).parent / "data/args_custom.toml"
    conf = NoSgxDockerConfig.load(path=toml)

    ref_conf = NoSgxDockerConfig(
        host="localhost",
        app_cert="cert.pem",
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert conf == ref_conf

    toml = Path(__file__).parent / "data/args_ratls.toml"
    conf = NoSgxDockerConfig.load(path=toml)

    ref_conf = NoSgxDockerConfig(
        host="localhost",
        expiration_date=1714058115,
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert conf == ref_conf


def test_save(workspace: Path):
    """Test the `save` method."""
    toml = Path(__file__).parent / "data/args_custom.toml"
    conf = NoSgxDockerConfig.load(path=toml)

    tmp_toml = workspace / "args.toml"
    conf.save(tmp_toml)

    assert filecmp.cmp(toml, tmp_toml)

    toml = Path(__file__).parent / "data/args_ratls.toml"
    conf = NoSgxDockerConfig.load(path=toml)

    tmp_toml = workspace / "args.toml"
    conf.save(tmp_toml)

    assert filecmp.cmp(toml, tmp_toml)


def test_from_sgx():
    """Test the `from_sgx` method."""
    ref_conf = NoSgxDockerConfig(
        host="localhost",
        expiration_date=1714058115,
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    conf = NoSgxDockerConfig.from_sgx(
        SgxDockerConfig(
            size=4096,
            host="localhost",
            port=7788,
            app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
            expiration_date=1714058115,
            code="/home/cosmian/workspace/sgx_operator/code.tar",
            application="app:app",
            healthcheck="/health",
            signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
        )
    )

    assert conf == ref_conf


def test_volumes():
    """Test `volumes` function."""
    ref_conf = NoSgxDockerConfig(
        host="localhost",
        expiration_date=1714058115,
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert ref_conf.volumes(Path("/tmp/code.tar")) == {
        "/tmp/code.tar": {
            "bind": "/tmp/app.tar",
            "mode": "rw",
        }
    }

    ref_conf = NoSgxDockerConfig(
        host="localhost",
        app_cert="/app/cert.pem",
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert ref_conf.volumes(Path("/tmp/code.tar")) == {
        "/tmp/code.tar": {
            "bind": "/tmp/app.tar",
            "mode": "rw",
        },
        "/app/cert.pem": {
            "bind": "/tmp/cert.pem",
            "mode": "rw",
        },
    }


def test_cmd():
    """Test `cmd` function."""
    ref_conf = NoSgxDockerConfig(
        host="localhost",
        expiration_date=1714058115,
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert ref_conf.cmd() == [
        "--size",
        "4096M",
        "--code",
        "/tmp/app.tar",
        "--san",
        "localhost",
        "--id",
        "63322f85-1ff8-4483-91ae-f18d7398d157",
        "--application",
        "app:app",
        "--dry-run",
        "--ratls",
        "1714058115",
    ]

    ref_conf = NoSgxDockerConfig(
        host="localhost",
        app_cert="cert.pem",
        size=4096,
        app_id="63322f85-1ff8-4483-91ae-f18d7398d157",
        application="app:app",
    )

    assert ref_conf.cmd() == [
        "--size",
        "4096M",
        "--code",
        "/tmp/app.tar",
        "--san",
        "localhost",
        "--id",
        "63322f85-1ff8-4483-91ae-f18d7398d157",
        "--application",
        "app:app",
        "--dry-run",
        "--certificate",
        "/tmp/cert.pem",
    ]
