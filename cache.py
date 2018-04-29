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

        # Two data structures: a queue to manage which key to remove &
        #   the cache itself (hash map)
        self.keyQueue = queue.PriorityQueue(maxsize=capacity)
        self.cache = {}

    def size(self):
        return self.size

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
        raise NotImplementedError("Subclass responsibility")

    def clear(self):
        self.cache = {}
        self.keyQueue = queue.PriorityQueue(maxsize=self.capacity)
        self.size = 0
        self.rank = 0

    # Returns page if found in cache, or None
    def get(self, url):
        return self.cache.get(url, None)        


class LFU_Cache(Cache):
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
            self.keyQueue.put(Key(0, url))

        else:
            # move url location on queue
            newq = queue.PriorityQueue(maxsize=self.capacity)

            for i in range(0, self.size):
                k = self.keyQueue.get()
                if k.get_id() == url and self.cache[url] == html:
                    k.priority += 1
                newq.put(k)
            
            self.keyQueue = newq
 

class LRU_Cache(Cache):
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

# def test():
#     test_cap = 5
#     print("************ LRU CACHE TEST ************")
#     c = LRU_Cache(test_cap)

#     for i in range(0, test_cap):
#         c.add(str(i), "<html>" + str(i) + "</html>")
#     c.print()

#     c.add(str(i + 1), "this should be at the back, cache should start @1")
#     c.print()

#     c.add(str(2), "<html>" + str(2) + "</html>")
#     c.print()

#     if (c.get("2") != "<html>2</html>"):
#         print("FAILED TEST")
#         return

#     c.clear()
#     c.print()

#     if (c.get("2") != None):
#         print("FAILED TEST")
#         return

#     print("************ LFU CACHE TEST ************")
#     c2 = LFU_Cache(test_cap)
#     c2.print()


#     for i in range(0, test_cap):
#         for j in range (0, i+1):
#             # print("Adding %d" %(i,))
#             c2.add(str(i), "<html>" + str(i) + "</html>")

#     c2.print()

#     c2.add("5", "<html>5</html>");
#     c2.add("5", "<html>5</html>");
#     c2.add("5", "<html>5</html>");
#     c2.print()

#     print("PASSED")


# def main():
#     test()



# main()
