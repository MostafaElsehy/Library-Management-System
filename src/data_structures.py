"""Custom data structures used by the Library system.

- LinkedListQueue: to manage borrow requests efficiently (O(1) enqueue/dequeue)
- Graph: adjacency list to represent user-book interactions and enable BFS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Iterable, Iterator, List, Optional, Set, Tuple, TypeVar


T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    value: T
    next: Optional["_Node[T]"] = None


class LinkedListQueue(Generic[T]):
    """A simple FIFO queue implemented using a singly linked list.

    Operations:
        enqueue: O(1)
        dequeue: O(1)
        peek: O(1)
        __len__: O(1)
    """

    def __init__(self) -> None:
        self._head: Optional[_Node[T]] = None
        self._tail: Optional[_Node[T]] = None
        self._size: int = 0

    def enqueue(self, value: T) -> None:
        """Add a value to the end of the queue."""
        node = _Node(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self) -> T:
        """Remove and return the value at the front of the queue.

        Raises:
            IndexError: If the queue is empty.
        """
        if self._head is None:
            raise IndexError("dequeue from empty queue")
        node = self._head
        self._head = node.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return node.value

    def peek(self) -> T:
        """Return the value at the front of the queue without removing it.

        Raises:
            IndexError: If the queue is empty.
        """
        if self._head is None:
            raise IndexError("peek from empty queue")
        return self._head.value

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0


class Graph:
    """Undirected graph using an adjacency list.

    Nodes are represented by strings (e.g., "user:123", "book:abc").
    """

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = {}

    def add_node(self, node: str) -> None:
        """Ensure a node exists in the adjacency list."""
        self._adj.setdefault(node, set())

    def add_edge(self, a: str, b: str) -> None:
        """Add an undirected edge between two nodes (no self-loops)."""
        if a == b:
            return
        self.add_node(a)
        self.add_node(b)
        self._adj[a].add(b)
        self._adj[b].add(a)

    def neighbors(self, node: str) -> Iterable[str]:
        """Iterate neighbors of a node (empty if absent)."""
        return self._adj.get(node, set())

    def __contains__(self, node: str) -> bool:
        return node in self._adj

    def bfs(self, start: str, max_depth: int = 3) -> List[Tuple[str, int]]:
        """Breadth-first traversal returning nodes with their depth."""
        if start not in self._adj:
            return []
        visited: Set[str] = {start}
        queue: List[Tuple[str, int]] = [(start, 0)]
        order: List[Tuple[str, int]] = []
        i = 0
        while i < len(queue):
            node, depth = queue[i]
            i += 1
            order.append((node, depth))
            if depth >= max_depth:
                continue
            for neigh in self._adj[node]:
                if neigh not in visited:
                    visited.add(neigh)
                    queue.append((neigh, depth + 1))
        return order


