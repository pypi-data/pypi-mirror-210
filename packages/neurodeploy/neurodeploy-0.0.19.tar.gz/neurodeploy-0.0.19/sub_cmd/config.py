#!/usr/bin/python
from typing import Optional
import typer

import process.nd_config as config
import process.nd_credentials as nd_credentials
import neurodeploy
import rich


config_app = typer.Typer()


@config_app.callback()
def config_callback():
    print("Save cli config")


@config_app.command()
def update(
    username: str = typer.Option(
        ..., prompt="Enter your username", help="user username created with ui"
    ),
    password: str = typer.Option(
        ...,
        prompt="Enter your password",
        help="user password created with ui",
        confirmation_prompt=True,
        hide_input=False,
    ),
    credential_name: str = typer.Option(
        ..., prompt="Enter your crdential name", help="user credential name"
    ),
):
    config.save_config(username)
    neurodeploy.user.login(username, password)
    resp = neurodeploy.credentials.create(credential_name, "credential_of_" + username)
    if "message" in resp:
        print(resp)
        return 0
    resps = nd_credentials.save_credentials(resp)
    print("[bold red]Your confguration saved[/bold red]")
    print("[green]To start use : cli --help[/green] ")
