class Queue:
    def __init__(self, limit: int = 1000):
        self.queue = list()
        self.limit = limit
        self.total = 0

    def __len__(self):
        return len(self.queue)

    def add(self, item):
        self.queue.append(item)
        self.total += 1
        if len(self.queue) > self.limit:
            self.remove(self.queue[-1])

    def remove(self, item):
        self.queue.remove(item)
