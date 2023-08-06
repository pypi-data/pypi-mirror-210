def replace_delimiters(string):
    result = ""
    delimiter_flag = False

    for char in string:
        if char in [',', '.', '?', '!', ':', ';', ' ', '\t']:
            if not delimiter_flag:
                result += "*"
                delimiter_flag = True
        else:
            result += char
            delimiter_flag = False

    return result

# Ввод строки символов
input_string = input("Введите строку символов: ")

# Замена разделителей
new_string = replace_delimiters(input_string)

# Вывод результата
print("Результат замены разделителей:", new_string)