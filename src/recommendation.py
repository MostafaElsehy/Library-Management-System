"""Recommendation engine using graph traversal and simple scoring.

Scoring combines:
- Proximity in the user-book graph via BFS depth
- User interest match (genre)
- Global popularity (borrow_count)
"""

from __future__ import annotations

from collections import Counter
from typing import List, Tuple

from book import Book
from library import Library


class RecommendationEngine:
    """Produce book recommendations for users based on a simple heuristic.

    The heuristic combines:
    - Graph proximity: closer nodes in the user-book graph are preferred
    - Interest match: books whose genre is in the user's interests get a bonus
    - Popularity: books with higher borrow_count get a small bonus
    """
    def __init__(self, library: Library) -> None:
        self.library = library

    def recommend_for_user(self, user_id: str, k: int = 5) -> List[Tuple[Book, float]]:
        """Return up to k recommended books with associated scores.

        Args:
            user_id: The id of the user to recommend for.
            k: Maximum number of results to return.
        """
        user = self.library.users.get(user_id)
        if not user:
            return []

        start = f"user:{user_id}"
        traversal = self.library.user_book_graph.bfs(start, max_depth=3)

        # Score candidate books by:
        # - proximity in BFS (closer is better)
        # - shared genre interests
        # - global popularity (borrow_count)
        distance: dict[str, int] = {node: d for node, d in traversal}
        candidate_scores: dict[str, float] = {}

        for node, depth in traversal:
            if node.startswith("book:") and node != f"book:{user_id}":
                book_id = node.split(":", 1)[1]
                if book_id in user.borrowed_books:
                    continue
                book = self.library.books.get(book_id)
                if not book:
                    continue
                # Base score inversely proportional to depth
                score = 1.0 / (1 + depth)
                # Interest bonus
                if book.genre.lower() in user.interests:
                    score += 0.5
                # Popularity bonus (normalized rough factor)
                score += min(book.borrow_count / 10.0, 1.0)
                candidate_scores[book_id] = max(candidate_scores.get(book_id, 0.0), score)

        # Fallback: if graph yields nothing, recommend by interests and popularity
        if not candidate_scores:
            for b in self.library.books.values():
                if b.item_id in user.borrowed_books:
                    continue
                score = 0.0
                if b.genre.lower() in user.interests:
                    score += 0.7
                score += min(b.borrow_count / 10.0, 1.0)
                if score > 0:
                    candidate_scores[b.item_id] = score

        ranked = sorted(
            ((self.library.books[bid], sc) for bid, sc in candidate_scores.items()),
            key=lambda t: (-t[1], -t[0].borrow_count, t[0].title.lower()),
        )
        return ranked[:k]


