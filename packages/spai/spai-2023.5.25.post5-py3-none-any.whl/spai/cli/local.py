import os
from dotenv import load_dotenv
import subprocess
import json
from pathlib import Path
import psutil


def load_status(project=None):
    try:
        with open(Path.home() / ".spai/status.json", "r") as f:
            status = json.load(f)
        if project is None:
            return status
        return status[project] if project in status else {}
    except:
        return {}


def save_status(status, project):
    os.makedirs(Path.home() / ".spai", exist_ok=True)
    prev_status = load_status()
    if status == {}:
        del prev_status[project]
    else:
        prev_status[project] = status
    with open(Path.home() / ".spai/status.json", "w") as f:
        json.dump(prev_status, f)


def kill_process(status, name, typer):
    process_id = status[name]
    try:
        process = psutil.Process(process_id)
        if process.is_running():
            typer.echo(f"Item '{name}' is already running. Stopping it...")
            # You can also obtain additional information about the process if needed
            # print(f"Process name: {process.name()}")
            # print(f"Process CPU usage: {process.cpu_percent()}%")
            # print(f"Process memory usage: {process.memory_info().rss} bytes")
            subprocess.call(["kill", str(process_id)])
        else:
            # print("Process has terminated.")
            del status[name]
    except psutil.NoSuchProcess:  # process has terminated
        # print("No such process")
        del status[name]


def run_local(dir, config, typer):
    typer.echo(f"Running locally...")
    project = config["project"]
    status = load_status(project)
    if "scripts" in config:
        typer.echo(f"Running scripts...")
        for script in config["scripts"]:
            # check if script is already running
            if script["name"] in status:
                kill_process(status, script["name"], typer)
            typer.echo(f"Running script '{script['name']}'...")
            # TODO: reqs, env
            os.chdir(f"{dir}/scripts/{script['name']}")
            # os.system(f"python main.py")
            # status[script["name"]] = "hola"
            # TODO: run in background and store job ids so we can kill them
            process = subprocess.Popen(
                ["python", "main.py"], shell=False, stdout=open(f"output.txt", "w")
            )
            process_id = process.pid
            print(f"Background process ID: {process_id}")
            status[script["name"]] = process_id
            save_status(status, project)
    if "notebooks" in config:
        typer.echo(f"Running notebooks...")
        for notebook in config["notebooks"]:
            typer.echo(f"Running notebook '{notebook['name']}'...")
            # TODO: reqs, env
            # papermill can execute notebooks and save output in S3
            # papermill can execute notebooks with params
            os.chdir(f"{dir}/notebooks/{notebook['name']}")
            os.system(f"papermill main.ipynb output.ipynb")
    if "apis" in config:
        typer.echo(f"Running apis...")
        for api in config["apis"]:
            # check if api is already running
            if api["name"] in status:
                kill_process(status, api["name"], typer)
            typer.echo(f"Running api '{api['name']}'...")
            # TODO: reqs, env
            load_dotenv(f"{dir}/apis/{api['name']}/.env")
            # change directory to api folder
            os.chdir(f"{dir}/apis/{api['name']}")
            # os.system(f"uvicorn main:app --port {api['port']}")
            process = subprocess.Popen(
                ["python", "main.py"],  # for this to work need init in main with port
                shell=False,
                stdout=open("output.txt", "w"),
            )
            process_id = process.pid
            print(f"Background process ID: {process_id}")
            status[api["name"]] = process_id
            # TODO: run in background so we can run multiple apis
            # os.system(f"uvicorn main:app --port {api['port']}")
            save_status(status, project)
    return


def stop_local(typer, project=None):
    if project is None:
        # TODO: stop all projects
        return
    status = load_status(project)
    if status == {}:
        typer.echo(f"No items running for project '{project}'.")
        return
    typer.echo(f"Stopping local...")
    delete = []
    for item, pid in status.items():
        try:
            process = psutil.Process(pid)
            if process.is_running():
                typer.echo(f"Stoppping item '{item}'...")
                subprocess.call(["kill", str(pid)])
            else:
                print(f"Item '{item}' has terminated.")
        except psutil.NoSuchProcess:
            print(f"Item '{item}' has terminated.")
        delete.append(item)
    for item in delete:
        del status[item]
    save_status(status, project)


def list_local(typer, project=None):
    status = load_status()
    if status == {}:
        typer.echo(f"No items running.")
        return
    for project, items in status.items():
        typer.echo(f"Project '{project}':")
        for item, pid in items.items():
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    typer.echo(f"  Item '{item}' is running...")
                else:
                    print(f"  Item '{item}' has terminated.")
            except psutil.NoSuchProcess:
                print(f"  Item '{item}' has terminated.")
    return
