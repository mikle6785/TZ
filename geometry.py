import tkinter as tk
import random


class Arkanoid:
    def __init__(self, master):
        self.master = master
        self.master.title("Arkanoid")

        # Настройки игрового поля
        self.canvas_width = 600
        self.canvas_height = 600
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        # Параметры платформы
        self.paddle_width = 80
        self.paddle_height = 10
        self.paddle_x = (self.canvas_width - self.paddle_width) / 2
        self.paddle_y = self.canvas_height - self.paddle_height - 20
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x, self.paddle_y,
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height,
            fill="white"
        )

        # Параметры мяча
        self.ball_size = 10
        self.ball_x = self.canvas_width / 2
        self.ball_y = self.canvas_height / 2
        self.ball_x_speed = 3
        self.ball_y_speed = -3
        self.ball = self.canvas.create_oval(
            self.ball_x - self.ball_size, self.ball_y - self.ball_size,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            fill="white"
        )

        # Создание блоков
        self.blocks = []
        self.block_width = 40
        self.block_height = 20
        self.create_blocks()

        # Управление
        self.master.bind("<Left>", self.move_paddle_left)
        self.master.bind("<Right>", self.move_paddle_right)
        self.master.bind("<space>", self.toggle_pause)  # Изменено на toggle_pause
        self.master.bind("<p>", self.toggle_pause)  # Добавлена альтернативная клавиша паузы

        # Игровые параметры
        self.game_active = False
        self.game_paused = False  # Добавлено состояние паузы
        self.lives = 3
        self.score = 0

        # Отображение жизней и счета в верхних углах
        self.label_lives = self.canvas.create_text(
            50, 20,
            text=f"Lives: {self.lives}",
            fill="white", font=("Arial", 12),
            anchor="w"
        )

        self.label_score = self.canvas.create_text(
            self.canvas_width - 50, 20,
            text=f"Score: {self.score}",
            fill="white", font=("Arial", 12),
            anchor="e"
        )

        # Начальное сообщение
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Press SPACE to start",
            fill="white", font=("Arial", 20)
        )

        # Текст паузы
        self.pause_text = None

    def toggle_pause(self, event):
        if not self.game_active and not self.game_paused:
            # Если игра не активна и не на паузе - начинаем игру
            self.start_game(event)
        elif self.game_active:
            # Если игра активна - ставим на паузу
            self.game_active = False
            self.game_paused = True
            self.pause_text = self.canvas.create_text(
                self.canvas_width / 2, self.canvas_height / 2,
                text="PAUSED\nPress SPACE or P to continue",
                fill="white", font=("Arial", 20),
                justify="center"
            )
        elif self.game_paused:
            # Если игра на паузе - продолжаем
            self.game_active = True
            self.game_paused = False
            self.canvas.delete(self.pause_text)
            self.game_loop()

    def start_game(self, event):
        if not self.game_active and not self.game_paused:
            self.game_active = True
            self.canvas.delete(self.start_text)
            self.game_loop()

    def create_blocks(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        rows = 5
        cols = 10
        for row in range(rows):
            for col in range(cols):
                x = col * (self.block_width + 5) + 40
                y = row * (self.block_height + 5) + 60
                color = random.choice(colors)
                block = {
                    'id': self.canvas.create_rectangle(x, y, x + self.block_width, y + self.block_height,
                                                       fill=color),
                    'x': x, 'y': y,
                    'width': self.block_width, 'height': self.block_height,
                    'color': color
                }
                self.blocks.append(block)

    def move_paddle_left(self, event):
        if self.game_active:  # Движение только когда игра активна (не на паузе)
            self.paddle_x = max(0, self.paddle_x - 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

    def move_paddle_right(self, event):
        if self.game_active:  # Движение только когда игра активна (не на паузе)
            self.paddle_x = min(self.canvas_width - self.paddle_width, self.paddle_x + 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

    def game_loop(self):
        if not self.game_active or self.game_paused:
            return

        self.move_ball()
        self.check_collisions()

        if self.lives <= 0:
            self.game_over()
            return

        if not self.blocks:
            self.level_completed()
            return

        self.master.after(30, self.game_loop)

    def move_ball(self):
        if self.game_paused:  # Не двигаем мяч на паузе
            return

        self.ball_x += self.ball_x_speed
        self.ball_y += self.ball_y_speed

        # Отражение от стен
        if self.ball_x - self.ball_size <= 0 or self.ball_x + self.ball_size >= self.canvas_width:
            self.ball_x_speed *= -1
        if self.ball_y - self.ball_size <= 0:
            self.ball_y_speed *= -1

        self.canvas.coords(self.ball,
                           self.ball_x - self.ball_size, self.ball_y - self.ball_size,
                           self.ball_x + self.ball_size, self.ball_y + self.ball_size)

    def check_collisions(self):
        # Коллизия с платформой
        paddle_coords = self.canvas.coords(self.paddle)
        if (self.ball_y + self.ball_size >= paddle_coords[1] and
                self.ball_y - self.ball_size <= paddle_coords[3] and
                self.ball_x + self.ball_size >= paddle_coords[0] and
                self.ball_x - self.ball_size <= paddle_coords[2]):
            self.ball_y_speed *= -1

        # Коллизия с блоками
        for block in self.blocks[:]:
            block_left = block['x']
            block_right = block['x'] + block['width']
            block_top = block['y']
            block_bottom = block['y'] + block['height']

            ball_left = self.ball_x - self.ball_size
            ball_right = self.ball_x + self.ball_size
            ball_top = self.ball_y - self.ball_size
            ball_bottom = self.ball_y + self.ball_size

            if (ball_right > block_left and
                    ball_left < block_right and
                    ball_bottom > block_top and
                    ball_top < block_bottom):

                # Удаляем блок
                self.canvas.delete(block['id'])
                self.blocks.remove(block)
                self.score += 10
                self.canvas.itemconfig(self.label_score, text=f"Score: {self.score}")

                # Определяем направление отскока
                delta_left = abs(ball_right - block_left)
                delta_right = abs(ball_left - block_right)
                delta_top = abs(ball_bottom - block_top)
                delta_bottom = abs(ball_top - block_bottom)

                min_delta = min(delta_left, delta_right, delta_top, delta_bottom)

                if min_delta == delta_left or min_delta == delta_right:
                    self.ball_x_speed *= -1
                else:
                    self.ball_y_speed *= -1

                break

        # Проверка выхода за нижнюю границу
        if self.ball_y + self.ball_size > self.canvas_height:
            self.lives -= 1
            self.canvas.itemconfig(self.label_lives, text=f"Lives: {self.lives}")
            if self.lives > 0:
                self.reset_ball()
            else:
                self.game_over()

    def reset_ball(self):
        self.ball_x = self.canvas_width / 2
        self.ball_y = self.canvas_height / 2
        self.ball_x_speed = 3 * (1 if random.random() > 0.5 else -1)
        self.ball_y_speed = -3
        self.game_active = False
        self.game_paused = False  # Сбрасываем паузу при рестарте
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Press SPACE to continue",
            fill="white", font=("Arial", 20))

    def game_over(self):
        self.game_active = False
        self.game_paused = False  # Сбрасываем паузу при окончании игры
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Game Over!", fill="red", font=("Arial", 30))

    def level_completed(self):
        self.game_active = False
        self.game_paused = False  # Сбрасываем паузу при завершении уровня
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Level Completed!", fill="green", font=("Arial", 30))


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()