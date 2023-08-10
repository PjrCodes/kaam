import argparse
import utils.command_functions as cf
from datetime import datetime
from utils import validators


class Parser:
    def __init__(self, version: str = "unspecified"):
        self.parser = argparse.ArgumentParser(
            prog="kaam",
            description="A simple manager for tasks.",
            epilog="Thanks for using kaam!",
        )
        self.version = version

    def setup(self):
        self.parser.add_argument(
            "-v",
            "--verbosity",
            action="count",
            help="Increase verbosity of the output.",
        )
        subparsers = self.parser.add_subparsers(
            title="subcommands", description="Valid subcommands"
        )
        self.parser.add_argument(
            "--version", action="version", version=f"%(prog)s {self.version}"
        )

        parser_add = subparsers.add_parser("add", help="Add a task to the list.")
        parser_add.add_argument("name", help="Name of the task.")
        parser_add.add_argument(
            "-p",
            "--priority",
            help="Priority of the task. Higher numbers are higher priority.",
            type=int,
            choices=range(1, 6),
            default=5,
        )
        parser_add.add_argument(
            "-d",
            "--due",
            help="Due date of the task, in ISO format: YYYY-MM-DD:HH:mm:ss",
            type=datetime.fromisoformat,
        )
        parser_add.set_defaults(func=cf.add_to_tasks)

        parser_remove = subparsers.add_parser(
            "remove", help="Remove a task from the list."
        )
        parser_remove.add_argument(
            "id", help="Task ID to remove", type=validators.valid_id
        )
        parser_remove.set_defaults(func=cf.remove_from_tasks)

        parser_list = subparsers.add_parser("list", help="List all tasks.")
        parser_list.add_argument(
            "-s",
            "--sort",
            help="Sort tasks by a field.",
            choices=["name", "priority", "due"],
            default="name",
        )
        parser_list.set_defaults(func=cf.list_tasks)

        parser_done = subparsers.add_parser(
            "done", aliases=["do", "complete"], help="Mark a task as done."
        )
        parser_done.add_argument(
            "id", help="Task ID to mark as done.", type=validators.valid_id
        )
        parser_done.set_defaults(func=cf.done_task)

        parser_undone = subparsers.add_parser(
            "undone", aliases=["undo", "finish"], help="Mark a task as undone."
        )
        parser_undone.add_argument(
            "id", help="Task ID to mark as undone.", type=validators.valid_id
        )
        parser_undone.set_defaults(func=cf.undone_task)

        parser_edit = subparsers.add_parser("edit", help="Edit a task.")
        parser_edit.add_argument(
            "id", help="Task ID to edit.", type=validators.valid_id
        )
        parser_edit.add_argument("name", help="New name of the task.")
        parser_edit.add_argument(
            "-p",
            "--priority",
            help="New priority of the task.",
            type=int,
            choices=range(1, 6),
        )
        parser_edit.add_argument(
            "-d", "--due", help="New due date of the task.", type=datetime.fromisoformat
        )
        parser_edit.set_defaults(func=cf.edit_task)

        parser_move = subparsers.add_parser("move", help="Move a task in the list.")
        parser_move.add_argument(
            "ID", help="Task ID to move.", type=validators.valid_id
        )
        parser_move.add_argument("position", help="New position of the task.", type=int)
        parser_move.add_argument(
            "-s",
            "--swap",
            help="Swap the task with the task at the given position.",
            action="store_true",
        )
        parser_move.set_defaults(func=cf.move_task)

        parser_clean = subparsers.add_parser("clean", help="Remove all done tasks.")
        parser_clean.set_defaults(func=cf.clean_tasks)

    def get_args(self) -> argparse.Namespace:
        args = self.parser.parse_args()
        return args
    