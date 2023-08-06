import json
import importlib
from pathlib import Path
import pickle
import requests
import typer
from typing import Optional
from typing_extensions import Annotated
from rich import print
from sidetrek.cli_commands import workflow
from sidetrek.cli_commands.constants import APP_NAME
from sidetrek.cli_commands.helpers import get_node_env, get_auth_api_base_url, version_callback


app = typer.Typer()

app.add_typer(workflow.app, name="workflow")

if get_node_env() != "production":
    print(f"Environment: {get_node_env()}\n")


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
):
    pass


@app.command()
def login(email: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    # Login and get refresh/access tokens
    try:
        auth_api_base_url = get_auth_api_base_url()
        login_payload = json.dumps({"username": email, "password": password})
        login_res = requests.post(f"{auth_api_base_url}/auth/login", data=login_payload, headers={"content-type": "application/json"})
        login_res.raise_for_status()
        login_res_data = login_res.json()

        # Save the cookies in a local file
        app_dir = typer.get_app_dir(APP_NAME)
        cred_path: Path = Path(app_dir) / ".credentials"
        Path(app_dir).mkdir(parents=True, exist_ok=True)
        with open(cred_path, "w") as f:
            json.dump({"refresh_token": login_res_data["refreshToken"]}, f)

        print("[bold green]Login successful! 👍")
    except requests.exceptions.HTTPError as errh:
        print(f"[red]{errh.response.status_code} {errh.response.text}")
        raise typer.Exit()
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)
        raise typer.Exit()
