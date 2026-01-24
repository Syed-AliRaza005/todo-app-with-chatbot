"""
Console Todo Application - UI Layer

This module handles Rich library rendering with color-coded tables.
"""

from typing import List
from rich.console import Console
from rich.table import Table
from rich import box

from src.models import Task, TaskCollection, TaskStatus


# Console instance for all output
console = Console()


# Color constants matching constitution (T017)
COLORS = {
    'pending': 'yellow',
    'completed': 'green',
    'header': 'bold cyan',
    'id': 'magenta',
    'timestamp': 'dim white',
    'success': 'green',
    'error': 'red bold'
}


# ============================================================================
# Table Rendering (T018)
# ============================================================================

def render_tasks_table(tasks: List[Task], title: str) -> None:
    """
    Renders a single categorized table with Rich styling.

    Args:
        tasks: List of tasks to display
        title: Section title (e.g., "All Tasks", "Pending", "Completed")
    """
    # Handle empty list
    if not tasks:
        return

    # Create table with styling and row separators
    table = Table(
        title=f"[{COLORS['header']}]{title}[/]",
        box=box.HEAVY,
        show_header=True,
        header_style=COLORS['header'],
        show_lines=True  # Add line between each row for better separation
    )

    # Add columns
    table.add_column("ID", justify="center", style=COLORS['id'], width=6)
    table.add_column("Title", justify="left", width=30)
    table.add_column("Description", justify="left", width=40)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Created", justify="center", style=COLORS['timestamp'], width=20)

    # Add rows with color coding
    for task in tasks:
        # Determine status color
        status_color = COLORS['completed'] if task.status == TaskStatus.COMPLETED.value else COLORS['pending']

        # Truncate long text
        title_display = task.title[:27] + "..." if len(task.title) > 30 else task.title
        desc_display = task.description[:37] + "..." if len(task.description) > 40 else task.description

        table.add_row(
            str(task.id),
            title_display,
            desc_display,
            f"[{status_color}]{task.status}[/]",
            task.created_at
        )

    # Print table
    console.print(table)
    console.print()  # Empty line after table


# ============================================================================
# Multi-Section Rendering (T019)
# ============================================================================

def render_all_tasks(collection: TaskCollection) -> None:
    """
    Displays all tasks in a single table with status column.

    Args:
        collection: TaskCollection to display
    """
    # Handle empty collection
    if not collection.tasks:
        console.print("[dim]📋 No tasks yet! Add your first task with the 'add' command[/dim]")
        return

    # Render single table with all tasks
    render_tasks_table(collection.tasks, "📋 All Tasks")


# ============================================================================
# Success/Error Messages (T020)
# ============================================================================

def render_success(message: str) -> None:
    """
    Displays success message in green.

    Args:
        message: Success message to display
    """
    console.print(f"[{COLORS['success']}]✓ {message}[/]")


def render_error(message: str) -> None:
    """
    Displays error message in red.

    Args:
        message: Error message to display
    """
    console.print(f"[{COLORS['error']}]✗ {message}[/]")


# ============================================================================
# Task Detail View (T021)
# ============================================================================

def render_task_detail(task: Task) -> None:
    """
    Displays single task in formatted view.

    Args:
        task: Task to display
    """
    # Determine status color
    status_color = COLORS['completed'] if task.status == TaskStatus.COMPLETED.value else COLORS['pending']

    console.print()
    console.print(f"  [{COLORS['header']}]ID:[/] [{COLORS['id']}]{task.id}[/]")
    console.print(f"  [{COLORS['header']}]Title:[/] {task.title}")
    console.print(f"  [{COLORS['header']}]Description:[/] {task.description}")
    console.print(f"  [{COLORS['header']}]Status:[/] [{status_color}]{task.status}[/]")
    console.print(f"  [{COLORS['header']}]Created:[/] [{COLORS['timestamp']}]{task.created_at}[/]")
    console.print()
