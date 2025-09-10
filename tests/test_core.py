import unittest

from book import Book
from user import User
from library import Library
from recommendation import RecommendationEngine


class LibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lib = Library()
        self.b1 = Book("b1", "A", "Auth", genre="tech", total_copies=1, _available_copies=1)
        self.b2 = Book("b2", "B", "Auth", genre="fiction", total_copies=1, _available_copies=1)
        self.lib.add_book(self.b1)
        self.lib.add_book(self.b2)
        self.u1 = User("u1", "User1", interests={"tech"})
        self.u2 = User("u2", "User2", interests={"fiction"})
        self.lib.add_user(self.u1)
        self.lib.add_user(self.u2)

    def test_borrow_and_return(self):
        ok = self.lib.borrow_book("u1", "b1")
        self.assertTrue(ok)
        self.assertEqual(self.b1.available_copies, 0)
        self.assertIn("b1", self.u1.borrowed_books)

        ok = self.lib.return_book("u1", "b1")
        self.assertTrue(ok)
        self.assertEqual(self.b1.available_copies, 1)
        self.assertNotIn("b1", self.u1.borrowed_books)

    def test_queue_when_unavailable(self):
        self.assertTrue(self.lib.borrow_book("u1", "b1"))
        self.assertFalse(self.lib.borrow_book("u2", "b1"))
        self.lib.enqueue_borrow_request("u2", "b1")
        self.assertEqual(len(self.lib.borrow_requests), 1)
        # returning should process queued request
        self.assertTrue(self.lib.return_book("u1", "b1"))
        self.lib.process_next_borrow()
        self.assertIn("b1", self.u2.borrowed_books)

    def test_top_k(self):
        self.lib.borrow_book("u1", "b1")
        self.lib.return_book("u1", "b1")
        self.lib.borrow_book("u1", "b1")
        top = self.lib.top_k_books(1)
        self.assertEqual(top[0].item_id, "b1")


class RecommendationTests(unittest.TestCase):
    def test_recommendations(self):
        lib = Library()
        b1 = Book("b1", "Clean Code", "Martin", genre="tech", total_copies=1, _available_copies=1)
        b2 = Book("b2", "1984", "Orwell", genre="fiction", total_copies=1, _available_copies=1)
        lib.add_book(b1)
        lib.add_book(b2)
        u1 = User("u1", "Alice", interests={"tech"})
        lib.add_user(u1)
        reco = RecommendationEngine(lib)
        # no history -> interest based
        recs = reco.recommend_for_user("u1", 2)
        self.assertTrue(any(book.item_id == "b1" for book, _ in recs))


if __name__ == "__main__":
    unittest.main()


