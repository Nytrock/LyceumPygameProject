import sys
from math import sqrt

import pygame
import os
import random

# Константы
types_coordinates = {"O": ([(0, 0), (-1, 0), (0, 1), (-1, 1)], 1),
                     "I": ([(0, 0), (-1, 0), (-2, 0), (1, 0)], 2),
                     "S": ([(0, 0), (1, 0), (0, 1), (-1, 1)], 3),
                     "Z": ([(0, 0), (-1, 0), (0, 1), (1, 1)], 4),
                     "L": ([(0, 0), (-1, 0), (-1, 1), (1, 0)], 5),
                     "J": ([(0, 0), (-1, 0), (1, 1), (1, 0)], 6),
                     "T": ([(0, 0), (-1, 0), (0, 1), (1, 0)], 7)}
types_rotations = {"O": [[(0, 0), (-1, 0), (0, 1), (-1, 1)]],
                   "I": [[(0, 0), (-1, 0), (-2, 0), (1, 0)], [(0, 0), (0, 1), (0, 2), (0, -1)]],
                   "S": [[(0, 0), (1, 0), (0, 1), (-1, 1)], [(0, 0), (1, 0), (0, -1), (1, 1)]],
                   "Z": [[(0, 0), (-1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (1, -1), (0, 1)]],
                   "L": [[(0, 0), (-1, 0), (-1, 1), (1, 0)], [(0, 0), (0, 1), (-1, -1), (0, -1)],
                         [(0, 0), (-1, 0), (1, -1), (1, 0)], [(0, 0), (0, 1), (1, 1), (0, -1)]],
                   "J": [[(0, 0), (-1, 0), (1, 1), (1, 0)], [(0, 0), (0, 1), (-1, 1), (0, -1)],
                         [(0, 0), (-1, 0), (-1, -1), (1, 0)], [(0, 0), (0, 1), (1, -1), (0, -1)]],
                   "T": [[(0, 0), (-1, 0), (0, 1), (1, 0)], [(0, 0), (0, -1), (0, 1), (-1, 0)],
                         [(0, 0), (-1, 0), (0, -1), (1, 0)], [(0, 0), (0, -1), (0, 1), (1, 0)]]}


# Стандартный класс
def load_image(name, color_key=None):
    fullname = os.path.join("data/img", name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Не удаётся загрузить:", name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


# Стандартный класс
class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, even):
        for sprite in self:
            sprite.get_event(even)


# Стандартный класс
class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, even):
        pass


# Поле
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, topi, cell_size):
        self.left = left
        self.top = topi
        self.cell_size = cell_size

    # Тестовый рендер
    def test_render(self, scree):
        colors = [pygame.Color("Black"), pygame.Color("Yellow"), pygame.Color("Cyan"), pygame.Color("Green"),
                  pygame.Color("Red"), pygame.Color("Orange"), pygame.Color("Blue"), pygame.Color("Purple")]
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(scree, colors[self.board[y][x]], (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size))
                pygame.draw.rect(scree, pygame.Color("white"), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)

    # Изменение положения фигуры
    def change_board(self, list_, coordinates, number):
        x, y = coordinates
        for elem in list_:
            self.board[y + elem[1]][x + elem[0]] = number

    # Проверка свободы внизу
    def scan_down(self, list_, coordinates):
        free_cubes = []
        for elem in list_:
            if (elem[0], elem[1] + 1) not in list_:
                free_cubes.append(elem)
        for elem in free_cubes:
            if coordinates[1] + elem[1] + 1 >= len(self.board):
                return False
            if self.board[coordinates[1] + elem[1] + 1][coordinates[0] + elem[0]] != 0:
                return False
        return True

    # Проверка того, не выходит ли фигура за пределы поля
    @staticmethod
    def scan_up(list_, coordinates):
        free_cubes = []
        for elem in list_:
            if (elem[0], elem[1] - 1) not in list_:
                free_cubes.append(elem)
        for elem in free_cubes:
            if coordinates[1] + elem[1] - 1 < 3:
                return True
        return False

    # Может ли фигура вращаться
    def Check_Rotate(self, list_, coordinates, number):
        for elem in list_:
            if 0 <= coordinates[1] + elem[1] <= len(self.board) - 1 and \
                    0 <= coordinates[0] + elem[0] <= len(self.board[0]) - 1:
                if self.board[coordinates[1] + elem[1]][coordinates[0] + elem[0]] != 0 and \
                        self.board[coordinates[1] + elem[1]][coordinates[0] + elem[0]] != number:
                    return False
            else:
                return False
        return True

    # Проверка свободы слева
    def Scan_Left(self, list_, coordinates):
        for elem in list_:
            if coordinates[0] + elem[0] - 1 < 0:
                return False
            if (elem[0] - 1, elem[1]) not in list_ and \
                    self.board[coordinates[1] + elem[1]][coordinates[0] + elem[0] - 1] != 0:
                return False
        return True

    # проверка свободы справа
    def Scan_Right(self, list_, coordinates):
        for elem in list_:
            if coordinates[0] + elem[0] + 1 >= len(self.board[0]):
                return False
            if (elem[0] + 1, elem[1]) not in list_ and \
                    self.board[coordinates[1] + elem[1]][coordinates[0] + elem[0] + 1] != 0:
                return False
        return True


# Фигура
class Figure:
    def __init__(self, name="", Next=False, Archive=False):
        if name == "":
            self.name = random.choice(list(types_coordinates.keys()))
        else:
            self.name = name
        self.dx = 0
        self.coordinates, self.color = types_coordinates[self.name]
        self.sprites = []
        self.Stop = False
        self.num_rotation = 0
        if not Next and not Archive:
            self.x, self.y = 5, 1
            for elem in self.coordinates:
                self.sprites.append(Figure_Sprite(self.name, elem, self.x, self.y, board))
            self.update()
        elif Next:
            self.x, self.y = 2, 0
            for elem in self.coordinates:
                self.sprites.append(Figure_Sprite(self.name, elem, self.x, self.y, board))
            board_next.change_board(self.coordinates, (self.x, self.y), self.color)
            for elem in range(len(self.sprites)):
                self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board_next)
                self.sprites[elem].image = pygame.transform.scale(self.sprites[elem].image, (35, 35))
        elif Archive:
            self.x, self.y = 2, 0
            for elem in self.coordinates:
                self.sprites.append(Figure_Sprite(self.name, elem, self.x, self.y, board))
            board_arch.change_board(self.coordinates, (self.x, self.y), self.color)
            for elem in range(len(self.sprites)):
                self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board_arch)
                self.sprites[elem].image = pygame.transform.scale(self.sprites[elem].image, (35, 35))

    # Движение вниз
    def update(self):
        if board.scan_down(self.coordinates, (self.x, self.y)):
            board.change_board(self.coordinates, (self.x, self.y), 0)
            self.y += 1
            for elem in range(len(self.sprites)):
                self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board)
            board.change_board(self.coordinates, (self.x, self.y), self.color)
        else:
            self.Stop = True

    # Проверка проигрыша
    def Lose(self):
        if board.scan_up(self.coordinates, (self.x, self.y)):
            return True
        return False

    # Поворот
    def Rotate(self, number):
        if board.scan_down(self.coordinates, (self.x, self.y)):
            rotations = types_rotations[self.name]
            self.num_rotation = (self.num_rotation + number) % (len(rotations))
            if board.Check_Rotate(rotations[self.num_rotation], (self.x, self.y), self.color):
                board.change_board(self.coordinates, (self.x, self.y), 0)
                self.coordinates = rotations[self.num_rotation]
                board.change_board(self.coordinates, (self.x, self.y), self.color)
                for elem in range(len(self.sprites)):
                    self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board)

    # Движение влево-вправо
    def Move(self, vector):
        if vector == "left" and board.Scan_Left(self.coordinates, (self.x, self.y)):
            board.change_board(self.coordinates, (self.x, self.y), 0)
            self.x -= 1
            board.change_board(self.coordinates, (self.x, self.y), self.color)
        elif vector == "right" and board.Scan_Right(self.coordinates, (self.x, self.y)):
            board.change_board(self.coordinates, (self.x, self.y), 0)
            self.x += 1
            board.change_board(self.coordinates, (self.x, self.y), self.color)
        for elem in range(len(self.sprites)):
            self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board)

    # Мгновенное движение вниз
    def Down(self):
        number = 0
        while board.scan_down(self.coordinates, (self.x, self.y)):
            board.change_board(self.coordinates, (self.x, self.y), 0)
            self.y += 1
            board.change_board(self.coordinates, (self.x, self.y), self.color)
            number += 1
        for elem in range(len(self.sprites)):
            self.sprites[elem].Move(self.coordinates[elem], self.x, self.y, board)
        return number

    # Удаление фигуры из окна показа следующего
    def Out_next(self):
        for elem in self.sprites:
            Figures_sprites.remove(elem)
        self.sprites.clear()


# Спрайт фигуры
class Figure_Sprite(Sprite):
    def __init__(self, name, coord, x, y, game_board):
        super().__init__(Figures_sprites)
        self.image = pygame.transform.scale(load_image(name + "-block.png"), (42, 42))
        self.rect = self.image.get_rect().move(game_board.left + (x + coord[0]) * game_board.cell_size,
                                               game_board.top + (y + coord[1]) * game_board.cell_size)

    # Движение за фигурой
    def Move(self, coord, x, y, game_board):
        self.rect = self.image.get_rect().move(game_board.left + (x + coord[0]) * game_board.cell_size,
                                               game_board.top + (y + coord[1]) * game_board.cell_size)


# Проверка заполненности линий
def Check_Board():
    number = []
    for elem in range(len(board.board)):
        if 0 not in board.board[elem]:
            number.append(elem)
            up = board.board[:elem]
            down = board.board[elem + 1:]
            board.board = [list(map(lambda x: 0, board.board[elem]))] + up + down
    if number:
        return number
    return []


# Выйти из стартового экрана
def terminate():
    pygame.quit()
    sys.exit()


# Стартовый экран
def start_screen():
    intro_text = ["                               УПРАВЛЕНИЕ", "",
                  "Стрелки влево и вправо - перемещение фигуры ",
                  "влево-вправо",
                  "Стрелка вверх - разворот фигуры по часовой стрелке",
                  "z - разворот фигуры против часовой стрелки",
                  "Стрелка Вниз - опустить фигуру вниз на 1 клетку",
                  "Пробел - опустить фигуру полностью",
                  "Левый Shift - отложить фигуру на хранение",
                  "Q - увеличить скорость игры",
                  "",
                  "               Для начала игры нажми любую кнопку           "]

    background_image = pygame.transform.scale(load_image("Start.jpg"), (590, 960))
    screen.blit(background_image, (0, 0))
    Font = pygame.font.Font("data/fonts/Start.ttf", 15)
    text_coord = 60
    for line in intro_text:
        string_render = Font.render(line, True, (220, 236, 174))
        intro_rect = string_render.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_render, intro_rect)

    while True:
        for even in pygame.event.get():
            if even.type == pygame.QUIT:
                terminate()
            elif even.type == pygame.KEYDOWN or \
                    even.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(60)


# Очистка спрайтов
def New_game():
    for sprite in Figures_sprites:
        Figures_sprites.remove(sprite)


# Кодирование лучшего счёта
def Code(n):
    n *= 84674
    n /= 4
    n **= 2
    return int(n)


# Декодирование лучшего счёта
def Decode(n):
    n = sqrt(n)
    n *= 4
    n /= 84674
    return int(n)


# Основа
if __name__ == "__main__":
    # Создание экрана и основных полей
    Figures_sprites = SpriteGroup()
    pygame.init()
    size = (590, 960)
    screen = pygame.display.set_mode(size)
    board = Board(10, 24)
    board.set_view(15, -40, 41)

    board_next = Board(4, 2)
    board_next.set_view(435, 200, 34)

    board_arch = Board(4, 2)
    board_arch.set_view(435, 370, 34)

    # Создаем собственный таймер на скорость игры
    running = True
    clock = pygame.time.Clock()
    FPS = 450
    pygame.time.set_timer(pygame.USEREVENT, FPS)
    # Стартовый экран
    start_screen()
    # Звуки
    pygame.mixer.music.load("data/audio/Background.mp3")
    pygame.mixer.music.play(loops=-1)
    pygame.mixer.music.set_volume(0.1)
    sound1 = pygame.mixer.Sound("data/audio/BlockFall.mp3")
    sound1.set_volume(0.5)
    sound2 = pygame.mixer.Sound("data/audio/LineClear.mp3")
    sound2.set_volume(0.5)
    BackMusic = True

    # Настройка счёта, архива и загрузка изображений
    score = 0
    file = open("Score.txt", "r", encoding="utf-8")
    num = int(file.readline())
    decoded_num = Decode(num)
    BestScore = decoded_num
    archive_value = 0
    level = 1
    Arch = True
    sl = {1: 40, 2: 100, 3: 300, 4: 1200}
    flyDown = False
    flyRight = False
    flyLeft = False
    background = load_image("Background.jpg")
    top = load_image("Top.png")
    # Создание стартовых фигур
    Main_Figure = Figure()
    Archive_Figure = None
    Next_Figure = Figure(Next=True)
    while running:
        font = pygame.font.Font("data/fonts/Font.ttf", 23)
        endGame = pygame.font.Font("data/fonts/Font.ttf", 23)
        for event in pygame.event.get():
            # Выход из игры
            if event.type == pygame.QUIT:
                running = False
            # Обновление поля
            if event.type == pygame.USEREVENT and not Main_Figure.Stop:
                Main_Figure.update()
                if flyLeft:
                    Main_Figure.Move("left")
                if flyRight:
                    Main_Figure.Move("right")
            elif event.type == pygame.KEYDOWN:
                # Если игра не закончилась
                if BackMusic:
                    # Поворот фигуры
                    if event.key == pygame.K_UP:
                        Main_Figure.Rotate(1)
                    # Ускорение игры
                    elif event.key == pygame.K_q:
                        if level < 16:
                            level += 1
                            FPS -= 25
                            pygame.time.set_timer(pygame.USEREVENT, FPS)
                    # Поворот фигуры
                    elif event.key == pygame.K_z:
                        Main_Figure.Rotate(-1)
                    # Мгновенный спуск
                    elif event.key == pygame.K_SPACE:
                        Main_Figure.Down()
                        Arch = True
                    # Движение влево
                    elif event.key == pygame.K_LEFT:
                        Main_Figure.Move("left")
                        flyLeft = True
                    # Движение вправо
                    elif event.key == pygame.K_RIGHT:
                        Main_Figure.Move("right")
                        flyRight = True
                    # Архив
                    elif event.key == pygame.K_LSHIFT and Arch:
                        if archive_value == 0:
                            Archive_Figure = Figure(name=Main_Figure.name, Archive=True)
                            board.change_board(Main_Figure.coordinates, (Main_Figure.x, Main_Figure.y), 0)
                            Main_Figure.Out_next()
                            Main_Figure = Figure(name=Next_Figure.name)
                            Next_Figure.Out_next()
                            Next_Figure = Figure(Next=True)
                        elif archive_value == 1:
                            board.change_board(Main_Figure.coordinates, (Main_Figure.x, Main_Figure.y), 0)
                            Main_Figure.Out_next()
                            Archive_Figure.Out_next()
                            Main_Figure, Archive_Figure = Figure(name=Archive_Figure.name), \
                                                          Figure(name=Main_Figure.name, Archive=True)
                        archive_value = 1
                        Arch = False
                    # Спуск вниз
                    elif event.key == pygame.K_DOWN:
                        flyDown = True
                else:
                    # Начало новой игры
                    New_game()
                    pygame.mixer.music.load("data/audio/Background.mp3")
                    pygame.mixer.music.play(loops=-1)
                    pygame.mixer.music.set_volume(0.1)
                    board = Board(10, 24)
                    board.set_view(15, -40, 41)
                    board_next = Board(4, 2)
                    board_next.set_view(435, 200, 34)
                    board_arch = Board(4, 2)
                    board_arch.set_view(435, 370, 34)
                    score = 0
                    BackMusic = True
                    Main_Figure = Figure()
                    Archive_Figure = None
                    Next_Figure = Figure(Next=True)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    flyDown = False
                elif event.key == pygame.K_LEFT:
                    flyLeft = False
                elif event.key == pygame.K_RIGHT:
                    flyRight = False
        screen.blit(background, (0, 0))
        if flyDown:
            if board.scan_down(Main_Figure.coordinates, (Main_Figure.x, Main_Figure.y)):
                clock.tick(20)
                board.change_board(Main_Figure.coordinates, (Main_Figure.x, Main_Figure.y), 0)
                Main_Figure.y += 1
                board.change_board(Main_Figure.coordinates, (Main_Figure.x, Main_Figure.y), Main_Figure.color)
                for i in range(len(Main_Figure.sprites)):
                    Main_Figure.sprites[i].Move(Main_Figure.coordinates[i], Main_Figure.x, Main_Figure.y, board)
        # Отображение текста
        string_rendered = endGame.render(str(score), True, (254, 236, 174))
        screen.blit(string_rendered, pygame.Rect(535, 98, 0, 0))
        string_rendered = endGame.render(str(level), True, (254, 236, 174))
        screen.blit(string_rendered, pygame.Rect(535, 484, 0, 0))
        Figures_sprites.draw(screen)
        screen.blit(top, (0, 0))
        # При остановке фигуры
        if Main_Figure.Stop:
            if BackMusic:
                sound1.play()
            if not Main_Figure.Lose():
                new_score = Check_Board()
                Arch = True
                if new_score:
                    sound2.play()
                    score += sl[len(new_score)] * level
                    for i in Figures_sprites:
                        if (i.rect.y - board.top) // 41 in new_score:
                            Figures_sprites.remove(i)
                        elif (i.rect.y - board.top) // 41 < max(new_score):
                            if Archive_Figure is not None:
                                if i in Archive_Figure.sprites:
                                    continue
                            i.rect = pygame.Rect(i.rect.x, i.rect.y + 41 * len(new_score), 42, 42)
                Main_Figure = Figure(name=Next_Figure.name)
                Next_Figure.Out_next()
                Next_Figure = Figure(Next=True)
            else:
                # Конец игры
                if score > BestScore:
                    open("Score.txt", "w").close()
                    file = open("Score.txt", "w", encoding="utf-8")
                    file.write(str(Code(score)))
                    BestScore = score
                if BackMusic:
                    pygame.mixer.music.load("data/audio/Game Over.mp3")
                    pygame.mixer.music.play(loops=-1)
                    pygame.mixer.music.set_volume(0.1)
                    BackMusic = False
                fon = pygame.transform.scale(load_image("Start.jpg"), (590, 960))
                screen.blit(fon, (0, 0))
                endGame = pygame.font.Font("data/fonts/Font.ttf", 116)
                string_rendered = endGame.render("You Lose",
                                                 True, (254, 236, 174))
                screen.blit(string_rendered, pygame.Rect(0, 100, 0, 0))
                endGame = pygame.font.Font("data/fonts/Font.ttf", 58)
                string_rendered = endGame.render("Score: " + str(score),
                                                 True, (220, 236, 174))
                screen.blit(string_rendered, pygame.Rect(130, 250, 0, 0))
                endGame = pygame.font.Font("data/fonts/Font.ttf", 48)
                string_rendered = endGame.render("Best Score: " + str(BestScore),
                                                 True, (220, 236, 174))
                screen.blit(string_rendered, pygame.Rect(90, 350, 0, 0))
                endGame = pygame.font.Font("data/fonts/Font.ttf", 30)
                string_rendered = endGame.render("For new game press any button",
                                                 True, (220, 236, 174))
                screen.blit(string_rendered, pygame.Rect(20, 920, 0, 0))
        clock.tick(60)
        pygame.display.flip()
    pygame.quit()
