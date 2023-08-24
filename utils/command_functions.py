import argparse
from .wrappers.database import Database
from rich.console import Console
from rich.table import Table
from datetime import datetime
from rich import box
from dateutil import parser
from . import validators


def add_to_tasks(args: argparse.Namespace):
    db = Database()
    parsed_date = validators.valid_date(args.due)
    db.add_task(" ".join(args.name), args.priority, parsed_date)


def remove_from_tasks(args: argparse.Namespace):
    db = Database()
    db.remove_task(args.id)


def list_tasks(args: argparse.Namespace):
    db = Database()
    # print the tasks sorted by args.sort
    tasks = db.get_tasks()
    if args.sort == "name":
        tasks.sort(key=lambda task: task.name)
    elif args.sort == "priority":
        tasks.sort(key=lambda task: task.priority, reverse=True)
    elif args.sort == "due":
        tasks.sort(key=lambda task: task.due)

    rtable = Table(
        title="Tasks",
        caption=datetime.now().strftime("%d %B %Y %H:%M"),
        box=box.ROUNDED,
        min_width=100,
        title_style="bold magenta",
    )

    rtable.add_column("ID", justify="right", style="cyan", no_wrap=True)
    rtable.add_column("Task Name", style="magenta")
    rtable.add_column("Priority", justify="right", style="green")
    rtable.add_column("Due By", style="bold cyan")
    rtable.add_column("Done", justify="right", style="magenta italic bold")

    for task in tasks:
        rtable.add_row(
            str(task.id),
            task.name,
            str(task.priority),
            task.due.strftime("%d %b %Y %H:%M hrs") if task.due else "None",
            f"[green]{task.done}[/]" if task.done else f"{task.done}",
        )

    console = Console()
    print()
    console.print(rtable, justify="center")
    print()


def done_task(args: argparse.Namespace):
    db = Database()
    db.mark_task_as_done(args.id)


def undone_task(args: argparse.Namespace):
    db = Database()
    db.mark_task_as_undone(args.id)


def edit_task(args: argparse.Namespace):
    db = Database()
    db.edit_task(args.id, " ".join(args.name), args.priority, args.due)


def clean_tasks(args: argparse.Namespace):
    db = Database()
    db.clean_tasks()
