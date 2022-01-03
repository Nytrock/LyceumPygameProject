import sys

import pygame
import os
import random

types_coords = {'O': ([(0, 0), (-1, 0), (0, 1), (-1, 1)], 1),
                'I': ([(0, 0), (-1, 0), (-2, 0), (1, 0)], 2),
                'S': ([(0, 0), (1, 0), (0, 1), (-1, 1)], 3),
                'Z': ([(0, 0), (-1, 0), (0, 1), (1, 1)], 4),
                'L': ([(0, 0), (-1, 0), (-1, 1), (1, 0)], 5),
                'J': ([(0, 0), (-1, 0), (1, 1), (1, 0)], 6),
                'T': ([(0, 0), (-1, 0), (0, 1), (1, 0)], 7)}
types_rotations = {'O': [[(0, 0), (-1, 0), (0, 1), (-1, 1)]],
                   'I': [[(0, 0), (-1, 0), (-2, 0), (1, 0)], [(0, 0), (0, 1), (0, 2), (0, -1)]],
                   'S': [[(0, 0), (1, 0), (0, 1), (-1, 1)], [(0, 0), (1, 0), (0, -1), (1, 1)]],
                   'Z': [[(0, 0), (-1, 0), (0, 1), (1, 1)], [(0, 0), (1, 0), (1, -1), (0, 1)]],
                   'L': [[(0, 0), (-1, 0), (-1, 1), (1, 0)], [(0, 0), (0, 1), (-1, -1), (0, -1)],
                         [(0, 0), (-1, 0), (1, -1), (1, 0)], [(0, 0), (0, 1), (1, 1), (0, -1)]],
                   'J': [[(0, 0), (-1, 0), (1, 1), (1, 0)], [(0, 0), (0, 1), (-1, 1), (0, -1)],
                         [(0, 0), (-1, 0), (-1, -1), (1, 0)], [(0, 0), (0, 1), (1, -1), (0, -1)]],
                   'T': [[(0, 0), (-1, 0), (0, 1), (1, 0)], [(0, 0), (0, -1), (0, 1), (-1, 0)],
                         [(0, 0), (-1, 0), (0, -1), (1, 0)], [(0, 0), (0, -1), (0, 1), (1, 0)]]}


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

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

    def change_board(self, list_, coords, num):
        x, y = coords
        for i in list_:
            self.board[y + i[1]][x + i[0]] = num

    def scan_down(self, list_, coords):
        free_cubes = []
        for i in list_:
            if (i[0], i[1] + 1) not in list_:
                free_cubes.append(i)
        for i in free_cubes:
            if coords[1] + i[1] + 1 >= len(self.board):
                return False
            if self.board[coords[1] + i[1] + 1][coords[0] + i[0]] != 0:
                return False
        return True

    def scan_up(self, list_, coords):
        free_cubes = []
        for i in list_:
            if (i[0], i[1] - 1) not in list_:
                free_cubes.append(i)
        for i in free_cubes:
            if coords[1] + i[1] - 1 < 4:
                return True
        return False


class Figure:
    def __init__(self, name=""):
        if name == "":
            self.name = random.choice(list(types_coords.keys()))
        else:
            self.name = name
        self.coords, self.color = types_coords[self.name]
        self.sprites = []
        self.x, self.y = 5, 1
        for i in self.coords:
            self.sprites.append(Figure_Sprite(self.name, i, self.x, self.y, board))
        self.Stop = False
        self.num_rotation = 0
        self.update()

    def update(self):
        if board.scan_down(self.coords, (self.x, self.y)):
            board.change_board(self.coords, (self.x, self.y), 0)
            self.y += 1
            board.change_board(self.coords, (self.x, self.y), self.color)
        else:
            self.Stop = True

    def Lose(self):
        if board.scan_up(self.coords, (self.x, self.y)):
            return True
        return False

    def Rotate(self, num):
        if board.scan_down(self.coords, (self.x, self.y)):
            rotations = types_rotations[self.name]
            board.change_board(self.coords, (self.x, self.y), 0)
            self.num_rotation = (self.num_rotation + num) % (len(rotations))
            self.coords = rotations[self.num_rotation]
            board.change_board(self.coords, (self.x, self.y), self.color)

    def Move(self, vector):
        if vector == "down" and board.scan_down(self.coords, (self.x, self.y)):
            board.change_board(self.coords, (self.x, self.y), 0)
            self.y += 1
            board.change_board(self.coords, (self.x, self.y), self.color)

    def In_Next(self):
        self.x, self.y = 2, 0
        self.Stop = False
        board_next.change_board(self.coords, (self.x, self.y), self.color)
        for i in range(len(self.sprites)):
            self.sprites[i].Move(self.coords[i], self.x, self.y, board_next)

    def Out_next(self):
        for i in self.sprites:
            Figures_sprites.remove(i)
        self.sprites.clear()
        for i in self.coords:
            self.sprites.append(Figure_Sprite(self.name, i, self.x, self.y, board))


class Figure_Sprite(Sprite):
    def __init__(self, name, coord, x, y, game_board):
        super().__init__(Figures_sprites)
        self.image = load_image(name + "-block.png")
        self.rect = self.image.get_rect().move(game_board.left + (x + coord[0]) * game_board.cell_size,
                                               game_board.top + (y + coord[1]) * game_board.cell_size)

    def Move(self, coord, x, y, game_board):
        self.rect = self.image.get_rect().move(game_board.left + (x + coord[0]) * game_board.cell_size,
                                               game_board.top + (y + coord[1]) * game_board.cell_size)


def Check_Board():
    num = 0
    sl = {1: 40, 2: 100, 3: 300, 4: 1200}
    for i in range(len(board.board)):
        if 0 not in board.board[i]:
            num += 1
            up = board.board[:i]
            down = board.board[i + 1:]
            board.board = list(map(lambda x: 0, board.board[i])) + up + down
    if num:
        return sl[num]
    return 0


def Create_Archive():
    pass


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["УПРАВЛЕНИЕ", "",
                  "Стрелки влево и вправо - перемещение фигуры влево-вправо",
                  "Стрелка вверх - разворот фигуры по часовой стрелке",
                  "z - разворот фигуры против часовой стрелки",
                  "Стрелка Вниз - опустить фигуру вниз на 1 клетку",
                  "Пробел - опустить фигуру полностью",
                  "Левый Shift - отложить фигуру на хранение"]

    fon = pygame.transform.scale(load_image('Start.jpg'), (800, 950))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('data/F77 Minecraft.ttf', 18)
    text_coord = 350
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 15
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    Figures_sprites = SpriteGroup()
    pygame.init()
    size = (800, 950)
    screen = pygame.display.set_mode(size)
    board = Board(10, 24)
    board.set_view(100, -120, 40)

    board_next = Board(4, 2)
    board_next.set_view(560, 120, 40)

    running = True
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 500)

    start_screen()
    score = 0

    Main_Figure = Figure()
    Archive_Figure = None
    Next_Figure = Figure()
    Next_Figure.In_Next()
    while running:
        font = pygame.font.Font("data/F77 Minecraft.ttf", 23)
        endGame = pygame.font.Font("data/F77 Minecraft.ttf", 47)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.USEREVENT and not Main_Figure.Stop:
                Main_Figure.update()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    Main_Figure.Rotate(1)
                elif event.key == pygame.K_z:
                    Main_Figure.Rotate(-1)
                elif event.key == pygame.K_DOWN:
                    Main_Figure.Move("down")
                elif event.key == pygame.K_LEFT:
                    Main_Figure.Move("left")
                elif event.key == pygame.K_RIGHT:
                    Main_Figure.Move("right")
                elif event.key == pygame.K_LSHIFT:
                    Create_Archive()
        screen.fill((0, 0, 0))
        if Main_Figure.Stop:
            if not Main_Figure.Lose():
                score += Check_Board()
                Main_Figure = Figure(name=Next_Figure.name)
                Next_Figure.Out_next()
                Next_Figure = Figure()
                Next_Figure.In_Next()
                string_rendered = endGame.render("Счёт: " + str(score), True, pygame.Color('white'))
                screen.blit(string_rendered, pygame.Rect(200, 860, 0, 0))
            else:
                string_rendered = endGame.render("Вы проиграли", True, pygame.Color('white'))
                screen.blit(string_rendered, pygame.Rect(100, 860, 0, 0))
        board.test_render(screen)
        pygame.draw.rect(screen, pygame.Color("black"), (0, 0, 700, 40))
        pygame.draw.rect(screen, pygame.Color("white"), (520, 80, 240, 160), width=1)
        pygame.draw.rect(screen, pygame.Color("white"), (520, 360, 240, 200), width=1)
        string_rendered = font.render("Следующая фигура", True, pygame.Color('white'))
        screen.blit(string_rendered, pygame.Rect(520, 40, 0, 0))
        string_rendered = font.render("Карман", True, pygame.Color('white'))
        screen.blit(string_rendered, pygame.Rect(600, 320, 0, 0))
        if not Main_Figure.Stop:
            string_rendered = endGame.render("Счёт: " + str(score), True, pygame.Color('white'))
            screen.blit(string_rendered, pygame.Rect(200, 860, 0, 0))
        Figures_sprites.draw(screen)
        clock.tick(60)
        pygame.display.flip()
    pygame.quit()
