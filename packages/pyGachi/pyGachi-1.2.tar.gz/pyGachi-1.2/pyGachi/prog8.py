from tkinter import *
import sqlite3

def create_table():
    conn = sqlite3.connect('students2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                patronymic TEXT,
                birth_date DATE,
                group_number INT)''')
    conn.commit()
    conn.close()

def insert_data():
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    patronymic = entry_patronymic.get()
    birth_date = entry_birth_date.get()
    group_number = entry_group_number.get()

    conn = sqlite3.connect('students2.db')
    c = conn.cursor()
    c.execute("INSERT INTO students2 (first_name, last_name, patronymic, birth_date, group_number) VALUES (?, ?, ?, ?, ?)",
              (first_name, last_name, patronymic, birth_date, group_number))
    conn.commit()
    conn.close()

def retrieve_data():
    conn = sqlite3.connect('students2.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students2")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        print(row)

def close_window():
    retrieve_data()
    window.destroy()

# Создание окна
window = Tk()
window.title("Форма для ввода информации о студентах")
window.geometry("400x300")

# Метки и поля ввода
label_first_name = Label(window, text="Фамилия")
label_first_name.pack()
entry_first_name = Entry(window)
entry_first_name.pack()

label_last_name = Label(window, text="Имя")
label_last_name.pack()
entry_last_name = Entry(window)
entry_last_name.pack()

label_patronymic = Label(window, text="Отчество")
label_patronymic.pack()
entry_patronymic = Entry(window)
entry_patronymic.pack()

label_birth_date = Label(window, text="Дата рождения")
label_birth_date.pack()
entry_birth_date = Entry(window)
entry_birth_date.pack()

label_group_number = Label(window, text="Номер группы")
label_group_number.pack()
entry_group_number = Entry(window)
entry_group_number.pack()

# Кнопки
button_insert = Button(window, text="Ввод", command=insert_data)
button_insert.pack()

button_exit = Button(window, text="Выход", command=close_window)
button_exit.pack()

create_table()

window.mainloop()