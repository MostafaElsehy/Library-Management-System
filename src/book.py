"""Book and LibraryItem models.

This module demonstrates OOP concepts:
- Encapsulation: `Book.available_copies` guarded by methods
- Inheritance: `Book` extends `LibraryItem`
- Polymorphism: `to_dict` overridden in `Book`
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LibraryItem:
    """Base class for items stored in the library.

    Demonstrates inheritance and encapsulation through properties.

    Attributes:
        item_id: Stable identifier for the library item.
        title: Human-readable title.
        author: Primary author name.
    """

    item_id: str
    title: str
    author: str

    def __post_init__(self) -> None:
        if not self.item_id or not self.title or not self.author:
            raise ValueError("item_id, title and author are required")

    def to_dict(self) -> Dict[str, str]:
        """Serialize common fields into a dictionary."""
        return {
            "id": self.item_id,
            "title": self.title,
            "author": self.author,
        }


@dataclass
class Book(LibraryItem):
    """Represents a book in the library.

    - Uses encapsulated properties for copy counts
    - Tracks borrow popularity

    Attributes:
        genre: Canonical genre label (lowercase recommended).
        total_copies: Total number of copies owned.
        _available_copies: Internal mutable available counter.
        borrow_count: Number of successful borrow operations.
    """

    genre: str
    total_copies: int = field(default=1)
    _available_copies: int = field(default=1, repr=False)
    borrow_count: int = field(default=0)

    def __post_init__(self) -> None:  # type: ignore[override]
        super().__post_init__()
        if self.total_copies < 0:
            raise ValueError("total_copies must be >= 0")
        if self._available_copies < 0 or self._available_copies > self.total_copies:
            self._available_copies = self.total_copies
        if not self.genre:
            raise ValueError("genre is required")

    @property
    def available_copies(self) -> int:
        """Number of copies currently available for borrowing."""
        return self._available_copies

    def can_borrow(self) -> bool:
        """Return whether a copy can be borrowed right now."""
        return self._available_copies > 0

    def borrow_one(self) -> None:
        """Borrow a single copy, decreasing availability and increasing popularity."""
        if self._available_copies <= 0:
            raise ValueError("No available copies to borrow")
        self._available_copies -= 1
        self.borrow_count += 1

    def return_one(self) -> None:
        """Return a single copy, increasing availability."""
        if self._available_copies >= self.total_copies:
            raise ValueError("All copies already returned")
        self._available_copies += 1

    def to_dict(self) -> Dict[str, str | int]:  # type: ignore[override]
        """Serialize book fields into a dictionary including availability and popularity."""
        base = super().to_dict()
        base.update(
            {
                "genre": self.genre,
                "total_copies": self.total_copies,
                "available_copies": self.available_copies,
                "borrow_count": self.borrow_count,
            }
        )
        return base


