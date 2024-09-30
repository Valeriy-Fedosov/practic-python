import pygame
import time
import random
import sqlite3

# Инициализация Pygame
pygame.init()

# Определение цветов
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Параметры игры
WIDTH = 800
HEIGHT = 600
SNAKE_BLOCK = 10
SNAKE_SPEED = 15

# Класс Змейка
class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = 'RIGHT'
        self.grow = False

    def move(self):
        head_x, head_y = self.positions[0]
        if self.direction == 'UP':
            head_y -= SNAKE_BLOCK
        elif self.direction == 'DOWN':
            head_y += SNAKE_BLOCK
        elif self.direction == 'LEFT':
            head_x -= SNAKE_BLOCK
        elif self.direction == 'RIGHT':
            head_x += SNAKE_BLOCK

        new_head = (head_x, head_y)
        self.positions.insert(0, new_head)

        if not self.grow:
            self.positions.pop()
        else:
            self.length += 1
            self.grow = False

    def change_direction(self, new_direction):
        opposite_directions = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        if new_direction != opposite_directions[self.direction]:
            self.direction = new_direction

    def grow_snake(self):
        self.grow = True

# Класс Яблоко
class Apple:
    def __init__(self):
        self.position = (random.randint(0, (WIDTH - SNAKE_BLOCK) // SNAKE_BLOCK) * SNAKE_BLOCK,
                         random.randint(0, (HEIGHT - SNAKE_BLOCK) // SNAKE_BLOCK) * SNAKE_BLOCK)

    def respawn(self):
        self.position = (random.randint(0, (WIDTH - SNAKE_BLOCK) // SNAKE_BLOCK) * SNAKE_BLOCK,
                         random.randint(0, (HEIGHT - SNAKE_BLOCK) // SNAKE_BLOCK) * SNAKE_BLOCK)

# Функция для ввода никнейма
def input_nickname():
    nickname = ''
    input_active = True
    font_style = pygame.font.SysFont("bahnschrift", 25)
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Нажатие Enter завершает ввод
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Удаление символа
                    nickname = nickname[:-1]
                else:
                    nickname += event.unicode  # Добавление символа

        screen.fill(BLUE)
        text_surface = font_style.render(f"Ведите nickname: {nickname}", True, WHITE)
        screen.blit(text_surface, [WIDTH // 6, HEIGHT // 3])
        
        pygame.display.update()

    return nickname

# Основная функция игры
def game_loop(nickname):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Змейка')

    clock = pygame.time.Clock()
    snake = Snake()
    apple = Apple()
    score = 0

    font_style = pygame.font.SysFont("Bad Script", 30)
    font_style1 = pygame.font.SysFont("Bad Script", 22)


    def display_score(score):
        value = font_style.render(f"Score: {score}", True, WHITE)
        screen.blit(value, [0, 0])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                nickname = input_nickname() 
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction('UP')
                elif event.key == pygame.K_DOWN:
                    snake.change_direction('DOWN')
                elif event.key == pygame.K_LEFT:
                   snake.change_direction('LEFT')
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction('RIGHT')

        snake.move()

        # Проверка столкновения с яблоком
        if snake.positions[0] == apple.position:
            snake.grow_snake()
            apple.respawn()
            score += 1  # Увеличиваем счет

        # Проверка столкновения со стенами или собой
        head_x, head_y = snake.positions[0]
        if (head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT or snake.positions[0] in snake.positions[1:]):
            conn = sqlite3.connect('lider.db')
            cursor = conn.cursor()
            # Проверим есть ли такая запись в базе данных, если есть, то ее обновим
            cursor.execute("SELECT nicname FROM Users")

            # добавляем новую запись в таблицу users
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO users (nicname, score) VALUES (?, ?)', (nicname, score))
                cursor.close()
                conn.close()
            else:
                break

        screen.fill(BLUE)
        for pos in snake.positions:
            pygame.draw.rect(screen, GREEN, [pos[0], pos[1], SNAKE_BLOCK, SNAKE_BLOCK])
        
        pygame.draw.rect(screen, RED, [apple.position[0], apple.position[1], SNAKE_BLOCK, SNAKE_BLOCK])
        
        display_score(score)  # Отображаем счет
        
        # Отображаем никнейм
        nickname_surface = font_style.render(f"Nickname: {nickname}", True, WHITE)
        screen.blit(nickname_surface, [100, 0])

        # Отображение лидеров
        conn = sqlite3.connect('lider.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nicname, score FROM Users ORDER BY score DESC')
        results = cursor.fetchall()
        for i in range(5):
             lider_surface = font_style1.render(f": {results[i]}", True, WHITE)
             screen.blit(lider_surface, [600, 18 * i])

        cursor.close()
        conn.close()

        
        pygame.display.update()
        clock.tick(SNAKE_SPEED)

    pygame.quit()

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake Game')
        
    nickname = input_nickname()  # Получаем никнейм
    
    if nickname:  
        game_loop(nickname)
        
