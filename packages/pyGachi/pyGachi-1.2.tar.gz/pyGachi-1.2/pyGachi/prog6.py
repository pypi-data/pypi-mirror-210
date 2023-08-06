from tkinter import *
import sqlite3

def create_table():
    conn = sqlite3.connect('students3.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students3 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                address TEXT,
                phone TEXT)''')
    conn.commit()
    conn.close()

def insert_data():
    full_name = entry_full_name.get()
    address = entry_address.get()
    phone = entry_phone.get()

    conn = sqlite3.connect('students3.db')
    c = conn.cursor()
    c.execute("INSERT INTO students3 (full_name, address, phone) VALUES (?, ?, ?)",
              (full_name, address, phone))
    conn.commit()
    conn.close()

def retrieve_data():
    conn = sqlite3.connect('students3.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students3")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        print(row)

# Создание окна
window = Tk()
window.title("Форма для ввода информации о студентах")
window.geometry("400x300")

# Метки и поля ввода
label_full_name = Label(window, text="ФИО")
label_full_name.pack()
entry_full_name = Entry(window)
entry_full_name.pack()

label_address = Label(window, text="Адрес")
label_address.pack()
entry_address = Entry(window)
entry_address.pack()

label_phone = Label(window, text="Телефон")
label_phone.pack()
entry_phone = Entry(window)
entry_phone.pack()

# Кнопки
button_insert = Button(window, text="Ввод", command=insert_data)
button_insert.pack()

button_retrieve = Button(window, text="Вывод", command=retrieve_data)
button_retrieve.pack()

create_table()

window.mainloop()