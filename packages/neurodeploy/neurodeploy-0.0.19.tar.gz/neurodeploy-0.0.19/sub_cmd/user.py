#!/usr/bin/python
from typing import Optional
import typer
from rich import print
import neurodeploy


user_app = typer.Typer()


@user_app.command("login")
def user_login(username: str = typer.Option(...), password: str = typer.Option(...)):
    """
    #user create
    """
    neurodeploy.user.login(username, password)
    print("[green]Token saved after login[/green] ")
