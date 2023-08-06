import typer
from pathlib import Path

from .cli.commands import hello
from .cli import (
    load_and_validate_config,
    deploy_and_run_cloud,
    run_local,
    stop_local,
    list_local,
)

app = typer.Typer()
app.add_typer(hello.app, name="hello")


@app.command()
def run(
    dir: Path = typer.Option(Path("."), "-d"),
    cloud: bool = typer.Option(False, "-c", "--cloud"),
):
    # make sure dir is absolute
    dir = Path(dir).resolve()
    # load and validate config
    config = load_and_validate_config(dir, typer, cloud)
    # print(config)
    # run project
    if cloud:
        return deploy_and_run_cloud(dir, config, typer)
    return run_local(dir, config, typer)


@app.command()
def list(
    project: str = typer.Option(None, "-p", "--project"),
):
    return list_local(typer, project)


@app.command()
def stop(
    project: str = typer.Option(None, "-p", "--project"),
):
    # TODO: get confirmation
    return stop_local(typer, project)


if __name__ == "__main__":
    app()
