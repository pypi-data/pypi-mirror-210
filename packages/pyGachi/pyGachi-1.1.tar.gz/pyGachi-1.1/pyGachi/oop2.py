class Product:
    def __init__(self, name, store, price):
        self.__name = name
        self.__store = store
        self.__price = price

    def get_name(self):
        return self.__name

    def get_store(self):
        return self.__store

    def get_price(self):
        return self.__price


class Warehouse:
    def __init__(self):
        self.__products = []

    def add_product(self, product):
        self.__products.append(product)

    def get_product_by_index(self, index):
        if index < len(self.__products):
            return self.__products[index]
        else:
            return None

    def get_product_by_name(self, name):
        for product in self.__products:
            if product.get_name() == name:
                return product
        return None

    def sort_by_store(self):
        self.__products.sort(key=lambda product: product.get_store())

    def sort_by_name(self):
        self.__products.sort(key=lambda product: product.get_name())

    def sort_by_price(self):
        self.__products.sort(key=lambda product: product.get_price())

    def __add__(self, other):
        total_price = 0
        for product in self.__products + other.__products:
            total_price += product.get_price()
        return total_price


# Создаем товары
product1 = Product("Книга", "Магазин книг", 500)
product2 = Product("Мышь", "Магазин компьютеров", 1500)
product3 = Product("Клавиатура", "Магазин компьютеров", 2000)

# Создаем склад и добавляем товары
warehouse = Warehouse()
warehouse.add_product(product1)
warehouse.add_product(product2)
warehouse.add_product(product3)

# Выводим информацию о товарах
print(warehouse.get_product_by_index(0).get_name())
print(warehouse.get_product_by_name("Мышь").get_price())

# Сортируем товары по названию магазина, по наименованию и по цене
warehouse.sort_by_store()
print([product.get_store() for product in warehouse._Warehouse__products])

warehouse.sort_by_name()
print([product.get_name() for product in warehouse._Warehouse__products])

warehouse.sort_by_price()
print([product.get_price() for product in warehouse._Warehouse__products])

# Выполняем сложение цен товаров на складах
warehouse2 = Warehouse()
warehouse2.add_product(Product("Наушники", "Магазин электроники", 1000))
print(warehouse + warehouse2)
