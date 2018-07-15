import pygame
import random
import os

from enum import Enum

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class GameObject(pygame.sprite.Sprite):
    def __init__(self, image_file, position):
        super(GameObject, self).__init__()
        self._image = pygame.image.load(image_file)
        self.rect = self._image.get_rect()
        self.width, self.height = self._image.get_size()
        self.set_position(position)

    def set_position(self, position):
        self.position = position
        self.rect.left, self.rect.top = position

    def get_position(self):
        return self.rect.left, self.rect.top

    def draw(self, screen):
        screen.blit(self._image, (self.rect.left, self.rect.top))


class AnimatedGameObject(pygame.sprite.Sprite):
    def __init__(self, images_path, position, stop_time=0.1, running=False):
        super(AnimatedGameObject, self).__init__()

        self.images = [pygame.image.load(os.path.join(images_path, image_file)) for image_file in sorted(os.listdir(images_path))]
        self.index = 0
        self._image = self.images[self.index] # Start image for animation
        self.rect = self._image.get_rect()
        self.stop_time = stop_time
        self.elapsed_time = 0

        self.set_position(position)
        self.running = running

    def animate(self, dt):
        if not self.running:
            return False

        if self.index + 1 >= len(self.images):
            self.restart_anim()
            return False

        self.elapsed_time += dt
        if self.elapsed_time >= self.stop_time:
            self.elapsed_time = 0
            self.index += 1
            self._image = self.images[self.index]
            self.rect = self._image.get_rect()
            self.set_position(self.position)

        return True

    def set_position(self, position):
        self.position = position
        self.rect.left, self.rect.top = position

    def draw(self, screen):
        screen.blit(self._image, (self.rect.left, self.rect.top))

    def restart_anim(self):
        self.index = 0
        self.running = False


class Background(GameObject):
    def __init__(self, image_file, position=(0, 0)):
        GameObject.__init__(self, image_file, position)

    def draw(self, screen):
        GameScene.SCREEN.fill(WHITE)
        super(Background, self).draw(GameScene.SCREEN)


class Ball(GameObject):
    def __init__(self, image_file, position=(-100, 0), safe=True):
        GameObject.__init__(self, image_file, position)
        self.safe = safe

    def is_inside(self, bucket):
        bucket_x0, bucket_y0 = bucket.rect.left, bucket.rect.top
        bucket_x1 = bucket.rect.right

        ball_x0 = self.rect.left
        ball_x1, ball_y1 = self.rect.right, self.rect.bottom

        if ball_x0 >= bucket_x0 \
                and ball_x1 <= bucket_x1 \
                and ball_y1 - 25 >= bucket_y0 >= ball_y1 - 50:
            return True
        else:
            return False


class Bucket(GameObject):
    def __init__(self, image_file, position):
        GameObject.__init__(self, image_file, position)
        self.x = position[0]
        self.direction = Direction.NONE
        self.dx = 3.8


class BallManager:
    BALL_COUNT = 0
    def __init__(self):
        ball = Ball(image_file='ball_small.png')
        spiky_ball = Ball(image_file='spiky_ball_small.png', safe=False)

        self.balls = [ball, spiky_ball]
        self.ball_weights = {0: 3, 1: 1}
        self.ball_speed = 7
        self.ball_x = 0
        self.ball_y = 0
        self.ball = None

        self.reset_pos()

    def reset_pos(self):
        self.ball_x = random.randrange(0, 460)
        self.ball_y = random.randrange(-600, -200)

    def generate_ball(self):
        BallManager.BALL_COUNT += 1
        self.ball = self.balls[
            random.choice([x for x in self.ball_weights for y in range(self.ball_weights[x])])
        ]
        self.reset_pos()
        self.ball.set_position((self.ball_x, self.ball_y))
        return self.ball

    def update_pos(self):
        self.ball_y += self.ball_speed
        self.ball.set_position((self.ball_x, self.ball_y))

    def get_ball_in_scene(self):
        # Do not change anything here
        if self.ball_y > -20:
            return self.ball
        else:
            return None


class Direction(Enum):
    LEFT = -1
    NONE = 0
    RIGHT = 1


class GameScene:
    SCREEN = None
    FPS = 60

    def __init__(self, width, height):
        GameScene.SCREEN = pygame.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.score = 0
        self.lives = 3
        self.running = False
        self.time_elapsed = 0
        self.bucket = Bucket('bucket_trans.png', (width * 0.45, height * 0.8))
        self.bg = Background('bg.png')
        self.anim = AnimatedGameObject('BallCollectAnim', (-100, 0))
        self.ball_manager = BallManager()
        pygame.display.set_caption('Catch em all!')

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.bucket.direction = Direction.LEFT
                if event.key == pygame.K_RIGHT:
                    self.bucket.direction = Direction.RIGHT

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.bucket.direction = Direction.NONE

    def calculate_direction(self):
        # gets the ball visible on screen
        ball_in_scene = self.ball_manager.get_ball_in_scene()

        # TODO: Write your code here

        # Update self.direction based on ball_in_scene
        # ball_in_scene has attributes like - height, width, rect.top, rect.left
        # So does self.bucket
        # self.bucket.direction = Direction.NONE

    def display_score(self):
        text = self.font.render("Score: {0}".format(self.score), 2, BLACK)
        GameScene.SCREEN.blit(text, (5, 10))

    def display_lives(self):
        text = self.font.render("Lives: {0}".format(self.lives), 2, BLACK)
        GameScene.SCREEN.blit(text, (5, 34))

    def game_loop(self):
        self.running = True

        bucket_x, bucket_y = self.bucket.get_position()
        ball = self.ball_manager.generate_ball()

        while self.running:
            # Comment the below line to stop processing events from the user
            self.process_events()

            self.calculate_direction()

            dt = self.clock.tick(GameScene.FPS)
            self.time_elapsed += dt

            self.bg.draw(GameScene.SCREEN)
            self.ball_manager.update_pos()
            ball.draw(GameScene.SCREEN)

            ball_caught = ball.is_inside(self.bucket)

            if ball_caught:
                if not ball.safe:
                    self.lives -= 1
                else:
                    self.score += 1
                    self.anim.running = True
                    self.anim.set_position((ball.rect.left + ball.width // 2 - 10, self.bucket.rect.top + 5))
                ball = self.ball_manager.generate_ball()
            elif self.ball_manager.ball_y > self.height:
                if ball.safe:
                    self.lives -= 1
                ball = self.ball_manager.generate_ball()

            bucket_new_x = bucket_x + self.bucket.dx * self.bucket.direction.value
            if 0 <= bucket_new_x <= self.width - self.bucket.width:
                bucket_x = bucket_new_x
                self.bucket.set_position((bucket_x, bucket_y))
            self.bucket.draw(GameScene.SCREEN)

            if self.anim.animate(dt / 300):
                self.anim.draw(GameScene.SCREEN)

            self.display_score()
            self.display_lives()

            pygame.display.update()

            if self.lives is 0:
                self.running = False


if __name__ == '__main__':
    scene = GameScene(500, 600)
    scene.game_loop()
    print("Final score: {0}, Total time played: {1} secs, Total balls dropped: {2}"
          .format(scene.score, scene.time_elapsed/1000, BallManager.BALL_COUNT - 1))
    pygame.quit()
    quit()