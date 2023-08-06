from __future__ import annotations

import warnings

import pytest
from typer.testing import CliRunner

from module_qc_database_tools.cli import app


@pytest.fixture()
def runner():
    return CliRunner(mix_stderr=False)


def test_generate_yarr_config_help(runner):
    result = runner.invoke(
        app,
        args=[
            "generate-yarr-config",
            "-h",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr


def test_register_component_help(runner):
    result = runner.invoke(
        app,
        args=[
            "register-component",
            "-h",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr


def test_generate_yarr_config(runner, tmp_path):
    warnings.simplefilter("ignore", ResourceWarning)

    output_dir = tmp_path / "configs"

    result = runner.invoke(
        app,
        args=[
            "generate-yarr-config",
            "-o",
            output_dir,
            "--sn",
            "20UPGR92101041",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stderr

    paths = [p.relative_to(output_dir) for p in list(output_dir.rglob("*"))]
    assert sorted(map(str, paths)) == [
        "20UPGR92101041",
        "20UPGR92101041/20UPGR92101041_L2_LP.json",
        "20UPGR92101041/20UPGR92101041_L2_cold.json",
        "20UPGR92101041/20UPGR92101041_L2_warm.json",
        "20UPGR92101041/L2_LP",
        "20UPGR92101041/L2_LP/0x15479_L2_LP.json",
        "20UPGR92101041/L2_LP/0x15489_L2_LP.json",
        "20UPGR92101041/L2_LP/0x15499_L2_LP.json",
        "20UPGR92101041/L2_LP/0x154a9_L2_LP.json",
        "20UPGR92101041/L2_cold",
        "20UPGR92101041/L2_cold/0x15479_L2_cold.json",
        "20UPGR92101041/L2_cold/0x15489_L2_cold.json",
        "20UPGR92101041/L2_cold/0x15499_L2_cold.json",
        "20UPGR92101041/L2_cold/0x154a9_L2_cold.json",
        "20UPGR92101041/L2_warm",
        "20UPGR92101041/L2_warm/0x15479_L2_warm.json",
        "20UPGR92101041/L2_warm/0x15489_L2_warm.json",
        "20UPGR92101041/L2_warm/0x15499_L2_warm.json",
        "20UPGR92101041/L2_warm/0x154a9_L2_warm.json",
    ]
