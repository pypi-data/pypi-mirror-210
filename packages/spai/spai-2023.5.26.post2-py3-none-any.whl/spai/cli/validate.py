import os
import yaml
from pydantic import BaseModel
from typing import Union, List


class ScriptConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    run_every: Union[int, None] = None  # seconds
    run_on_start: bool = True


class NotebookConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    run_every: Union[int, None] = None  # seconds
    run_on_start: bool = True


class APIConfig(BaseModel):
    name: str
    command: Union[str, None] = None


class UIConfig(BaseModel):
    name: str
    command: str  # steamlit, javascript, ...


class Config(BaseModel):
    project: Union[str, None] = None
    scripts: Union[List[ScriptConfig], None] = None
    notebooks: Union[List[NotebookConfig], None] = None
    apis: Union[List[APIConfig], None] = None
    uis: Union[List[UIConfig], None] = None


def validate_folder(dir, folder, typer):
    if not os.path.exists(dir / folder):
        raise typer.BadParameter(f"No {folder} directory found in '{dir}'.")


def validate_item(dir, folder, item, name, typer, file="main.py"):
    # check name
    if not item.name:
        raise typer.BadParameter(f"{name} '{item.name}' is missing 'name' attribute.")
    # check folder has folder with item name
    if not os.path.exists(dir / folder / item.name):
        raise typer.BadParameter(
            f"{name} '{item.name}' cannot be found in {dir}/{folder}."
        )
    # check folder has file
    if not file in os.listdir(dir / folder / item.name):
        raise typer.BadParameter(f"{name} '{item.name}' is missing file 'main.py'.")
    # TODO: check optionals: reqs, env...


def load_and_validate_config(dir, typer, cloud):
    # check dir exists
    if not dir.exists():
        raise typer.BadParameter(f"Directory '{dir}' does not exist.")
    # check dir is a spai project
    if not "spai.config.yml" in os.listdir(dir):
        raise typer.BadParameter(
            f"Directory '{dir}' is not a spai project. No spai.config.yml file found."
        )
    # load config
    config = {}
    with open(dir / "spai.config.yml", "r") as f:
        config = yaml.safe_load(f)
    if not config:
        raise typer.BadParameter(f"spai.config.yml file is empty.")
    config = Config(**config)
    # TODO: check if project name is already taken in cloud, locally is not a problem
    config.project = dir.name if not config.project else config.project
    # check scripts
    if config.scripts:
        # check project has scripts folder
        validate_folder(dir, "scripts", typer)
        for script in config.scripts:
            validate_item(dir, "scripts", script, "script", typer)
    else:
        typer.echo("No scripts found in spai.config.yml.")
    # check notebooks
    if config.notebooks:
        # check project has notebooks folder
        validate_folder(dir, "notebooks", typer)
        for notebook in config.notebooks:
            validate_item(dir, "notebooks", notebook, "notebook", typer, "main.ipynb")
    # check apis
    if config.apis:
        # check project has apis folder
        validate_folder(dir, "apis", typer)
        for api in config.apis:
            validate_item(dir, "apis", api, "api", typer)
    # check uis
    if config.uis:
        # check project has uis folder
        validate_folder(dir, "uis", typer)
        for ui in config.uis:
            validate_item(dir, "uis", ui, "ui", typer)
    return config
