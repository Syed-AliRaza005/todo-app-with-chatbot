"""
Console Todo Application - Interactive REPL Mode

This module provides an interactive REPL interface like Claude CLI.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.storage import load_collection, save_collection
from src.models import TodoError, ValidationError, TaskNotFoundError, StorageError
from src.ui import render_all_tasks, render_success, render_error, render_task_detail


console = Console()


class TodoREPL:
    """Interactive REPL for todo management."""

    def __init__(self):
        """Initialize the REPL."""
        self.running = True
        self.collection = None

    def run(self):
        """Main REPL loop."""
        self.display_banner()
        self.load_data()

        console.print("[dim]Type a command or 'help' for assistance. Type 'exit' to quit.[/dim]\n")

        while self.running:
            try:
                # Get command from user
                command_line = console.input("[bold cyan]todo>[/bold cyan] ").strip()

                if not command_line:
                    continue

                # Parse and execute command
                self.execute_command(command_line)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                render_error(f"Unexpected error: {e}")

        console.print("\n[bold cyan]👋 Goodbye! Your tasks are saved.[/bold cyan]\n")

    def display_banner(self):
        """Show application header."""
        banner = Panel.fit(
            "[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]\n"
            "[bold yellow]║   📋 Console Todo Application v1.0   ║[/bold yellow]\n"
            "[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n\n"
            "[green]✨ Manage your tasks with style! ✨[/green]",
            border_style="bold cyan",
            padding=(1, 2),
        )
        console.print("\n")
        console.print(banner)
        console.print("\n")

        # Show available commands
        help_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED,
            title="[bold cyan]Available Commands[/bold cyan]",
            title_style="bold cyan"
        )
        help_table.add_column("Command", style="yellow", width=25)
        help_table.add_column("Description", style="dim white")

        help_table.add_row("add", "Add task (interactive prompts)")
        help_table.add_row("list", "Show all tasks in single table")
        help_table.add_row("done", "Mark task completed (prompts for ID)")
        help_table.add_row("update", "Update task (shows current values)")
        help_table.add_row("delete", "Delete task (with confirmation)")
        help_table.add_row("clear", "Clear all tasks")
        help_table.add_row("help", "Show detailed help")
        help_table.add_row("exit", "Exit the application")

        console.print(help_table)
        console.print()

    def load_data(self):
        """Load tasks from storage."""
        try:
            self.collection = load_collection()
            task_count = len(self.collection.tasks)
            if task_count > 0:
                console.print(f"[dim]📂 Loaded {task_count} task(s)[/dim]\n")
            else:
                console.print("[dim]📭 No tasks found. Start by adding one![/dim]\n")
        except StorageError as e:
            render_error(f"Failed to load tasks: {e}")
            self.collection = load_collection()  # Create empty

    def save_data(self):
        """Save tasks to storage."""
        try:
            save_collection(self.collection)
        except StorageError as e:
            render_error(f"Failed to save tasks: {e}")

    def execute_command(self, command_line: str):
        """Parse and execute a command."""
        parts = command_line.split(maxsplit=1)
        if not parts:
            return

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Route to appropriate handler
        if command == "exit" or command == "quit":
            self.running = False
        elif command == "help":
            self.cmd_help()
        elif command == "list" or command == "ls":
            self.cmd_list()
        elif command == "add":
            self.cmd_add(args)
        elif command == "done":
            self.cmd_done(args)
        elif command == "update":
            self.cmd_update(args)
        elif command == "delete" or command == "del":
            self.cmd_delete(args)
        elif command == "clear":
            self.cmd_clear()
        else:
            render_error(f"Unknown command: {command}")
            console.print("[dim]Type 'help' to see available commands[/dim]")

    def cmd_help(self):
        """Show help message."""
        help_text = """
[bold cyan]📚 Available Commands:[/bold cyan]

  [yellow]add[/yellow]
    Add a new task (interactive prompts - no quotes needed!)
    [dim]Just type 'add' and answer: Title? Description?[/dim]
    [dim]Quick way: add "Buy groceries" "Milk, eggs, bread"[/dim]

  [yellow]list[/yellow] (or [yellow]ls[/yellow])
    Display all tasks in a single table with status column
    [dim]Shows Pending (yellow) and Completed (green) tasks[/dim]

  [yellow]done[/yellow]
    Mark a task as completed (interactive prompt)
    [dim]Just type 'done' and enter task ID when asked[/dim]
    [dim]Quick way: done 1[/dim]

  [yellow]update[/yellow]
    Update task title and description (shows current values!)
    [dim]Just type 'update' - will show current and ask for new[/dim]
    [dim]Quick way: update 1 "New title" "New description"[/dim]

  [yellow]delete[/yellow] (or [yellow]del[/yellow])
    Remove a task (shows task and confirms before deleting)
    [dim]Just type 'delete' - will show task and ask confirmation[/dim]
    [dim]Quick way: delete 1[/dim]

  [yellow]clear[/yellow]
    Delete all tasks and reset ID counter
    [dim]⚠️  Will ask for confirmation - this is permanent![/dim]

  [yellow]help[/yellow]
    Show this help message

  [yellow]exit[/yellow] (or [yellow]quit[/yellow])
    Exit the application (your tasks are auto-saved)

[bold green]💡 Pro Tip:[/bold green] [dim]Just type the command name for interactive prompts!
No need to remember arguments or use quotes.[/dim]
"""
        console.print(help_text)

    def cmd_list(self):
        """List all tasks."""
        try:
            render_all_tasks(self.collection)
        except Exception as e:
            render_error(f"Failed to list tasks: {e}")

    def cmd_add(self, args: str):
        """Add a new task with interactive prompts."""
        try:
            # If args provided, use them (backwards compatibility)
            if args.strip():
                parts = self.parse_quoted_args(args)
                if len(parts) >= 2:
                    title = parts[0]
                    description = parts[1]
                else:
                    render_error("Usage: add <title> <description>")
                    return
            else:
                # Interactive prompts
                console.print("[bold cyan]➕ Add New Task[/bold cyan]\n")

                title = console.input("  [yellow]Title:[/yellow] ").strip()
                if not title:
                    render_error("Title cannot be empty")
                    return

                description = console.input("  [yellow]Description:[/yellow] ").strip()
                if not description:
                    render_error("Description cannot be empty")
                    return

            # Add task
            self.collection = self.collection.add_task(title, description)
            self.save_data()

            # Get the newly added task
            new_task = self.collection.tasks[-1]

            # Render success
            console.print()
            render_success("Task added successfully!")
            render_task_detail(new_task)

        except ValidationError as e:
            render_error(str(e))
        except StorageError as e:
            render_error(str(e))
        except Exception as e:
            render_error(f"Failed to add task: {e}")

    def cmd_done(self, args: str):
        """Mark task as done with interactive prompt."""
        try:
            # If args provided, use them
            if args.strip():
                task_id = int(args.strip())
            else:
                # Interactive prompt
                console.print("[bold cyan]✓ Mark Task as Done[/bold cyan]\n")
                id_input = console.input("  [yellow]Task ID:[/yellow] ").strip()
                if not id_input:
                    render_error("Task ID is required")
                    return
                task_id = int(id_input)

            # Mark done
            self.collection = self.collection.mark_done(task_id)
            self.save_data()

            # Get updated task
            updated_task = self.collection.get_task(task_id)

            # Render success
            console.print()
            render_success(f"Task #{task_id} marked as completed!")
            if updated_task:
                render_task_detail(updated_task)

        except ValueError:
            render_error("Invalid task ID. Please provide a number.")
        except TaskNotFoundError as e:
            render_error(str(e))
        except StorageError as e:
            render_error(str(e))
        except Exception as e:
            render_error(f"Failed to mark task as done: {e}")

    def cmd_update(self, args: str):
        """Update a task with interactive prompts."""
        try:
            # If args provided, use them
            if args.strip():
                parts = args.split(maxsplit=1)
                if len(parts) < 2:
                    render_error("Usage: update <id> <title> <description>")
                    return

                task_id = int(parts[0])
                remaining = parts[1]

                # Parse quoted title and description
                quoted_parts = self.parse_quoted_args(remaining)
                if len(quoted_parts) < 2:
                    render_error("Please provide both title and description")
                    return

                title = quoted_parts[0]
                description = quoted_parts[1]
            else:
                # Interactive prompts
                console.print("[bold cyan]✏️  Update Task[/bold cyan]\n")

                id_input = console.input("  [yellow]Task ID:[/yellow] ").strip()
                if not id_input:
                    render_error("Task ID is required")
                    return
                task_id = int(id_input)

                # Show current task first
                current_task = self.collection.get_task(task_id)
                if current_task:
                    console.print(f"\n  [dim]Current:[/dim]")
                    console.print(f"  [dim]Title: {current_task.title}[/dim]")
                    console.print(f"  [dim]Description: {current_task.description}[/dim]\n")

                title = console.input("  [yellow]New Title:[/yellow] ").strip()
                if not title:
                    render_error("Title cannot be empty")
                    return

                description = console.input("  [yellow]New Description:[/yellow] ").strip()
                if not description:
                    render_error("Description cannot be empty")
                    return

            # Update task
            self.collection = self.collection.update_task(task_id, title, description)
            self.save_data()

            # Get updated task
            updated_task = self.collection.get_task(task_id)

            # Render success
            console.print()
            render_success(f"Task #{task_id} updated successfully!")
            if updated_task:
                render_task_detail(updated_task)

        except ValueError:
            render_error("Invalid task ID. Please provide a number.")
        except TaskNotFoundError as e:
            render_error(str(e))
        except ValidationError as e:
            render_error(str(e))
        except StorageError as e:
            render_error(str(e))
        except Exception as e:
            render_error(f"Failed to update task: {e}")

    def cmd_delete(self, args: str):
        """Delete a task with interactive prompt."""
        try:
            # If args provided, use them
            if args.strip():
                task_id = int(args.strip())
            else:
                # Interactive prompt with warning
                console.print("\n[bold red]⚠️  DELETE TASK ⚠️[/bold red]")
                console.print("[red]═══════════════════════════[/red]\n")
                id_input = console.input("  [yellow]Task ID to delete:[/yellow] ").strip()
                if not id_input:
                    render_error("Task ID is required")
                    return
                task_id = int(id_input)

            # Get task before deleting
            task_to_delete = self.collection.get_task(task_id)

            # Show task and confirm with prominent warning
            if task_to_delete:
                console.print(f"\n[bold yellow]  📋 Task to be deleted:[/bold yellow]")
                console.print(f"  [white]Title: {task_to_delete.title}[/white]")
                console.print(f"  [white]Description: {task_to_delete.description}[/white]")
                console.print(f"  [red]Status: {task_to_delete.status}[/red]\n")

                console.print("[bold red]⚠️  This action cannot be undone![/bold red]")
                confirm = console.input("  [bold yellow]Type 'yes' to confirm deletion:[/bold yellow] ").strip().lower()
                if confirm not in ['yes', 'y']:
                    console.print("[dim]✓ Cancelled - task not deleted[/dim]")
                    return

            # Delete task
            self.collection = self.collection.delete_task(task_id)
            self.save_data()

            # Render success
            console.print()
            if task_to_delete:
                render_success(f"Task #{task_id} deleted successfully!")
                console.print(f"  [dim]Deleted: \"{task_to_delete.title}\"[/dim]")
                console.print(f"  [dim]Note: Other task IDs remain unchanged[/dim]")
            else:
                render_success(f"Task #{task_id} deleted!")

        except ValueError:
            render_error("Invalid task ID. Please provide a number.")
        except TaskNotFoundError as e:
            render_error(str(e))
        except StorageError as e:
            render_error(str(e))
        except Exception as e:
            render_error(f"Failed to delete task: {e}")

    def cmd_clear(self):
        """Clear all tasks with strong warning."""
        try:
            # Count tasks first
            task_count = len(self.collection.tasks)

            if task_count == 0:
                console.print("[dim]No tasks to clear[/dim]")
                return

            # Show dramatic warning
            console.print("\n[bold red on white]  ⚠️  DANGER ZONE ⚠️  [/bold red on white]")
            console.print("[red]═══════════════════════════════════════[/red]")
            console.print(f"[bold yellow]  You are about to delete ALL {task_count} task(s)![/bold yellow]")
            console.print("[bold red]  This will PERMANENTLY erase:[/bold red]")
            console.print("[red]  • All task data[/red]")
            console.print("[red]  • All task history[/red]")
            console.print("[red]  • Reset ID counter to 1[/red]")
            console.print("[red]═══════════════════════════════════════[/red]\n")

            console.print("[bold red]⚠️  THIS CANNOT BE UNDONE! ⚠️[/bold red]\n")

            # First confirmation
            response1 = console.input("[bold yellow]Type 'DELETE' (all caps) to continue: [/bold yellow]").strip()

            if response1 != 'DELETE':
                console.print("[green]✓ Safe! No tasks were deleted.[/green]")
                return

            # Second confirmation
            console.print(f"\n[bold red]Last chance! Really delete {task_count} task(s)?[/bold red]")
            response2 = console.input("[bold yellow]Type 'yes' to confirm: [/bold yellow]").strip().lower()

            if response2 not in ['yes', 'y']:
                console.print("[green]✓ Safe! No tasks were deleted.[/green]")
                return

            # Create empty collection
            self.collection = self.collection.clear()
            self.save_data()

            # Render success with warning color
            console.print("\n[bold red]💥 ALL TASKS CLEARED! 💥[/bold red]")
            console.print(f"  [dim]Deleted: {task_count} task(s)[/dim]")
            console.print(f"  [dim]ID counter reset to 1[/dim]")
            console.print(f"  [yellow]Start fresh with 'add' command[/yellow]\n")

        except StorageError as e:
            render_error(str(e))
        except Exception as e:
            render_error(f"Failed to clear tasks: {e}")

    def parse_quoted_args(self, text: str) -> list:
        """Parse quoted arguments from command line."""
        import shlex
        try:
            return shlex.split(text)
        except ValueError:
            # If shlex fails, try simple split
            return text.split()


def main():
    """Entry point for interactive REPL."""
    repl = TodoREPL()
    try:
        repl.run()
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Goodbye![/bold cyan]\n")
        sys.exit(0)


if __name__ == '__main__':
    main()
