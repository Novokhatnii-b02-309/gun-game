import pygame.draw

from gun_objects import *

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
    bombs = []
    bullets_amount = 10
    points = 0
    gun_health = 100

    gun_image.convert_alpha()
    gun_image_flip.convert_alpha()
    background_image.convert_alpha()
    target_image.convert_alpha()
    bullet_image.convert_alpha()
    bullet_image = pygame.transform.rotozoom(bullet_image, 0, 0.02)
    bomber_image.convert_alpha()
    health_image.convert_alpha()
    health_image = pygame.transform.rotozoom(health_image, 0, 0.02)

    clock = pygame.time.Clock()
    gun = Gun(screen)
    target = Target(screen)
    bomber = Bomber(screen)
    finished = False

    while not finished:
        screen.blit(background_image, (0, 0))
        gun.draw()
        if target.live:
            target.draw()
        if bomber.live:
            bomber.draw()
        for b in balls:
            b.draw()
        for bomb in bombs:
            bomb.draw()

        power_bar = PowerBar(screen, gun.x, gun.y, gun.f2_power)
        pb_ratio = power_bar.ratio()
        pb_color = power_bar.color(pb_ratio)
        power_bar.draw(pb_color, pb_ratio, gun.f2_on)

        gun_health_bar = HealthBar(screen, 55, 17, gun_health, 100, 20)
        ghb_ratio = gun_health_bar.ratio()
        gun_health_bar.draw(ghb_ratio)
        screen.blit(health_image, health_image.get_rect(center=(25, 25)))

        draw_text(screen, 'Your score: ' + str(target.points), 18, WIDTH / 2, 10)
        screen.blit(bullet_image, bullet_image.get_rect(center=(25, 75)))
        draw_text(screen, str(bullets_amount), 25, 55, 65)
        if bullets_amount <= 0 or gun_health <= 0:
            points = max(points, target.points)
            draw_text(screen, 'GAME OVER! YOUR BEST: ' + str(points), 40, WIDTH / 2, HEIGHT / 2 - 110)
            draw_text(screen, 'PRESS R TO RESTART', 40, WIDTH / 2, HEIGHT / 2 - 60)

        pygame.display.update()
        target.move()
        bomber.move(gun)

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN and bullets_amount > 0 and gun_health > 0:
                gun.fire2_start(event)
            elif event.type == pygame.MOUSEBUTTONUP and bullets_amount > 0 and gun_health > 0:
                gun.fire2_end(event, balls, bullet)
                bullets_amount -= 1

        if bombs == []:
            bomber.drop(bombs)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_ESCAPE]:
            finished = True
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
            gun.move(-5)
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
            gun.move(5)
        if (bullets_amount <= 0 or gun_health < 0) and key_pressed[pygame.K_r]:
            bullets_amount = 10
            gun_health = 100
            points = target.points
            target.points = 0
        gun.targetting(gun.get_mouse_position())

        for b in balls:
            b.move()
            if b.hittest(target) and target.live:
                target.live = 0
                target.hit()
                t = pygame.time.get_ticks()
                bullets_amount += 2
            if target.live == 0 and pygame.time.get_ticks() - t >= 1000:
                target.new_target()
            if b.hittest(bomber) and bomber.live:
                bomber.live = 0
                bomber.hit()
                t_b = pygame.time.get_ticks()
                bullets_amount += 2
            if target.live == 0 and pygame.time.get_ticks() - t >= 1000:
                target.new_target()
            if bomber.live == 0 and pygame.time.get_ticks() - t_b >= 1000:
                bomber.new_bomber()
            if abs(b.get_vx()) <= 1e-20:
                balls = balls[1:]
        for bomb in bombs:
            bomb.bomb_move()
            if bomb.hittest(gun):
                gun_health -= 10
                bombs = bombs[1:]
            if abs(bomb.y + bomb.r - (HEIGHT - 15)) <= 1:
                bombs.pop()

        gun.power_up()

pygame.quit()