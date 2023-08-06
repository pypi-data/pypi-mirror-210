class Train:
    def __init__(self, destination, number, departure_time):
        self.__destination = destination
        self.__number = number
        self.__departure_time = departure_time

    def get_destination(self):
        return self.__destination

    def get_number(self):
        return self.__number

    def get_departure_time(self):
        return self.__departure_time

    def __lt__(self, other):
        return self.__departure_time < other.get_departure_time()

    def __str__(self):
        return f"Train {self.__number} to {self.__destination}, departs at {self.__departure_time}"


class TrainStation:
    def __init__(self):
        self.__trains = []

    def add_train(self, train):
        self.__trains.append(train)

    def get_train_by_number(self, number):
        for train in self.__trains:
            if train.get_number() == number:
                return train
        return None

    def get_trains_by_destination(self, destination):
        result = []
        for train in self.__trains:
            if train.get_destination() == destination:
                result.append(train)
        result.sort()
        return result

    def get_trains_departing_after(self, departure_time):
        result = []
        for train in self.__trains:
            if train.get_departure_time() > departure_time:
                result.append(train)
        result.sort()
        return result

    def __str__(self):
        result = []
        for train in self.__trains:
            result.append(str(train))
        return "\n".join(result)

# Пример использования классов
train1 = Train("Moscow", "123A", "08:00")
train2 = Train("St. Petersburg", "456B", "09:30")
train3 = Train("Kazan", "789C", "11:45")

station = TrainStation()
station.add_train(train1)
station.add_train(train2)
station.add_train(train3)

# Вывод информации о поезде по номеру с помощью индекса
print(station.get_train_by_number("123A"))

# Вывод информации о поездах, отправляющихся после введенного с клавиатуры времени
time = input("Enter departure time: ")
trains = station.get_trains_departing_after(time)
print("Trains departing after", time)
print("\n".join([str(train) for train in trains]))

# Перегруженная операция сравнения, выполняющая сравнение времени отправления двух поездов
print(train1 < train2)

# Вывод информации о поездах, отправляющихся в заданный пункт назначения. Информация должна быть отсортирована по времени отправления
destination = input("Enter destination: ")
trains = station.get_trains_by_destination(destination)
print("Trains to", destination)
print("\n".join([str(train) for train in trains]))
