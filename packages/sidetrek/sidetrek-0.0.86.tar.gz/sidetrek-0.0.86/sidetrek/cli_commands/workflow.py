import os
import sys
import time
import threading
from pathlib import Path
import typer
import subprocess
from time import sleep
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from sidetrek.cli_commands.helpers import (
    get_current_user,
    get_generated_local_sidetrek_dir_path,
    get_generated_workflow_name,
    download_generated_flyte_workflow,
    get_workflow_draft_version,
    print_timer,
)

app = typer.Typer()


@app.command()
def run(workflow_id: int = typer.Option(...), workflow_args: str = "{}"):
    """
    Execute the workflow locally (e.g. for testing).

    * You can retrieve the --workflow-id (e.g. 42) from Sidetrek app.
    * Workflow version used it always `draft` for this command
    * --workflow-args is a stringified JSON of your workflow arguments (e.g. '{"learning_rate"=0.1, "epochs"=5}').
    """
    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        print("generated_local_sidetrek_dir_path", get_generated_local_sidetrek_dir_path())

        # # Add a timer
        # print_timer()

        # Get current user
        auth_step = progress.add_task(description="Authenticating...", total=None)
        current_user = get_current_user()
        progress.remove_task(auth_step)
        time_elapsed = round(time.time() - start_time, 2)
        print(f"[green]✔️ [white]Authenticated [grey89]({time_elapsed}s)")

        # # Allow access to the s3 bucket
        # print(f"current_user={current_user}")
        # ipconfig = os.system('ipconfig')

        # Always use the draft version for testing
        wf_generation_step = progress.add_task(description="Generating the workflow...", total=None)
        workflow_version = get_workflow_draft_version(workflow_id=workflow_id)
        # print(f"workflow_version={workflow_version}")

        # Generate the workflow file
        wf_file_path = download_generated_flyte_workflow(user_id=current_user["id"], workflow_version=workflow_version)
        generated_wf_name = get_generated_workflow_name(workflow_id)
        progress.remove_task(wf_generation_step)
        time_elapsed = round(time.time() - start_time, 2)
        print(f"[green]✔️ [white]Workflow generated [grey89]({time_elapsed}s) - generated workflow: {wf_file_path.as_posix()}")

        wf_execution_step = progress.add_task(description="Executing the workflow...", total=None)
        # print(" ".join(["pyflyte", "run", wf_file_path.as_posix(), generated_wf_name, "--_wf_args", workflow_args]))
        with subprocess.Popen(
            ["pyflyte", "run", wf_file_path, generated_wf_name, "--_wf_args", workflow_args],
            cwd=get_generated_local_sidetrek_dir_path(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            for line in process.stdout:
                print(line, end="")

            _, error = process.communicate()

            if process.returncode != 0:
                time_elapsed = round(time.time() - start_time, 2)
                print(f"[light_coral]{error}")
                print(f"[red]✕ [white]Workflow execution failed [grey89]({time_elapsed}s)")
                raise typer.Exit()

            progress.remove_task(wf_execution_step)
            time_elapsed = round(time.time() - start_time, 2)
            print(f"[green]✔️ [white]Workflow execution completed 🎉 [grey89]({time_elapsed}s)")
