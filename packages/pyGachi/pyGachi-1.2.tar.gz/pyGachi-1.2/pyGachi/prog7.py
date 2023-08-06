from tkinter import *
from sqlite3 import *

def sql_connection():
    try:
        con = connect('DB2.db')
        return con
    except Error as e:
        print(e)

def sql_table(con):
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Данные (
                 Фамилия TEXT,
                 Имя TEXT,
                 Отчество TEXT,
                 Группа TEXT,
                 Оценка1 INT,
                 Оценка2 INT,
                 Оценка3 INT);
               """)
    con.commit()

def Vvod():
    if (isinstance(tx1, Entry) and isinstance(tx2, Entry) and isinstance(tx3, Entry) and isinstance(tx4, Entry) and
            isinstance(tx5, Entry) and isinstance(tx6, Entry)):
        if (tx1.get() != "" and tx2.get() != "" and tx3.get() != "" and tx4.get() != "" and tx5.get() != "" and tx6.get() != ""):
            cur = con.cursor()
            cur.execute("INSERT INTO Данные (Фамилия, Имя, Отчество, Группа, Оценка1, Оценка2, Оценка3) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (tx1.get(), tx2.get(), tx3.get(), tx4.get(), tx5.get(), tx6.get(), tx7.get()))
            print("Данные внесены")

def Vivod():
    cur = con.cursor()
    cur.execute("SELECT * FROM Данные")
    res = cur.fetchall()
    print(res)
    con.commit()

def Close():
    exit()

con = sql_connection()

w = Tk()
w.title("Форма для ввода информации о студентах")

sql_table(con)

# Создание и размещение меток и полей для ввода данных
labels = ['Фамилия', 'Имя', 'Отчество', 'Группа', 'Оценка 1', 'Оценка 2', 'Оценка 3']
entries = []

for i, label_text in enumerate(labels):
    label = Label(w, text=label_text, font='Verdana 16', width="20", height="3")
    label.grid(row=i, column=0)
    entry = Entry(w, font='Verdana 16')
    entry.grid(row=i, column=1)
    entries.append(entry)

# Присваивание переменным tx1, tx2, tx3, tx4, tx5 и tx6 значения полей ввода
tx1, tx2, tx3, tx4, tx5, tx6, tx7 = entries
btn1 = Button(w, text="Ввод", font='Verdana 16', command=Vvod)
btn1.grid(row=len(labels), column=0)
btn2 = Button(w, text="Вывод", font='Verdana 16', command=Vivod)
btn2.grid(row=len(labels), column=1)
btn3 = Button(w, text="Выход", font='Verdana 16', command=Close)
btn3.grid(row=len(labels), column=2)

w.mainloop()
