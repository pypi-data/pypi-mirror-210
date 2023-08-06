"""The CLI of kthutils"""

import typer
import typerconf as config
import kthutils.ug

cli = typer.Typer(name="kthutils",
                  help="A collection of tools useful at KTH")

config.add_config_cmd(cli)
cli.add_typer(kthutils.ug.cli)

if __name__ == "__main__":
    cli()
