from bisect import insort
from bisect import bisect_left


class SortedList:

    """
    Efficient sorted list implementation.
    Maintains a list of elements in sorted order.
    Supports insertion, deletion, and search operations.
    """

    def __init__(self, iterable=None):
        """Initialize the sorted list with an optional iterable."""
        self._list = []
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, item):
        """Add an item to the sorted list."""
        insort(self._list, item)

    def remove(self, item):
        """Remove an item from the sorted list."""
        self._list.remove(item)

    def clear(self):
        """Clear all items from the sorted list."""
        self._list.clear()

    def pop(self, index=-1):
        """Remove and return an item at the given index (default last)."""
        return self._list.pop(index)

    def remove_if_exists(self, item):
        """Remove an item if it exists in the sorted list."""
        if item in self:
            self.remove(item)

    def index(self, item):
        """Return the index of an item in the sorted list."""
        index = bisect_left(self._list, item)
        if index != len(self._list) and self._list[index] == item:
            return index
        raise ValueError(f"{item} not in list")

    def __contains__(self, item):
        """Check if an item is in the sorted list."""
        index = bisect_left(self._list, item)
        return index != len(self._list) and self._list[index] == item

    def __len__(self):
        """Return the number of items in the sorted list."""
        return len(self._list)

    def __getitem__(self, index):
        """Get an item by index."""
        return self._list[index]

    def __iter__(self):
        """Return an iterator over the sorted list."""
        return iter(self._list)

    def __repr__(self):
        """Return a string representation of the sorted list."""
        return f"SortedList{self._list}"
