class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        curr_node = self.head
        while curr_node.next:
            curr_node = curr_node.next
        curr_node.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def insert_after_node(self, prev_node, data):
        if not prev_node:
            print("Предыдущий узел отсутствует в списке")
            return
        new_node = Node(data)
        new_node.next = prev_node.next
        prev_node.next = new_node

    def delete_node(self, key):
        curr_node = self.head
        if curr_node and curr_node.data == key:
            self.head = curr_node.next
            curr_node = None
            return
        prev_node = None
        while curr_node and curr_node.data != key:
            prev_node = curr_node
            curr_node = curr_node.next
        if curr_node is None:
            return
        prev_node.next = curr_node.next
        curr_node = None

    def print_list(self):
        curr_node = self.head
        while curr_node:
            print(curr_node.data, end=" ")
            curr_node = curr_node.next

# Создание связного списка с вводом
linked_list = LinkedList()

n = int(input("Введите количество элементов: "))

for i in range(n):
    val = input(f"Введите значение {i+1}-го элемента: ")
    linked_list.append(val)

# Вывод списка
print("Список: ", end="")
linked_list.print_list()

# Добавление элемента в начало списка
val = input("\nВведите значение для добавления в начало списка: ")
linked_list.prepend(val)
print("Список после добавления в начало: ", end="")
linked_list.print_list()

# Добавление элемента после указанного узла
pos = int(input("\nВведите позицию для добавления элемента: "))
node = linked_list.head
for i in range(pos-1):
    node = node.next
val = input(f"Введите значение для добавления после элемента {node.data}: ")
linked_list.insert_after_node(node, val)
print("Список после добавления элемента: ", end="")
linked_list.print_list()

# Удаление элемента
val = input("\nВведите значение для удаления: ")
linked_list.delete_node(val)
print("Список после удаления элемента: ", end="")
linked_list.print_list()
