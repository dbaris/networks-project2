import queue

class Key:
    def __init__(self, priority, url):
        self.priority = priority
        self.id = url

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def get_priority(self):
        return self.priority

    def get_id(self):
        return self.id

class Cache:
    def __init__(self, capacity) :
        self.capacity = capacity
        self.size = 0
        self.rank = 0
        self.keyQueue = queue.PriorityQueue(maxsize=capacity)
        self.cache = {}

    def print(self):
        print("Cache Contents:")
        if self.size == 0:
            print("Empty")

        else:
            print("Size: %d elements" % (self.size,))
            newq = queue.PriorityQueue(maxsize=self.capacity)
            for i in range (0, self.size):
                k = self.keyQueue.get()
                html = self.cache[k.get_id()]
                print("%d) %s --> %s" % (k.get_priority(), k.get_id(), html))
                newq.put(k)

            self.keyQueue = newq

    def add(self, url, html):
        inCache = self.cache.get(url, None)

        # Not in cache 
        if inCache is None:
            # if cache is full, remove something
            if self.size == self.capacity:
                oldKey = self.keyQueue.get()
                self.cache.pop(oldKey.get_id())
                self.size -= 1

            # add url/html to cache
            self.cache[url] = html
            self.size += 1

            # add url to end of queue
            self.keyQueue.put(Key(self.rank, url))
            self.rank += 1

        else:
            # move url location on queue
            newq = queue.PriorityQueue(maxsize=self.capacity)

            for i in range(0, self.size):
                k = self.keyQueue.get()
                if k.get_id() == url and self.cache[url] == html:
                    k.priority = self.rank
                newq.put(k)
            
            self.keyQueue = newq
            self.rank += 1


    def clear(self):
        self.cache = {}
        self.keyQueue = queue.PriorityQueue(maxsize=self.capacity)
        self.size = 0
        self.rank = 0

    # Returns page if found in cache, or None
    def get(self, url):
        return self.cache.get(url, None)        


def test():
    test_cap = 100
    c = Cache(test_cap)

    for i in range(0, test_cap):
        c.add(str(i), "<html>" + str(i) + "</html>")
    c.print()

    c.add(str(i + 1), "this should be at the back, cache should start @1")
    c.print()

    c.add(str(2), "<html>" + str(2) + "</html>")
    c.print()

    if (c.get("2") != "<html>2</html>"):
        print("FAILED TEST")
        return

    c.clear()
    c.print()

    if (c.get("2") != None):
        print("FAILED TEST")
        return

    print("PASSED (...probably)")


def main():
    test()


main()
