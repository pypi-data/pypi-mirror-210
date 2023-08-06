"""
Top-level entrypoint for the command line interface.
"""


import typer

import module_qc_database_tools
from module_qc_database_tools.cli.generate_yarr_config import (
    main as generate_yarr_config,
)
from module_qc_database_tools.cli.register_component import main as register_component

# subcommands
app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", help="Print the current version."),
    prefix: bool = typer.Option(
        False, "--prefix", help="Print the path prefix for data files."
    ),
) -> None:
    """
    Manage top-level options
    """
    if version:
        typer.echo(f"module-qc-database-tools v{module_qc_database_tools.__version__}")
        raise typer.Exit()
    if prefix:
        typer.echo(module_qc_database_tools.data.resolve())
        raise typer.Exit()


app.command("generate-yarr-config")(generate_yarr_config)
app.command("register-component")(register_component)

# for generating documentation using mkdocs-click
typer_click_object = typer.main.get_command(app)
