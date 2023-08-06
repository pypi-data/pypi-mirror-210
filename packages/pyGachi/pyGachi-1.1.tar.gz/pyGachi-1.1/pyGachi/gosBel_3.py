class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Queue:
    def __init__(self):
        self.front = None
        self.rear = None

    def is_empty(self):
        return self.front is None

    def enqueue(self, data):
        new_node = Node(data)

        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node

    def dequeue(self):
        if self.is_empty():
            raise Exception("Queue is empty")

        dequeued_data = self.front.data
        self.front = self.front.next

        if self.front is None:
            self.rear = None

        return dequeued_data

    def peek(self):
        if self.is_empty():
            raise Exception("Queue is empty")

        return self.front.data

    def size(self):
        count = 0
        current = self.front

        while current is not None:
            count += 1
            current = current.next

        return count


queue = Queue()
queue.enqueue(10)
queue.enqueue(20)
queue.enqueue(30)

print(queue.dequeue())  # Вывод: 10
print(queue.peek())  # Вывод: 20
print(queue.size())  # Вывод: 2