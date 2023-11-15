import math
from random import choice, randrange

import pygame


FPS = 40

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]
g = 1

WIDTH = 800
HEIGHT = 600
GUN_X = 100
GUN_Y = 450

class Ball:
    def __init__(self, screen: pygame.Surface, x=GUN_X, y=GUN_Y):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 15
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """

        # описание столкновения с левой и правой границами
        if self.x + self.r > WIDTH or self.x - self.r < 0:
            self.vx = -self.vx * 0.5
            self.vy *= 0.5
            self.x += self.vx

        # описание столкновения с верхней и нижней границами
        if self.y + self.r > HEIGHT - 15 or self.y - self.r < 0:
            self.vy = -self.vy * 0.5
            self.vx *= 0.5
            if abs(self.vx) >= 0.5:
                self.y -= self.vy
        if abs(self.vx) >= 1e-2:
            self.x += self.vx
            self.y -= self.vy
            self.vy -= g

    def get_vx(self):
        return self.vx

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Объект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if obj.x - obj.r <= self.x <= obj.x + obj.r and obj.y - obj.r <= self.y <= obj.y + obj.r:
            return True
        return False

class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.x = GUN_X + 100
        self.y = GUN_Y
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.original_image = gun_image
        self.image = pygame.transform.rotate(self.original_image, self.an)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, x=self.x)
        self.an = math.degrees(math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x)))
        new_ball.vx = self.f2_power * math.cos(math.radians(self.an))
        new_ball.vy = -self.f2_power * math.sin(math.radians(self.an))
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    # ищем координаты мышки
    def get_mouse_position(self):
        return [pygame.mouse.get_pos()[0] - self.x, pygame.mouse.get_pos()[1] - self.y]

    def targetting(self, position):
        """Прицеливание. Зависит от положения мыши."""
        # координаты мышки
        x_pos = position[0]
        y_pos = position[1]

        # чтобы не возникало деления на 0, описываем отдельно случай, когда мышка над ружьём
        if x_pos != 0:
            ratio = y_pos / x_pos
            if x_pos > 0:
                self.original_image = gun_image
            else:
                self.original_image = gun_image_flip
            self.an = math.degrees(math.atan(ratio))
        elif x_pos == 0:
            if y_pos > 0:
                self.original_image = gun_image
            if y_pos < 0:
                self.original_image = gun_image_flip
            self.an = 90
        else:
            self.an = 0

        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        self.image = pygame.transform.rotate(self.original_image, -self.an)
        self.screen.blit(self.image, self.rect)

    def move(self, add_x):
        if 0 <= self.x <= WIDTH:
            self.x += add_x
            self.rect.center = (self.x, self.y)
        elif self.x <= 0 and add_x > 0:
            self.x += add_x
            self.rect.center = (self.x, self.y)
        elif self.x >= WIDTH and add_x < 0:
            self.x += add_x
            self.rect.center = (self.x, self.y)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY


class Target:
    def __init__(self, screen):
        """ Инициализация новой цели. """
        self.screen = screen
        self.points = 0
        self.live = 1
        self.x = randrange(600, 780)
        self.y = randrange(300, 550)
        self.r = randrange(10, 50)
        self.color = RED
        self.original_image = target_image
        self.image = pygame.transform.rotozoom(self.original_image, 0, self.r / 2000)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def new_target(self):
        """ Инициализация новой цели. """
        self.live = 1
        self.x = randrange(600, 780)
        self.y = randrange(300, 550)
        self.r = randrange(10, 50)
        self.color = RED
        self.original_image = target_image
        self.image = pygame.transform.rotozoom(self.original_image, 0, self.r / 2000)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def hit(self, add=1):
        """Попадание шарика в цель."""
        self.points += add

    def draw(self):
        pygame.transform.rotozoom(self.original_image, 0, self.r / 2000)
        self.screen.blit(self.image, self.rect)

# функция для отрисовки набранных очков на экране
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    bullet = 0
    balls = []

    gun_image = pygame.image.load("gun-40(2).png").convert_alpha()
    gun_image_flip = pygame.image.load("gun-40(rot).png").convert_alpha()
    background_image = pygame.image.load("background.jpg").convert_alpha()
    target_image = pygame.image.load("target.png").convert_alpha()

    clock = pygame.time.Clock()
    gun = Gun(screen)
    target = Target(screen)
    finished = False

    while not finished:
        screen.blit(background_image, (0, 0))
        gun.draw()
        if target.live:
            target.draw()
        draw_text(screen, 'Your score:' + str(target.points), 18, WIDTH / 2, 10)
        for b in balls:
            b.draw()
        pygame.display.update()

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gun.fire2_start(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                gun.fire2_end(event)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_ESCAPE]:
            finished = True
        if key_pressed[pygame.K_LEFT]:
            gun.move(-5)
        if key_pressed[pygame.K_RIGHT]:
            gun.move(5)
        gun.targetting(gun.get_mouse_position())

        for b in balls:
            b.move()
            if b.hittest(target) and target.live:
                target.live = 0
                target.hit()
                t = pygame.time.get_ticks()
            if target.live == 0 and pygame.time.get_ticks() - t >= 1000:
                target.new_target()
            if abs(b.get_vx()) <= 1e-20:
                balls = balls[1:]
        gun.power_up()

pygame.quit()
