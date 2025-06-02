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
        self.master.bind("<space>", self.start_game)

        # Игровые параметры
        self.game_active = False
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

    def start_game(self, event):
        if not self.game_active:
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
                y = row * (self.block_height + 5) + 60  # Сместили ниже для счетчиков
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
        if self.game_active:
            self.paddle_x = max(0, self.paddle_x - 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

    def move_paddle_right(self, event):
        if self.game_active:
            self.paddle_x = min(self.canvas_width - self.paddle_width, self.paddle_x + 30)
            self.canvas.coords(self.paddle,
                               self.paddle_x, self.paddle_y,
                               self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height)

    def game_loop(self):
        if not self.game_active:
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
            if (self.ball_x > block['x'] - self.ball_size and
                    self.ball_x < block['x'] + block['width'] + self.ball_size and
                    self.ball_y > block['y'] - self.ball_size and
                    self.ball_y < block['y'] + block['height'] + self.ball_size):

                # Удаляем блок
                self.canvas.delete(block['id'])
                self.blocks.remove(block)
                self.score += 10
                self.canvas.itemconfig(self.label_score, text=f"Score: {self.score}")

                # Определяем направление отскока
                if (self.ball_x + self.ball_size > block['x'] and
                        self.ball_x - self.ball_size < block['x'] + block['width']):
                    self.ball_y_speed *= -1  # Вертикальный отскок
                else:
                    self.ball_x_speed *= -1  # Горизонтальный отскок

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
        self.start_text = self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Press SPACE to continue",
            fill="white", font=("Arial", 20))

    def game_over(self):
        self.game_active = False
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Game Over!", fill="red", font=("Arial", 30))

    def level_completed(self):
        self.game_active = False
        self.canvas.create_text(
            self.canvas_width / 2, self.canvas_height / 2,
            text="Level Completed!", fill="green", font=("Arial", 30))


if __name__ == "__main__":
    root = tk.Tk()
    game = Arkanoid(root)
    root.mainloop()