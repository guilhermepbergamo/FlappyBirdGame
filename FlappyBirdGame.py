import pygame
import os
import random


# screen size
screen_width = 500
screen_height = 800


# game images
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
    ]

# starting the game
pygame.font.init()
POINTS_FONT = pygame.font.SysFont('roboto', 50)


class Bird:
    IMGS = BIRD_IMAGES
    # rotation animations
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.image_count = 0
        self.image = self.IMGS[0]
        
    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y
    
    def move(self):
        # calculate displacement
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.speed * self.time
        
        # constrain displacement
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement
        
        # bird angle
        if displacement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
            else:
                if self.angle > -90:
                    self.angle -= self.ROTATION_SPEED
        
    def draw(self, screen):
        # which bird image will be used
        self.image_count += 1
        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.image_count < self.ANIMATION_TIME*2:
            self.image = self.IMGS[1]
        elif self.image_count < self.ANIMATION_TIME*3:
            self.image = self.IMGS[2]
        elif self.image_count < self.ANIMATION_TIME*4:
            self.image = self.IMGS[1]
        elif self.image_count >= self.ANIMATION_TIME*4 + 1:
            self.image = self.IMGS[0]
            self.image_count = 0
            
        # if the bird is falling -> no wings
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.image_count = self.ANIMATION_TIME*2
            
        # draw image
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        image_center_pos = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_image.get_rect(center=image_center_pos)
        screen.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)
        
        
class Pipe:
    DISTANCE = 200
    SPEED = 5
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.base_pos = 0
        self.top_pipe = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.base_pipe = PIPE_IMAGE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.top_pipe.get_height()
        self.base_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.top_pipe, (self.x, self.top_pos))
        screen.blit(self.base_pipe, (self.x, self.base_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_pipe)
        base_mask = pygame.mask.from_surface(self.base_pipe)
        
        top_distance = (self.x - bird.x, self.top_pos - round(bird.y))
        base_distance = (self.x - bird.x, self.base_pos - round(bird.y))
        
        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)
        
        if base_point or top_point:
            return True
        else:
            return False
        

class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMAGE.get_width()
    IMAGE = FLOOR_IMAGE
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED
        
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)
    
    text = POINTS_FONT.render(f'Score: {points}', True, (255, 255, 255))
    screen.blit(text, (screen_width - 10 - text.get_width(), 10))
    floor.draw(screen)
    pygame.display.update()
    

def main():
    birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((screen_width, screen_height))
    points = 0
    clock = pygame.time.Clock()

    playing = True
    while playing:
        # ingame FPS
        clock.tick(30)
        
        # user interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()
        
        # move things
        for bird in birds:
            bird.move()
        floor.move()
        
        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.top_pipe.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipes:
            pipes.remove(pipe)
                        
        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, floor, points)


if __name__ == '__main__':
    main()
