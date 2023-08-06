"""Render Change Logs
"""

from typing import List
import os

import jinja2

from gitaudit.git.change_log_entry import ChangeLogEntry, FileAdditionsDeletions


def calculate_total_additions(numstat: List[FileAdditionsDeletions]):
    """
    Calculate the total number of additions for a given list of file additions and deletions.

    Args:
        numstat (List[FileAdditionsDeletions]): A list of objects containing the additions and
            deletions for each file.

    Returns:
        int: The total number of additions across all files.
    """
    return sum(item.additions for item in numstat)


def calculate_total_deletions(numstat: List[FileAdditionsDeletions]):
    """
    Calculate the total number of deletions for a given list of file additions and deletions.

    Args:
        numstat (List[FileAdditionsDeletions]): A list of objects containing the additions and
            deletions for each file.

    Returns:
        int: The total number of deletions across all files.
    """
    return sum(item.deletions for item in numstat)


def render_change_log_to_text(entries: List[ChangeLogEntry]) -> str:
    """Renders the change log entries as a formatted text using a Jinja2 template.

    Args:
        entries (List[ChangeLogEntry]): A list of ChangeLogEntry objects to be included in the
            rendered text.

    Returns:
        str: A string containing the rendered change log entries as formatted text.
    """
    template_root = os.path.join(
        os.path.dirname(__file__), 'templates')

    template_loader = jinja2.FileSystemLoader(searchpath=template_root)
    template_env = jinja2.Environment(loader=template_loader)
    template_env.globals['calculate_total_additions'] = calculate_total_additions
    template_env.globals['calculate_total_deletions'] = calculate_total_deletions
    template = template_env.get_template("change_log.html")
    return template.render(change_log_entries=entries)


def render_change_to_to_file(entries: List[ChangeLogEntry], file_path: str):
    """Renders the change log entries as a formatted text using a Jinja2 template and saves the
        result to a file.

    Args:
        entries (List[ChangeLogEntry]): A list of ChangeLogEntry objects to be included in the
            rendered text.
        file_path (str): The path to the file where the rendered text will be saved.

    Returns:
        None
    """
    with open(file_path, 'w', encoding='utf-8') as file_p:
        file_p.write(render_change_log_to_text(entries))
