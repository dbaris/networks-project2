import queue

CAPACITY = 100

class Page:
    def __init__(self, priority, url, html):
        self.priority = priority
        self.id = url
        self.contents = html
        
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

    def get_contents(self):
        return self.contents

class Cache:
    def __init__(self) :
        self.capacity = CAPACITY
        self.size = 0
        self.rank = 0
        # self.cache = CAPACITY * [None]     # this should probs be changed to a queue??
        self.cache = queue.PriorityQueue(maxsize=CAPACITY)

    def print(self):
        print("Cache Contents:")
        if self.size == 0:
            print("Empty")

        else:
            newq = queue.PriorityQueue(maxsize=CAPACITY)
            # print(self.size)
            for i in range (0, self.size):
                p = self.cache.get()
                print("%d) %s --> %s" % (p.get_priority(), p.get_id(), p.get_contents()))
                # print("%d) %s --> %s" % (i + 1, self.cache[i]["id"], self.cache[i]["contents"]))
                newq.put(p)

            self.cache = newq

    def add(self, url, html):

        # Check if in existing cache
        newq = queue.PriorityQueue(maxsize=CAPACITY)
        found = False

        for i in range(0, self.size):
            p = self.cache.get()
            if p.id == url and p.contents == html:
                found = True
                p.priority = self.rank
            newq.put(p)
        
        self.cache = newq

        # If not found, add
        if not found:
            if (self.size == self.capacity):
                self.cache.get()
                self.size -= 1
            self.cache.put(Page(self.rank, url, html))
            self.size += 1

        self.rank += 1
        

def test():
    c = Cache()

    for i in range(0, CAPACITY):
        c.add(str(i), "<html>" + str(i) + "</html>")

    c.add(str(i + 1), "this should be at the back, cache should start @1")
    c.print()

    c.add(str(2), "<html>" + str(2) + "</html>")
    c.print()


# def main():
#     # test()


# main()
