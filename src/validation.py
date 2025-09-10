"""Input validation helpers for console I/O."""

from __future__ import annotations

from typing import Optional


def prompt_int(prompt: str, *, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """Prompt for an integer within optional bounds, looping until valid."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Please enter a number.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Invalid number. Try again.")
            continue
        if min_value is not None and value < min_value:
            print(f"Value must be >= {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be <= {max_value}.")
            continue
        return value


def prompt_non_empty(prompt: str) -> str:
    """Prompt for a non-empty string, looping until valid."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.")


def prompt_choice(prompt: str, *choices: str) -> str:
    """Prompt the user to select from a fixed set of case-insensitive choices."""
    normalized = {c.lower(): c for c in choices}
    while True:
        value = input(f"{prompt} ({'/'.join(choices)}): ").strip().lower()
        if value in normalized:
            return normalized[value]
        print("Invalid choice. Try again.")


