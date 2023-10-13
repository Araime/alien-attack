from os import path
from random import choice, randint

import pygame


def draw_bg():
    global offset, bg
    speed = 1

    screen.blit(bg, (0, offset))
    screen.blit(bg, (0, offset - screen_height))

    if offset >= screen_height:
        screen.blit(bg, (0, offset - screen_height))
        offset = offset - screen_height

    offset += speed


def create_aliens():
    global rows, cols
    # generate aliens
    for row in range(rows):
        for item in range(cols):
            alien = Alien(100 + item * 100, 150 + row * 70)
            alien_group.add(alien)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# create spaceship class
class Spaceship(pygame.sprite.Sprite):

    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, 'spaceship.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health = health
        self.health_remain = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # set movement speed
        speed = 6

        # set cooldown
        cooldown = 500
        game_over = 0

        # get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        # get current time
        now = pygame.time.get_ticks()

        # shoot
        if key[pygame.K_SPACE] and now - self.last_shot > cooldown:
            laser_snd.play()
            laser = Laser(self.rect.centerx, self.rect.top)
            laser_group.add(laser)
            self.last_shot = now

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.w, 15))
        if self.health_remain > 0:
            pygame.draw.rect(
                screen,
                green,
                (self.rect.x, (self.rect.bottom + 10), int(self.rect.w * (self.health_remain / self.health)), 15)
            )
        elif self.health_remain <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over


# create laser class
class Laser(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, 'laser.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        speed = 5
        self.rect.y -= speed
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion1_snd.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)


# create aliens class
class Alien(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, f'alien{randint(1, 5)}.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter_x = 0
        self.move_direction_x = 1
        self.move_counter_y = 0
        self.move_direction_y = 1

    def update(self):
        # move x direction
        self.rect.x += 1 * self.move_direction_x
        self.move_counter_x += 1
        if abs(self.move_counter_x) > 75:
            self.move_direction_x *= -1
            self.move_counter_x *= self.move_direction_x

        # move y direction
        self.rect.y += 1 * self.move_direction_y
        self.move_counter_y += 1
        if abs(self.move_counter_y) > 90:
            self.move_direction_y *= -1
            self.move_counter_y *= self.move_direction_y


# create alien laser class
class AlineLaser(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_dir, 'alien-laser.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        speed = 4
        self.rect.y += speed
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_snd.play()
            # reduce spaceship health
            spaceship.health_remain -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)


# create explosion class
class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(path.join(img_dir, f'exp{num}.png')).convert_alpha()
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (60, 60))
            # add the image to the list
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3

        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


if __name__ == '__main__':
    pygame.mixer.init()
    pygame.init()

    clock = pygame.time.Clock()
    fps = 60

    screen_width = 600
    screen_height = 800

    # define colours
    red = (255, 0, 0)
    green = (0, 255, 0)
    white = (255, 255, 255)

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Space Invaders')

    # define game variables
    img_dir = path.join(path.dirname(__file__), 'img')
    snd_dir = path.join(path.dirname(__file__), 'snd')
    offset = 0
    rows = 5
    cols = 5
    alien_cooldown = 1000
    last_alien_shot = pygame.time.get_ticks()
    countdown = 3
    last_count = pygame.time.get_ticks()
    game_over = 0  # game on, 1 win, -1 lost

    # define fonts
    font30 = pygame.font.SysFont('Constantia', 30)
    font40 = pygame.font.SysFont('Constantia', 40)

    # load image
    bg = pygame.image.load(path.join(img_dir, 'bg.png')).convert()

    # load sounds
    explosion1_snd = pygame.mixer.Sound(path.join(snd_dir, 'explosion.wav'))
    explosion1_snd.set_volume(0.15)

    explosion2_snd = pygame.mixer.Sound(path.join(snd_dir, 'explosion2.wav'))
    explosion2_snd.set_volume(0.4)

    laser_snd = pygame.mixer.Sound(path.join(snd_dir, 'laser.wav'))
    laser_snd.set_volume(0.1)

    # create sprite groups
    spaceship_group = pygame.sprite.Group()
    laser_group = pygame.sprite.Group()
    alien_group = pygame.sprite.Group()
    alien_laser_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()

    create_aliens()

    # create player
    spaceship = Spaceship(screen_width // 2, screen_height - 100, 3)
    spaceship_group.add(spaceship)

    run = True
    while run:
        clock.tick(fps)

        # draw background
        draw_bg()

        if countdown == 0:

            # create random alien lasers
            now = pygame.time.get_ticks()

            # alien shot
            if now - last_alien_shot > alien_cooldown and len(alien_group) > 0:
                attacking_alien = choice(alien_group.sprites())
                alien_laser = AlineLaser(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
                alien_laser_group.add(alien_laser)
                last_alien_shot = now

            # check if all the aliens have been killed
            if len(alien_group) == 0:
                game_over = 1

            if game_over == 0:
                # update spaceship
                game_over = spaceship.update()

                # update sprite groups
                laser_group.update()
                alien_group.update()
                alien_laser_group.update()
            else:
                if game_over == -1:
                    draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
                if game_over == 1:
                    draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))

        if countdown > 0:
            draw_text('GET READY', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
            draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer

        # update explosion group
        explosion_group.update()

        # draw sprite groups
        spaceship_group.draw(screen)
        laser_group.draw(screen)
        alien_group.draw(screen)
        alien_laser_group.draw(screen)
        explosion_group.draw(screen)

        # events handlers
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.flip()

    pygame.quit()
