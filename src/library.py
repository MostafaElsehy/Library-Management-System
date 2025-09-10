"""Library service managing books, users and operations.

Responsibilities:
- Maintain in-memory stores for books and users (dicts)
- Handle borrow/return flows and a FIFO request queue
- Provide search and popularity queries
- Maintain a user-book interaction graph for recommendations
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import heapq
import json
import os

from book import Book
from user import User
from data_structures import LinkedListQueue, Graph


class Library:
    """Library domain service holding state and providing operations.

    Manages in-memory collections of books and users, a FIFO borrow request
    queue, and a user↔book interaction graph to support recommendations.
    """

    def __init__(self) -> None:
        self.books: Dict[str, Book] = {}
        self.users: Dict[str, User] = {}
        self.borrow_requests: LinkedListQueue[Tuple[str, str]] = LinkedListQueue()
        self.user_book_graph: Graph = Graph()

    # CRUD operations for books
    def add_book(self, book: Book) -> None:
        """Insert a book or merge copy counts if the id already exists."""
        if book.item_id in self.books:
            # Update copies if re-adding with same id
            existing = self.books[book.item_id]
            existing.total_copies += book.total_copies
            existing._available_copies += book._available_copies
            return
        self.books[book.item_id] = book
        self.user_book_graph.add_node(f"book:{book.item_id}")

    def remove_book(self, book_id: str) -> bool:
        """Remove a book by id. Returns True if it existed."""
        return self.books.pop(book_id, None) is not None

    def update_book(self, book_id: str, **updates: object) -> bool:
        """Update attributes on a book if present. Returns success flag."""
        book = self.books.get(book_id)
        if not book:
            return False
        for key, value in updates.items():
            if hasattr(book, key):
                setattr(book, key, value)
        return True

    # User operations
    def add_user(self, user: User) -> None:
        """Register a new user (no-op if user_id already present)."""
        if user.user_id in self.users:
            return
        self.users[user.user_id] = user
        self.user_book_graph.add_node(f"user:{user.user_id}")

    # Searching
    def search_books(self, *, title: Optional[str] = None, author: Optional[str] = None, genre: Optional[str] = None) -> List[Book]:
        """Search books by partial title/author or exact genre (case-insensitive)."""
        def match(b: Book) -> bool:
            ok = True
            if title is not None:
                ok = ok and title.lower() in b.title.lower()
            if author is not None:
                ok = ok and author.lower() in b.author.lower()
            if genre is not None:
                ok = ok and genre.lower() == b.genre.lower()
            return ok

        return [b for b in self.books.values() if match(b)]

    # Borrow / Return
    def enqueue_borrow_request(self, user_id: str, book_id: str) -> None:
        """Add a borrow request to the FIFO queue."""
        self.borrow_requests.enqueue((user_id, book_id))

    def process_next_borrow(self) -> bool:
        """Attempt to fulfill the next queued borrow request."""
        if not self.borrow_requests:
            return False
        user_id, book_id = self.borrow_requests.dequeue()
        return self.borrow_book(user_id, book_id)

    def borrow_book(self, user_id: str, book_id: str) -> bool:
        """Borrow a book for a user, updating counts and the interaction graph."""
        user = self.users.get(user_id)
        book = self.books.get(book_id)
        if not user or not book:
            return False
        if not book.can_borrow():
            return False
        book.borrow_one()
        user.borrow(book_id)
        self.user_book_graph.add_edge(f"user:{user_id}", f"book:{book_id}")
        return True

    def return_book(self, user_id: str, book_id: str) -> bool:
        """Return a book from a user, updating availability. Returns success flag."""
        user = self.users.get(user_id)
        book = self.books.get(book_id)
        if not user or not book:
            return False
        if book_id not in user.borrowed_books:
            return False
        book.return_one()
        user.return_book(book_id)
        return True

    # Popularity
    def top_k_books(self, k: int) -> List[Book]:
        """Return the K most borrowed books (empty if k <= 0)."""
        if k <= 0:
            return []
        return heapq.nlargest(k, self.books.values(), key=lambda b: b.borrow_count)

    # Utility
    def available_books(self) -> List[Book]:
        """List books with at least one available copy, sorted by title then author."""
        return sorted(
            [b for b in self.books.values() if b.available_copies > 0],
            key=lambda b: (b.title.lower(), b.author.lower()),
        )

    # Persistence
    def _snapshot(self) -> Dict[str, object]:
        """Create a JSON-serializable snapshot of the library state."""
        return {
            "version": 1,
            "books": {bid: b.to_dict() for bid, b in self.books.items()},
            "users": {uid: u.to_dict() for uid, u in self.users.items()},
            "borrow_requests": self._borrow_requests_as_list(),
        }

    def _borrow_requests_as_list(self) -> List[Tuple[str, str]]:
        # Convert queue to list without mutating it (iterate the linked list)
        items: List[Tuple[str, str]] = []
        node = self.borrow_requests._head  # type: ignore[attr-defined]
        while node is not None:
            items.append(node.value)  # type: ignore[attr-defined]
            node = node.next  # type: ignore[attr-defined]
        return items

    def save_to_file(self, filepath: str) -> None:
        """Save the current state to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._snapshot(), f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> bool:
        """Load state from a JSON file. Returns True if successful."""
        path = os.path.abspath(filepath)
        if not os.path.exists(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False

        # Reset current state
        self.books.clear()
        self.users.clear()
        self.borrow_requests = LinkedListQueue()
        self.user_book_graph = Graph()

        # Rebuild books
        books_data = data.get("books", {})
        for bid, bdict in books_data.items():
            try:
                book = Book(
                    bid,
                    str(bdict.get("title", "")),
                    str(bdict.get("author", "")),
                    genre=str(bdict.get("genre", "")),
                    total_copies=int(bdict.get("total_copies", 0)),
                    _available_copies=int(bdict.get("available_copies", 0)),
                )
                book.borrow_count = int(bdict.get("borrow_count", 0))
                self.add_book(book)
            except Exception:
                continue

        # Rebuild users
        users_data = data.get("users", {})
        for uid, udict in users_data.items():
            try:
                interests = set(udict.get("interests", []))
                borrowed = set(udict.get("borrowed_books", []))
                history = list(udict.get("history", []))
                user = User(uid, str(udict.get("name", "")), interests=interests)
                user.borrowed_books = set(borrowed)
                user.history = list(history)
                self.add_user(user)
            except Exception:
                continue

        # Rebuild interaction graph (from user history)
        for uid, user in self.users.items():
            for bid in user.history:
                if bid in self.books:
                    self.user_book_graph.add_edge(f"user:{uid}", f"book:{bid}")

        # Rebuild borrow request queue
        for entry in data.get("borrow_requests", []) or []:
            try:
                u, b = entry
                self.enqueue_borrow_request(str(u), str(b))
            except Exception:
                continue

        return True


