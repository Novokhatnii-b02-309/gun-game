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

    gun_image.convert_alpha()
    gun_image_flip.convert_alpha()
    background_image.convert_alpha()
    target_image.convert_alpha()

    clock = pygame.time.Clock()
    gun = Gun(screen)
    target = Target(screen)
    finished = False

    while not finished:
        screen.blit(background_image, (0, 0))
        gun.draw()
        if target.live:
            target.draw()
        draw_text(screen, 'Your score: ' + str(target.points), 18, WIDTH / 2, 10)
        for b in balls:
            b.draw()
        pygame.display.update()
        target.move()

        power_bar = PowerBar(gun.x, gun.y, gun.f2_power)
        pb_ratio = power_bar.ratio()
        pb_color = power_bar.color(pb_ratio)
        power_bar.draw(screen, pb_color, pb_ratio)

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gun.fire2_start(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                gun.fire2_end(event, balls, bullet)

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
