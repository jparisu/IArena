import heapq
from dataclasses import dataclass
from typing import Any, Generic, List, Protocol, Set, Tuple, TypeVar

from IArena.utils.RandomGenerator import RandomGenerator

T = TypeVar("T")


@dataclass(frozen=True, order=True)
class _HeapItem(Generic[T]):
    """
    Heap ordering is lexicographic by fields:
        (priority, tie, element)

    This makes the queue a min-heap by priority, and random among equal
    priorities due to tie.
    """
    priority: float
    tie: int
    element: T


class RandomTiePriorityQueue(Generic[T]):
    """
    Min-priority queue with:
      - O(1) membership check by element via a set
      - O(log n) insertion
      - O(log n) pop
      - uniform random selection among equal priorities via random tie-break

    Notes:
      - Elements must be hashable (for membership set).
      - No removal/update of arbitrary elements; only pop-min is supported.
      - Duplicate elements are rejected.
    """

    def __init__(self, random_generator: RandomGenerator = None) -> None:
        self._heap: List[_HeapItem[T]] = []
        self._elements: Set[T] = set()
        self._rng: RandomGenerator = random_generator if random_generator is not None else RandomGenerator()

    def __contains__(self, element: T) -> bool:
        return element in self._elements

    def __len__(self) -> int:
        return len(self._heap)

    def push(self, priority: float, element: T) -> None:
        """
        Insert a new (priority, element).

        Raises:
            ValueError: if element already exists in the queue.
        """
        if element in self._elements:
            raise ValueError("Element already exists in the queue")

        tie = self._rng.any_int()
        heapq.heappush(self._heap, _HeapItem(priority=priority, tie=tie, element=element))
        self._elements.add(element)

    def pop(self) -> Tuple[float, T]:
        """
        Remove and return (priority, element) with the smallest priority.
        Among equal priorities, selection is randomized via tie-breaker.

        Raises:
            IndexError: if the queue is empty.
        """
        if not self._heap:
            raise IndexError("pop from empty priority queue")

        item = heapq.heappop(self._heap)
        self._elements.remove(item.element)
        return item.priority, item.element
