"""Console application entry point for the Library Management System.

Features:
- CRUD for books and users
- Borrow/Return with a request queue
- Top-K popularity
- Recommendations via graph traversal

The UI leverages helpers in `ui.py` for consistent terminal output.
"""

from __future__ import annotations

"""Console application wiring for the interactive CLI."""


from book import Book
from library import Library
from user import User
from recommendation import RecommendationEngine
from ui import error, info, menu, success, table, title, wait_key
from validation import prompt_choice, prompt_int, prompt_non_empty
import os


class Application:
    """Interactive console application to manage the library system."""
    def __init__(self) -> None:
        self.library = Library()
        self.reco = RecommendationEngine(self.library)
        # Attempt to load persisted state; if unavailable, seed demo data.
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "library.json")
        self._data_file = os.path.abspath(data_path)
        if not self.library.load_from_file(self._data_file):
            self._seed_data()

    def _seed_data(self) -> None:
        # Seed some books and users for demo purposes
        books = [
            Book("b1", "Clean Code", "Robert C. Martin", genre="technology", total_copies=3, _available_copies=3),
            Book("b2", "The Pragmatic Programmer", "Andrew Hunt", genre="technology", total_copies=2, _available_copies=2),
            Book("b3", "1984", "George Orwell", genre="fiction", total_copies=2, _available_copies=2),
            Book("b4", "To Kill a Mockingbird", "Harper Lee", genre="fiction", total_copies=1, _available_copies=1),
            Book("b5", "Sapiens", "Yuval Noah Harari", genre="history", total_copies=2, _available_copies=2),
        ]
        for b in books:
            self.library.add_book(b)

        users = [
            User("u1", "Alice", interests={"technology", "history"}),
            User("u2", "Bob", interests={"fiction"}),
        ]
        for u in users:
            self.library.add_user(u)

    def run(self) -> None:
        """Run the main menu loop until the user chooses to exit."""
        while True:
            title("Library Management System")
            self._print_menu()
            choice = prompt_int("Choose an option: ", min_value=1, max_value=10)
            if choice == 1:
                self._add_book()
            elif choice == 2:
                self._remove_book()
            elif choice == 3:
                self._update_book()
            elif choice == 4:
                self._add_user()
            elif choice == 5:
                self._borrow_book()
            elif choice == 6:
                self._return_book()
            elif choice == 7:
                self._show_available_books()
            elif choice == 8:
                self._show_top_k()
            elif choice == 9:
                self._recommend()
            elif choice == 10:
                print("Goodbye!")
                try:
                    self.library.save_to_file(self._data_file)
                    info("State saved.")
                except Exception as e:  # noqa: BLE001
                    error(f"Failed to save state: {e}")
                break

    def _print_menu(self) -> None:
        """Render the main menu options."""
        options = [
            "Add Book",
            "Remove Book",
            "Update Book",
            "Add User",
            "Borrow Book",
            "Return Book",
            "Show Available Books",
            "Show Top-K Books",
            "Recommend Books",
            "Exit",
        ]
        menu(options)

    def _add_book(self) -> None:
        """Prompt the user for book fields and add it to the library."""
        book_id = prompt_non_empty("Book ID: ")
        title = prompt_non_empty("Title: ")
        author = prompt_non_empty("Author: ")
        genre = prompt_non_empty("Genre: ").lower()
        copies = prompt_int("Total copies: ", min_value=0)
        available = prompt_int("Available copies: ", min_value=0, max_value=copies)
        try:
            book = Book(book_id, title, author, genre=genre, total_copies=copies, _available_copies=available)
            self.library.add_book(book)
            success("Book added.")
        except Exception as e:  # noqa: BLE001
            error(f"Failed to add book: {e}")
        finally:
            wait_key()

    def _remove_book(self) -> None:
        """Remove a book by id if it exists."""
        book_id = prompt_non_empty("Book ID to remove: ")
        ok = self.library.remove_book(book_id)
        success("Removed.") if ok else error("Book not found.")
        wait_key()

    def _update_book(self) -> None:
        """Update mutable properties of a book by id."""
        book_id = prompt_non_empty("Book ID to update: ")
        if book_id not in self.library.books:
            error("Book not found.")
            wait_key()
            return
        print("Leave a field blank to skip updating it.")
        title = input("New Title: ").strip()
        author = input("New Author: ").strip()
        genre = input("New Genre: ").strip().lower()
        updates = {}
        if title:
            updates["title"] = title
        if author:
            updates["author"] = author
        if genre:
            updates["genre"] = genre
        ok = self.library.update_book(book_id, **updates)
        success("Updated.") if ok else error("Update failed.")
        wait_key()

    def _add_user(self) -> None:
        """Create a new user with optional interests and add to the library."""
        user_id = prompt_non_empty("User ID: ")
        name = prompt_non_empty("Name: ")
        interests_raw = input("Interests (comma-separated genres): ").strip()
        interests = {s.strip().lower() for s in interests_raw.split(',') if s.strip()}
        try:
            user = User(user_id, name, interests=interests)
            self.library.add_user(user)
            success("User added.")
        except Exception as e:  # noqa: BLE001
            error(f"Failed to add user: {e}")
        finally:
            wait_key()

    def _borrow_book(self) -> None:
        """Borrow a book or enqueue if not available."""
        user_id = prompt_non_empty("User ID: ")
        book_id = prompt_non_empty("Book ID: ")
        if user_id not in self.library.users:
            error("User not found.")
            wait_key()
            return
        if book_id not in self.library.books:
            error("Book not found.")
            wait_key()
            return
        if self.library.borrow_book(user_id, book_id):
            success("Borrowed.")
        else:
            info("Book not available. Added to borrow queue.")
            self.library.enqueue_borrow_request(user_id, book_id)
        wait_key()

    def _return_book(self) -> None:
        """Return a book and process any queued borrow requests."""
        user_id = prompt_non_empty("User ID: ")
        book_id = prompt_non_empty("Book ID: ")
        if self.library.return_book(user_id, book_id):
            success("Returned.")
            # Try to process next queued request automatically
            processed = self.library.process_next_borrow()
            if processed:
                info("A queued request has been processed.")
        else:
            error("Return failed.")
        wait_key()

    def _show_available_books(self) -> None:
        """Display all books with at least one available copy."""
        books = self.library.available_books()
        if not books:
            info("No available books.")
            wait_key()
            return
        rows = [
            [b.item_id, b.title, b.author, b.genre, f"{b.available_copies}/{b.total_copies}", str(b.borrow_count)]
            for b in books
        ]
        table(rows, headers=["ID", "Title", "Author", "Genre", "Avail/Total", "Borrowed"]) 
        wait_key()

    def _show_top_k(self) -> None:
        """Display the most-borrowed K books."""
        k = prompt_int("Top K = ", min_value=1)
        top = self.library.top_k_books(k)
        if not top:
            info("No books to show.")
            wait_key()
            return
        rows = [[str(i), b.title, b.author, b.genre, str(b.borrow_count)] for i, b in enumerate(top, start=1)]
        table(rows, headers=["#", "Title", "Author", "Genre", "Borrowed"]) 
        wait_key()

    def _recommend(self) -> None:
        """Show recommended books for a user from the recommendation engine."""
        user_id = prompt_non_empty("User ID: ")
        k = prompt_int("Number of recommendations: ", min_value=1)
        results = self.reco.recommend_for_user(user_id, k)
        if not results:
            info("No recommendations available.")
            wait_key()
            return
        rows = [[str(i), b.title, b.author, b.genre, f"{score:.2f}"] for i, (b, score) in enumerate(results, start=1)]
        table(rows, headers=["#", "Title", "Author", "Genre", "Score"]) 
        wait_key()


if __name__ == "__main__":
    Application().run()


