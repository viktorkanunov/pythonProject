import sys
import pygame
import sqlite3

pygame.init()
size = width, height = 1125, 900
tile_size = 75
offset = 75
FPS = 50
PLAYER_UP = pygame.USEREVENT + 1
PLAYER_DOWN = pygame.USEREVENT + 2
PLAYER_LEFT = pygame.USEREVENT + 3
PLAYER_RIGHT = pygame.USEREVENT + 4
time = 0
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
diam_group = pygame.sprite.Group()
score = 0
hit = False
win = False
point = 1000

def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=None):
    fullname = 'pics/' + name
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Невозможно загрузить картинку:', fullname)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


player_image = [load_image('hero.png', -1), load_image('heroleft0.png', -1), load_image('heroleft1.png', -1),
                load_image('heroright0.png', -1), load_image('heroright1.png', -1),
                load_image('heroup.png', -1)]
tile_images = [load_image('background.png', -1), load_image('Town.png', -1),
               load_image('tree.png', -1), load_image('камень.jpg', -1)]
coin_images = [load_image('diamond.png', -1), load_image('background.png', -1)]
diam_images = [load_image('Moteta.png', -1), load_image('diamond_2.png', -1), load_image('diamond_2.png', -1)]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_num, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_num]
        self.rect = self.image.get_rect().move(
            tile_size * pos_x, tile_size * pos_y + offset)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image[0]
        self.rect = self.image.get_rect().move(
            tile_size * pos_x, tile_size * pos_y + offset)
        self.step = 10

    def left(self):
        other = pygame.sprite.spritecollideany(self, tiles_group)
        hits = pygame.sprite.spritecollideany(self, coin_group)
        wins = pygame.sprite.spritecollideany(self, diam_group)
        self.image = player_image[3]
        if hits in coin_group:
            global hit
            hit = True
        if wins in diam_group:
            global win
            win = True
        if not other or other.rect.x > self.rect.x:
            self.rect.x -= self.step

    def right(self):
        other = pygame.sprite.spritecollideany(self, tiles_group)
        hits = pygame.sprite.spritecollideany(self, coin_group)
        wins = pygame.sprite.spritecollideany(self, diam_group)
        self.image = player_image[1]
        if hits in coin_group:
            global hit
            hit = True
        if wins in diam_group:
            global win
            win = True
        if not other or other.rect.x < self.rect.x:
            self.rect.x += self.step

    def up(self):
        other = pygame.sprite.spritecollideany(self, tiles_group)
        hits = pygame.sprite.spritecollideany(self, coin_group)
        wins = pygame.sprite.spritecollideany(self, diam_group)
        self.image = player_image[5]
        if hits in coin_group:
            global hit
            hit = True
        if wins in diam_group:
            global win
            win = True
        if not other or other.rect.y > self.rect.y:
            self.rect.y -= self.step

    def down(self):
        other = pygame.sprite.spritecollideany(self, tiles_group)
        hits = pygame.sprite.spritecollideany(self, coin_group)
        wins = pygame.sprite.spritecollideany(self, diam_group)
        self.image = player_image[0]
        if hits in coin_group:
            global hit
            hit = True
        if wins in diam_group:
            global win
            win = True
        if not other or other.rect.y < self.rect.y:
            self.rect.y += self.step


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(coin_group, all_sprites)
        self.image = coin_images[0]
        self.rect = self.image.get_rect().move(
            tile_size * pos_x, tile_size * pos_y + offset)


class Diam(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(diam_group, all_sprites)
        self.image = diam_images[0]
        self.rect = self.image.get_rect().move(
            tile_size * pos_x, tile_size * pos_y + offset)
        self.an = 0
        self.l_upd = pygame.time.get_ticks()
        self.fr_r = 15

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.l_upd > self.fr_r:
            self.l_upd = now
            self.an += 1
            if self.an == len(diam_images):
                self.an = 0
            self.image = diam_images[self.an]


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def load_level(screen, level_num):
    tile_type = {'.': 0, 'X': 1, 'T': 2, '$': 3, '@': 10, '!': 5, '%': 4}
    player, x, y = None, None, None
    coin, x, y = None, None, None
    diam, x, y = None, None, None
    all_sprites.empty()
    tiles_group.empty()
    player_group.empty()
    coin_group.empty()
    filename = f"data/level_{level_num:02d}.txt"
    with open(filename, 'r') as mapFile:
        level = [[tile_type[s] for s in line.strip()] for line in mapFile]
    for y in range(len(level)):
        for x in range(len(level[y])):
            screen.blit(tile_images[0], (tile_size * x, tile_size * y + offset))
            if level[y][x] == 10:
                player = Player(x, y)
            elif level[y][x] == 4:
                diam = Diam(x, y)
            elif level[y][x] == 5:
                coin = Coin(x, y)
            elif level[y][x]:
                Tile(level[y][x], x, y)
    return player, coin, diam, len(level[0]), len(level)


def draw_level(screen):
    screen.fill('darkgreen')
    for y in range(level_size_y):
        for x in range(level_size_x):
            screen.blit(tile_images[0], (tile_size * x, tile_size * y + offset))


def start_screen():
    intro_text = ["Правила игры",
                  "Клавиши со стрелками перемещают героя,",
                  "Ваша задача собрать все бонусы"]

    load_level(screen, 0)
    tiles_group.draw(screen)
    font30 = pygame.font.Font(None, 30)
    font90 = pygame.font.Font(None, 90)
    string_rendered = font90.render('', 1, 'yellow')
    rect = string_rendered.get_rect()
    rect.centerx = width // 2
    rect.y = 10
    screen.blit(string_rendered, rect)
    text_coord = offset + 130
    for line in intro_text:
        string_rendered = font30.render(line, 1, pygame.Color('black'))
        rect = string_rendered.get_rect()
        text_coord += 10
        rect.top = text_coord
        rect.centerx = width // 2
        text_coord += rect.height
        screen.blit(string_rendered, rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
con = sqlite3.connect("calcul.db")
cur = con.cursor()
camera = Camera()
running = True
sc = True
if not hit:
    player, coin, diam, level_size_x, level_size_y = load_level(screen, 1)

while running:
    time += 1
    if sc:
        point -= 1
    print(win)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == PLAYER_LEFT:
            player.left()
        if event.type == PLAYER_RIGHT:
            player.right()
        if event.type == PLAYER_UP:
            player.up()
        if event.type == PLAYER_DOWN:
            player.down()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.left()
                pygame.time.set_timer(PLAYER_LEFT, 50)
            elif event.key == pygame.K_RIGHT:
                player.right()
                pygame.time.set_timer(PLAYER_RIGHT, 50)
            elif event.key == pygame.K_UP:
                player.up()
                pygame.time.set_timer(PLAYER_UP, 50)
            elif event.key == pygame.K_DOWN:
                player.down()
                pygame.time.set_timer(PLAYER_DOWN, 50)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                pygame.time.set_timer(PLAYER_LEFT, 0)
            elif event.key == pygame.K_RIGHT:
                pygame.time.set_timer(PLAYER_RIGHT, 0)
            elif event.key == pygame.K_UP:
                pygame.time.set_timer(PLAYER_UP, 0)
            elif event.key == pygame.K_DOWN:
                pygame.time.set_timer(PLAYER_DOWN, 0)
    if hit:
        player, coin, diam, level_size_x, level_size_y = load_level(screen, 2)
        hit = False
    for sprite in all_sprites:
        camera.apply(sprite)
    draw_level(screen)
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(15)
    if win:
        load_level(screen, 0)
        sc = False
        cur.execute('INSERT INTO results VALUES(?,?)', (None, time)).fetchall()
        con.commit()
        con = sqlite3.connect("calcul.db")
        cur = con.cursor()
        result = cur.execute('''SELECT hist FROM results''').fetchall()
        cur.execute('''DELETE FROM results''').fetchall()
        cur.execute('INSERT INTO results VALUES(?,?)', (None, time + result[0][0])).fetchall()
        con.commit()
        con = sqlite3.connect("calcul.db")
        cur = con.cursor()
        result1 = cur.execute('''SELECT hist FROM results''').fetchall()
        font = pygame.font.Font(None, 36)
        text = font.render(f"Вы набрали {point} очков", True, (255, 255, 255))
        rect = text.get_rect()
        font1 = pygame.font.Font(None, 36)
        text1 = font1.render(f"Вы набрали {point} очков", True, (255, 255, 255))
        rect1 = text1.get_rect()
        screen.blit(text, (100, 100), rect)
        screen.blit(text1, (150, 150), rect1)
        pygame.display.flip()
    camera.update(player)
pygame.quit()
