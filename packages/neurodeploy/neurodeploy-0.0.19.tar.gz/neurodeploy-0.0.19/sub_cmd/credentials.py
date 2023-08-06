#!/usr/bin/python
from typing import Optional
import typer
from rich import print

from neurodeploy import credentials

credentials_app = typer.Typer()


@credentials_app.command("create")
def credentials_create(
    name: str = typer.Option(..., help="Your credential name"),
    description=typer.Option(..., help="Your credentials description message"),
):
    """
    #credentials create
    """
    resp = credentials.create(name, description)
    print(resp)


@credentials_app.command("list")
def credentials_list():
    """
    #credentials delete
    """
    resp = credentials.get()
    print(resp)


@credentials_app.command("delete")
def credentials_delete(name: str = typer.Option(..., help="Your credential name")):
    """
    #credentials delete
    """
    resp = credentials.delete(name)
    print(resp)
