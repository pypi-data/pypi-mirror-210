import json
from pathlib import Path
from typing import List, Optional

import itkdb
import jsbeautifier
import typer
from pymongo import MongoClient

import module_qc_database_tools
from module_qc_database_tools.chip_config_api import ChipConfigAPI
from module_qc_database_tools.core import Module
from module_qc_database_tools.utils import (
    chip_uid_to_serial_number,
    get_layer_from_serial_number,
)

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.command()
def main(
    serial_number: str = typer.Option(..., "-sn", "--sn", help="ATLAS serial number"),
    chip_template_path: Path = typer.Option(
        (module_qc_database_tools.data / "YARR" / "chip_template.json").resolve(),
        "-ch",
        "--chipTemplate",
        help="Default chip template from which the chip configs are generated.",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "-o",
        "--outdir",
        help="Path to output directory. If not specified, will store configs in mongodb.",
        exists=False,
        writable=True,
    ),
    modes: List[str] = typer.Option(
        ["warm", "cold", "LP"],
        "-m",
        "--mode",
        help="Modes to generate configs for.",
    ),
    version: str = typer.Option(
        "latest",  ## "TESTONWAFER", "MODULE/INITIAL_WARM", "etc"], ## use stage/test names?
        "-v",
        "--version",
        help="Generate chip configs, default is 'latest'. Possible choices: 'TESTONWAFER'...",
    ),
    mongo_uri: str = typer.Option(
        "mongodb://localhost:27017",
        "-u",
        "--uri",
        help="mongo URI (see documentation for mongo client)",
    ),
    itkdb_access_code1: Optional[str] = typer.Option(
        None, "--accessCode1", help="Access Code 1 for production DB"
    ),
    itkdb_access_code2: Optional[str] = typer.Option(
        None, "--accessCode2", help="Access Code 2 for production DB"
    ),
):
    """
    Main executable for generating yarr config.
    """
    if itkdb_access_code1 and itkdb_access_code2:
        user = itkdb.core.User(
            access_code1=itkdb_access_code1, access_code2=itkdb_access_code2
        )
        client = itkdb.Client(user=user)
    else:
        client = itkdb.Client()

    module = Module(client, serial_number)
    typer.echo("INFO: Getting layer-dependent config from module SN...")
    layer_config = get_layer_from_serial_number(serial_number)

    chip_template = json.loads(chip_template_path.read_text())

    for suffix in modes:
        connectivity_path = Path(output_dir or "", module.name).joinpath(
            f"{module.name}_{layer_config}{'_'+suffix if suffix else ''}.json"
        )

        generated_configs = module.generate_config(
            chip_template, layer_config, suffix=suffix, version=version
        )

        if output_dir:
            save_configs_local(generated_configs, connectivity_path)
        else:
            mongo_client = MongoClient(mongo_uri)
            chip_config_client = ChipConfigAPI(mongo_client)
            save_configs_mongo(generated_configs, chip_config_client, suffix)


def save_configs_local(configs, connectivity_path):
    """
    Save the configs generated to disk.
    """
    connectivity_path.parent.mkdir(parents=True, exist_ok=True)

    connectivity_path.write_text(json.dumps(configs["module"], indent=4))
    typer.echo(f"module connectivity file saved to {connectivity_path}")

    for chip_config, chip_spec in zip(configs["module"]["chips"], configs["chips"]):
        output_path = connectivity_path.parent.joinpath(chip_config["config"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ## needed to avoid having chip config file at 14MB (but slow)
        beautified = jsbeautifier.beautify(
            json.dumps(chip_spec), jsbeautifier.default_options()
        )
        output_path.write_text(beautified)  ## file size 1.9MB
        # output_path.write_text(json.dumps(chip_spec, indent=4)) ## file size 14MB due to linebreaks
        # output_path.write_text(json.dumps(chip_spec)) ## file size is 1.8M, no linebreak
        typer.echo(f"chip config file saved to {output_path}")


def save_configs_mongo(configs, chip_config_client, mode):
    """
    Save the configs generated to mongo.
    """
    for chip_spec in configs["chips"]:
        chip_serial_number = chip_uid_to_serial_number(
            chip_spec["RD53B"]["Parameter"]["Name"]
        )
        base_commit_id = chip_config_client.create_config(
            chip_serial_number, "MODULE/INITIAL_WARM", branch=mode
        )
        new_commit_id = chip_config_client.commit(
            base_commit_id,
            chip_spec,
            "initial generation from module-qc-database-tools",
        )
        typer.echo(
            f"chip config file saved to mongodb from {base_commit_id} ➜ {new_commit_id}"
        )


if __name__ == "__main__":
    typer.run(main)
