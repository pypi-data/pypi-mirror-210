import turtle

def draw_chessboard():
    # Создание экземпляра черепашки
    screen = turtle.Screen()
    screen.title("Шахматная доска")
    screen.setup(400, 300)
    turtle_pen = turtle.Turtle()
    turtle_pen.speed(0)

    # Определение размеров клетки
    cell_size = 50

    # Рисование доски
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                turtle_pen.fillcolor("white")
            else:
                turtle_pen.fillcolor("black")

            turtle_pen.penup()
            turtle_pen.goto(col * cell_size, -row * cell_size)
            turtle_pen.pendown()
            turtle_pen.begin_fill()
            for _ in range(4):
                turtle_pen.forward(cell_size)
                turtle_pen.right(90)
            turtle_pen.end_fill()

    # Завершение работы черепашки
    turtle_pen.hideturtle()
    turtle.done()

# Рисование шахматной доски
draw_chessboard()