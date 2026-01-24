"""
Console Todo Application - CLI Entry Point

This module provides the command-line interface with argparse routing.
"""

import argparse
import sys
from typing import Optional

from src.commands import cmd_add, cmd_list, cmd_done, cmd_update, cmd_delete, cmd_clear
from src.ui import render_error


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure ArgumentParser with all subcommands.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='todo',
        description='Console Todo Application - Manage your tasks with style',
        epilog='Examples:\n'
               '  %(prog)s add "Buy groceries" "Milk, eggs, bread"\n'
               '  %(prog)s list\n'
               '  %(prog)s done 1\n'
               '  %(prog)s update 1 "Buy groceries" "Milk, eggs, bread, butter"\n'
               '  %(prog)s delete 1\n'
               '  %(prog)s clear',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Command: add
    parser_add = subparsers.add_parser(
        'add',
        help='Add a new task',
        description='Create a new task with automatic ID and timestamp'
    )
    parser_add.add_argument('title', type=str, help='Task title')
    parser_add.add_argument('description', type=str, help='Task description')

    # Command: list
    subparsers.add_parser(
        'list',
        help='List all tasks',
        description='Display tasks in color-coded categorized tables'
    )

    # Command: done
    parser_done = subparsers.add_parser(
        'done',
        help='Mark a task as completed',
        description='Change task status from Pending to Completed'
    )
    parser_done.add_argument('task_id', type=int, help='ID of task to mark done')

    # Command: update
    parser_update = subparsers.add_parser(
        'update',
        help='Update task title and description',
        description='Modify task details (ID, status, and timestamp remain unchanged)'
    )
    parser_update.add_argument('task_id', type=int, help='ID of task to update')
    parser_update.add_argument('title', type=str, help='New task title')
    parser_update.add_argument('description', type=str, help='New task description')

    # Command: delete
    parser_delete = subparsers.add_parser(
        'delete',
        help='Delete a task',
        description='Remove task while preserving other task IDs'
    )
    parser_delete.add_argument('task_id', type=int, help='ID of task to delete')

    # Command: clear
    subparsers.add_parser(
        'clear',
        help='Clear all tasks',
        description='Delete all tasks and reset ID counter to 1'
    )

    return parser


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point with command routing and exception handling.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0=success, 1=user error, 2=system error)
    """
    parser = create_parser()

    # Parse arguments
    args = parser.parse_args(argv)

    # Handle no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command
    try:
        if args.command == 'add':
            cmd_add(args.title, args.description)
        elif args.command == 'list':
            cmd_list()
        elif args.command == 'done':
            cmd_done(args.task_id)
        elif args.command == 'update':
            cmd_update(args.task_id, args.title, args.description)
        elif args.command == 'delete':
            cmd_delete(args.task_id)
        elif args.command == 'clear':
            cmd_clear()
        else:
            render_error(f"Unknown command: {args.command}")
            return 1

        return 0

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n")
        render_error("Operation cancelled by user")
        return 130  # Standard Unix exit code for SIGINT

    except Exception as e:
        # Catch any unexpected errors
        render_error(f"Unexpected error: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
