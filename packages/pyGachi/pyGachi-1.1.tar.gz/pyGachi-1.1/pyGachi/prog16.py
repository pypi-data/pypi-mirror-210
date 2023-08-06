def count_letter_frequency(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            text = file.read().lower()
            letter_count = {}
            for char in text:
                if char.isalpha() and char.isalpha():
                    letter_count[char] = letter_count.get(char, 0) + 1

            # Вывод результатов
            print("Частота использования букв:")
            for letter, count in sorted(letter_count.items()):
                print(f"{letter}: {count}")

    except FileNotFoundError:
        print("Файл не найден.")


# Укажите имя файла с текстом для анализа
file_name = "book1.txt"

# Подсчет частоты использования букв в файле
count_letter_frequency(file_name)