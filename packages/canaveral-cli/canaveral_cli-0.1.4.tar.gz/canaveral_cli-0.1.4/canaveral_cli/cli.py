"""This module provides the Canaveral CLI"""
# canaveral_cli/cli.py

from typing import Optional
from pathlib import Path
import typer
import shutil
import yaml
from canaveral_cli import PACKAGEDIR, __app_name__, __version__
from canaveral_cli.definitions import get_updated_type_data
from canaveral_cli.merge_oam import merge_oam
from canaveral_cli.create_oam import oam_form, create_oam_file
from rich import print

app = typer.Typer()

def _version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.command()
def definitions():
    """Retrieve OAM types from source and store them locally. Needed for creating OAM files"""
    get_updated_type_data()

@app.command()
def create():
    """Interactively Create a OAM file"""
    oam_form_data = oam_form()
    # with open(PACKAGEDIR/"data/raw_data.yaml", "w") as f:
    #     yaml.dump(oam_form_data, f)
    #     f.close()
    # return
    # oam_form_data = yaml.load(open(PACKAGEDIR/"data/raw_data.yaml"), Loader=yaml.FullLoader)
    create_oam_file(oam_form_data)

@app.command()
def default():
    """Create the default OAM file"""
    shutil.copyfile(PACKAGEDIR/"data/templates/vela_default.yaml", "vela.yaml")
    print("✅ vela.yaml created successfully! ")
    
@app.command()
def merge(dev: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True),
          ops: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True)):
    """Merge Dev OAM file with Operations OAM file"""
    dev_yaml = yaml.load(dev.open(), Loader=yaml.FullLoader)
    ops_yaml = yaml.load(ops.open(), Loader=yaml.FullLoader)

    merged = merge_oam(dev_yaml, ops_yaml)
    
    with open("vela.yaml", "w") as f:
        yaml.dump(merged, f)
        f.close()

    #* Library hiyapyco doesn't work as expected, it doesn't merge nested lists
    # conf = hiyapyco.load([dev.absolute().as_posix(), ops.absolute().as_posix()], method=hiyapyco.METHOD_MERGE, interpolate=True)
    # print(type(conf))
    # with open("vela.yaml", "w") as f:
    #     f.write(hiyapyco.dump(conf, default_flow_style=False))
    #     f.close()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return

