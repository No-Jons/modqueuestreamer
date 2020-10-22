class Queue:
    def __init__(self, limit: int = 1000):
        self._items = list()
        self._limit = limit
        self.total = 0

    @property
    def queue(self):
        return self._items

    def __len__(self):
        return len(self._items)

    def add(self, item):
        self._items.append(item)
        self.total += 1
        if len(self._items) > self._limit:
            self.remove(self._items[-1])

    def remove(self, item):
        self._items.remove(item)
