import argparse

import utils.command_functions as cf
from utils import validators


class Parser:
    def __init__(self, version: str = "unspecified"):
        self.parser = argparse.ArgumentParser(
            prog="kaam",
            description="A simple manager for tasks.",
            epilog="Kaam karo yaar.",
        )
        self.version = version

    def setup(self):
        self.parser.add_argument(
            "-m", "--meta", help="Show metadata.", action="store_true"
        )
        self.parser.add_argument(
            "-v",
            "--verbosity",
            action="count",
            help="Increase verbosity of the output.",
        )
        self.parser.add_argument(
            "--version", action="version", version=f"%(prog)s {self.version}"
        )
        subparsers = self.parser.add_subparsers(
            title="subcommands", description="Valid subcommands"
        )

        parser_add = subparsers.add_parser(
            "add", help="Add a task to the list.", aliases=["a"]
        )
        parser_add.add_argument("name", help="Name of the task.", nargs="+")
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
            nargs="+",
        )
        parser_add.set_defaults(func=cf.add_to_tasks)

        parser_remove = subparsers.add_parser(
            "remove", help="Remove a task from the list.", aliases=["r", "rm"]
        )
        parser_remove.add_argument(
            "id", help="Task ID to remove", type=validators.valid_id, nargs="+"
        )
        parser_remove.set_defaults(func=cf.remove_from_tasks)

        parser_list = subparsers.add_parser(
            "list", help="List all tasks.", aliases=["ls", "l"]
        )
        parser_list.add_argument(
            "-s",
            "--sort",
            help="Sort tasks by a field.",
            choices=["name", "priority", "due", "created"],
            default="created",
        )
        parser_list.set_defaults(func=cf.list_tasks)

        parser_done = subparsers.add_parser(
            "done", aliases=["do", "complete", "d"], help="Mark a task as done."
        )
        parser_done.add_argument(
            "id",
            help="Task ID to mark as done.",
            type=validators.valid_id,
            nargs="+",
        )
        parser_done.set_defaults(func=cf.done_task)

        parser_undone = subparsers.add_parser(
            "undone",
            aliases=["undo", "finish", "udo", "u"],
            help="Mark a task as undone.",
        )
        parser_undone.add_argument(
            "id",
            help="Task ID to mark as undone.",
            type=validators.valid_id,
            nargs="+",
        )
        parser_undone.set_defaults(func=cf.undone_task)

        parser_edit = subparsers.add_parser(
            "edit", aliases=["e", "change"], help="Edit a task."
        )
        parser_edit.add_argument(
            "id", help="Task ID to edit.", type=validators.valid_id
        )
        group = parser_edit.add_mutually_exclusive_group(required=True)
        group.add_argument("-n", "--name", help="New name of the task.", nargs="+")
        group.add_argument(
            "-p",
            "--priority",
            help="New priority of the task.",
            type=int,
            choices=range(1, 6),
        )
        group.add_argument("-d", "--due", help="New due date of the task.", nargs="+")
        parser_edit.set_defaults(func=cf.edit_task)

        parser_clean = subparsers.add_parser(
            "clean", aliases=["clear", "cls", "clr", "c"], help="Remove all done tasks."
        )
        parser_clean.set_defaults(func=cf.clean_tasks)

        parser_category = subparsers.add_parser(
            "category", aliases=["cat"], help="Manage categories."
        )

        subparsers_category = parser_category.add_subparsers(
            title="subcommands", description="Valid subcommands"
        )

        parser_category_add = subparsers_category.add_parser(
            "add", aliases=["a"], help="Add a category."
        )
        parser_category_add.add_argument(
            "name", help="Name of the category.", nargs="+"
        )
        parser_category_add.set_defaults(func=cf.add_category)

        parser_category_remove = subparsers_category.add_parser(
            "remove", aliases=["r", "rm"], help="Remove a category."
        )
        parser_category_remove.add_argument(
            "name", help="Name of the category.", nargs="+"
        )
        parser_category_remove.set_defaults(func=cf.remove_category)

        parser_category_list = subparsers_category.add_parser(
            "list", aliases=["ls", "l"], help="List all categories."
        )
        parser_category_list.set_defaults(func=cf.list_categories)

        parser_category_edit = subparsers_category.add_parser(
            "edit", aliases=["e", "change"], help="Edit a category."
        )
        parser_category_edit.add_argument(
            "name", help="Name of the category to edit."
        )
        parser_category_edit.add_argument(
            "-n", "--newname", help="New name of the category.", nargs="+"
        )
        parser_category_edit.set_defaults(func=cf.edit_category)

        parser_category_aliases = subparsers_category.add_parser(
            "aliases", aliases=["alias", "al"], help="Manage aliases."
        )
        subparsers_category_aliases = parser_category_aliases.add_subparsers(
            title="subcommands", description="Valid subcommands"
        )
        categoryaliasadd = subparsers_category_aliases.add_parser(
            "add", aliases=["a"], help="Add an alias."
        )
        categoryaliasadd.add_argument(
            "name", help="Name of the category to add an alias to."
        )
        categoryaliasadd.add_argument(
            "alias", help="Alias to add to the category.", nargs="+"
        )
        categoryaliasadd.set_defaults(func=cf.add_category_alias)

        categoryrmadd = subparsers_category_aliases.add_parser(
            "remove", aliases=["r", "rm"], help="Remove an alias."
        )
        categoryrmadd.add_argument(
            "name", help="Name of the category to remove an alias from."
        )
        categoryrmadd.add_argument(
            "alias", help="Alias to remove from the category.", nargs="+"
        )
        categoryrmadd.set_defaults(func=cf.remove_category_alias)

        catlsadd = subparsers_category_aliases.add_parser(
            "list", aliases=["ls", "l"], help="List all aliases."
        )
        catlsadd.set_defaults(func=cf.list_category_aliases)

        self.parser.set_defaults(func=self.__print_help_wrapper)

    def __print_help_wrapper(self, args):
        self.parser.print_help()

    def get_args(self) -> argparse.Namespace:
        args = self.parser.parse_args()
        return args
