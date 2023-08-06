from rich import print

print("[bold red]Alert![/bold red] [green]Portal gun[/green] shooting! :boom:")

# from rich.table import Table
#
# table = Table("Name", "Item")
# table.add_row("Rick", "Portal Gun")
# table.add_row("Morty", "Plumbus")
# print(table)

# from rich import print
# from rich.panel import Panel
# print(Panel("Hello, [red]World!"))


# from rich.console import Console
# console = Console()
#
# try:
#    do_something()
# except Exception:
#    console.print_exception(show_locals=True)

# from rich.prompt import Confirm
# is_rich_great = Confirm.ask("Do you like rich?")
# assert is_rich_great

# import os
# import sys
#
# from rich import print
# from rich.columns import Columns
#
# if len(sys.argv) < 2:
#    print("Usage: python columns.py DIRECTORY")
# else:
#    directory = os.listdir(sys.argv[1])
#    columns = Columns(directory, equal=True, expand=True)
#    print(columns)

# from rich import print
# from rich.console import Group
# from rich.panel import Panel
#
# panel_group = Group(
#    Panel("Hello", style="on blue"),
#    Panel("World", style="on red"),
# )
# print(Panel(panel_group))


# MARKDOWN = """
## This is an h1
#
# Rich can do a pretty *decent* job of rendering markdown.
#
# 1. This is a list item
# 2. This is another list item
# """
# from rich.console import Console
# from rich.markdown import Markdown
#
# console = Console()
# md = Markdown(MARKDOWN)
# console.print(md)


# from rich import print
# from rich.padding import Padding
# test = Padding("Hello", (2, 4))
# print(test)

import time
from rich.progress import track

for i in track(range(20), description="Processing..."):
    time.sleep(1)  # Simulate work being done

from rich.tree import Tree
from rich import print

tree = Tree("Rich Tree")
tree.add("foo")
tree.add("bar")
print(tree)

# import time
#
# from rich.live import Live
# from rich.table import Table
#
# table = Table()
# table.add_column("Row ID")
# table.add_column("Description")
# table.add_column("Level")
#
# with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
#    for row in range(12):
#        time.sleep(0.4)  # arbitrary delay
#        # update the renderable internally
#        table.add_row(f"{row}", f"description {row}", "[red]ERROR")

# from rich import print
# from rich.layout import Layout
#
# layout = Layout()
# layout.split_column(
#    Layout(name="upper"),
#    Layout(name="lower")
# )
# layout["lower"].split_row(
#    Layout(name="left"),
#    Layout(name="right"),
# )
# print(layout)
