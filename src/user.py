"""User model for the library system.

Tracks interests, current borrow set, and historical borrow list.
Normalizes interests for case-insensitive comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class User:
    """User entity with normalized interests and basic borrowing state."""
    user_id: str
    name: str
    interests: Set[str] = field(default_factory=set)
    borrowed_books: Set[str] = field(default_factory=set)
    history: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.user_id or not self.name:
            raise ValueError("user_id and name are required")
        # normalize interests to lowercase
        self.interests = {s.strip().lower() for s in self.interests if s.strip()}

    def borrow(self, book_id: str) -> None:
        """Record that a user borrowed a book."""
        self.borrowed_books.add(book_id)
        self.history.append(book_id)

    def return_book(self, book_id: str) -> None:
        """Record that a user returned a book (idempotent)."""
        self.borrowed_books.discard(book_id)

    def to_dict(self) -> Dict[str, object]:
        """Serialize the user into a dictionary for display or storage."""
        return {
            "id": self.user_id,
            "name": self.name,
            "interests": sorted(self.interests),
            "borrowed_books": sorted(self.borrowed_books),
            "history": list(self.history),
        }


