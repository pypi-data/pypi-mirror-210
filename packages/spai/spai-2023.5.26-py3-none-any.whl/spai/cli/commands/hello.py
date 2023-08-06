import typer

app = typer.Typer()


@app.command()
def hello(name: str = 'World!'):
    """Say hello to someone"""
    typer.echo(f"hello, {name}")

@app.command()
def goodbye(name: str = 'World!'):
    """Say goodbye to someone"""
    typer.echo(f"goodbye, {name}")