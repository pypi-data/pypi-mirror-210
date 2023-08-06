#!/usr/bin/python
from typing import Optional
import typer
from rich import print

from neurodeploy import apikeys


apikeys_app = typer.Typer()


@apikeys_app.command("create")
def apikeys_create(
    model_name: str = typer.Option(
        "None", help="Your api key model name to be attached to"
    ),
    description: str = typer.Option(..., help="Your api key description message"),
    expires_after: str = typer.Option("", help="Your api key expiration on minutes"),
):
    """
    #apikeys create
    """
    resp = apikeys.create(description, model_name, expires_after)
    print(resp)


@apikeys_app.command("list")
def apikeys_list():
    """
    #credentials delete
    """
    resp = apikeys.get()
    print(resp)


@apikeys_app.command("delete")
def apikeys_delete(apikey: str = typer.Option(..., help="Your api key name")):
    """
    #apikeys delete
    """
    resp = apikeys.delete(apikey)
    print(resp)
