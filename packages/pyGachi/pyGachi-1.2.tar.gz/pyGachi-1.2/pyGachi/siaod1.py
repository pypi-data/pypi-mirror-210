class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

    def peek(self):
        return self.items[-1]

    def size(self):
        return len(self.items)

s = Stack()
n = int(input("Введите количество элементов: "))
for i in range(n):
    elem = input(f"Введите элемент {i+1}: ")
    s.push(elem)

print("Удаление элемента: ", s.pop())
print("Получение верхнего элемента без удаления: ", s.peek())
print("Проверка на пустоту: ", s.is_empty())
print("Размер стека: ", s.size()) 
