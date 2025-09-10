"""Simple console UI helpers for consistent presentation.

This module centralizes formatting concerns so the rest of the app can
focus on domain logic. Functions are intentionally lightweight and
dependency-free.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence
import os
import sys


def title(text: str) -> None:
    """Print a title with an underline matching its length."""
    print()
    print(text)
    print("=" * len(text))


def subtitle(text: str) -> None:
    """Print a subtitle with a dashed underline."""
    print(text)
    print("-" * len(text))


def info(text: str) -> None:
    """Print an informational message."""
    print(f"[i] {text}")


def success(text: str) -> None:
    """Print a success message."""
    print(f"[✓] {text}")


def warn(text: str) -> None:
    """Print a warning message."""
    print(f"[!] {text}")


def error(text: str) -> None:
    """Print an error message."""
    print(f"[x] {text}")


def menu(options: Sequence[str]) -> None:
    """Render a numeric menu for a sequence of options."""
    for idx, label in enumerate(options, start=1):
        print(f"{idx}. {label}")


def table(rows: Iterable[Sequence[str]], headers: Sequence[str] | None = None) -> None:
    """Render a simple monospaced table.

    Args:
        rows: Iterable of row sequences (strings recommended)
        headers: Optional sequence of header strings
    """
    rows_list: List[Sequence[str]] = list(rows)
    if headers is not None:
        rows_list.insert(0, headers)

    if not rows_list:
        return

    col_count = max(len(r) for r in rows_list)
    col_widths = [0] * col_count
    for r in rows_list:
        for i in range(col_count):
            cell = str(r[i]) if i < len(r) else ""
            col_widths[i] = max(col_widths[i], len(cell))

    def render_row(r: Sequence[str]) -> str:
        cells = [str(r[i]) if i < len(r) else "" for i in range(col_count)]
        padded = [cells[i].ljust(col_widths[i]) for i in range(col_count)]
        return " | ".join(padded)

    # Header
    start_idx = 0
    if headers is not None:
        print(render_row(headers))
        print("-+-".join("-" * w for w in col_widths))
        start_idx = 1

    # Data
    for r in rows_list[start_idx:]:
        print(render_row(r))


def wait_key(message: str = "Press any key to go back to the main menu...") -> None:
    """Pause until the user presses a key (Windows) or Enter (others)."""
    try:
        import msvcrt  # type: ignore

        print(message)
        msvcrt.getch()
    except Exception:
        input(message.replace("any key", "Enter"))
    clear_screen()


def clear_screen() -> None:
    """Clear the terminal screen in a cross-platform way."""
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            # Use ANSI escape codes as a fallback if 'clear' is unavailable
            if os.system("clear") != 0:
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.flush()
    except Exception:
        # Best-effort fallback: print many newlines
        print("\n" * 100)


