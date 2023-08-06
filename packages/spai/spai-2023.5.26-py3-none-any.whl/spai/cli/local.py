import os
from dotenv import load_dotenv
import subprocess
import schedule
import time
from multiprocessing import Process


def run_item(item, command):
    if item.command:
        os.system(item.command)
    else:
        os.system(command)


def run_script(args):
    script, dir, typer = args
    typer.echo(f"Running script '{script.name}'...")
    os.chdir(dir)  # change to project dir
    run_item(script, f"python scripts/{script.name}/main.py")


def run_notebook(args):
    notebook, dir, typer = args
    typer.echo(f"Running notebook '{notebook.name}'...")
    os.chdir(dir / "notebooks" / notebook.name)  # necessary ???
    run_item(
        notebook,
        f"papermill main.ipynb output.ipynb",
    )
    # papermill can execute notebooks and save output in S3
    # papermill can execute notebooks with params


def run_api(api, dir):
    os.chdir(dir)
    os.system(f"python apis/{api.name}/main.py")


def run_ui(ui, dir):
    os.chdir(dir)
    os.system(ui.command)


def run_schdule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_local(dir, config, typer):
    typer.echo(f"Deploying locally...")
    keep_alive = False
    processes = []
    if config.scripts:
        typer.echo(f"Deploying scripts...")
        for (
            script
        ) in (
            config.scripts
        ):  # the order affects in the execution of the scheduled tasks
            # # TODO: reqs, env
            if script.run_on_start:
                run_script((script, dir, typer))
            if script.run_every:
                keep_alive = True
                schedule.every(script.run_every).seconds.do(
                    run_script, (script, dir, typer)
                )  # if a task goes after another than takes more time than the scheduled time, it will have to wait
    if config.notebooks:
        typer.echo(f"Deploying notebooks...")
        for notebook in config.notebooks:
            # TODO: reqs, env
            if notebook.run_on_start:
                run_notebook((notebook, dir, typer))
            if notebook.run_every:
                keep_alive = True
                schedule.every(notebook.run_every).seconds.do(
                    run_notebook, (notebook, dir, typer)
                )
    if config.apis:
        typer.echo(f"Deploying apis...")
        for api in config.apis:
            typer.echo(f"Running api '{api.name}'...")
            # TODO: reqs, env
            # load_dotenv(f"{dir}/apis/{api.name}/.env")
            p = Process(target=run_api, args=(api, dir))
            p.start()
            processes.append(p)
    if config.uis:
        typer.echo(f"Deploying uis...")
        for ui in config.uis:
            typer.echo(f"Running ui '{ui.name}'...")
            # TODO: reqs, env
            # load_dotenv(f"{dir}/apis/{api.name}/.env")
            p = Process(target=run_ui, args=(ui, dir))
            p.start()
            processes.append(p)
    typer.echo(f"Project '{config.project}' deployed.")
    if keep_alive:
        p = Process(target=run_schdule)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return
