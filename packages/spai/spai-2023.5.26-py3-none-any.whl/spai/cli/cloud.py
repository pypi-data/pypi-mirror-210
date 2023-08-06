import os
import requests


def deploy_and_run_cloud(dir, config, typer):
    # TODO: check if project exists and confirm to overwrite
    # send to api
    typer.echo(f"Deploying...")
    if "agents" in config:
        typer.echo(f"Deploying agents...")
        for agent in config["agents"]:
            typer.echo(f"Deploying agent '{agent['name']}'...")
            agent_dir = dir / "agents" / agent["name"]
            has_requirements = "requirements.txt" in os.listdir(agent_dir)
            has_env = ".env" in os.listdir(agent_dir)
            response = requests.post(
                "http://localhost:8000/deploy/agent",
                files={
                    "agent": open(agent_dir / "main.py", "rb"),
                    "requirements": open(agent_dir / "requirements.txt", "rb")
                    if has_requirements
                    else None,
                    "env": open(agent_dir / ".env", "rb") if has_env else None,
                },
                data={
                    "name": agent["name"],
                },
            )
            if response.status_code == 200:
                typer.echo("Agent deployed successfully!")
            else:
                typer.echo("Something went wrong.")
                typer.echo(response.json()["detail"])
