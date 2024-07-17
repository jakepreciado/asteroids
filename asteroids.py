from tkinter import CENTER
import arcade
from abc import ABC, abstractmethod
import random
import math

# These are Global constants to use throughout the game
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

BULLET_RADIUS = 30
BULLET_SPEED = 10
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.25
SHIP_RADIUS = 30

INITIAL_ROCK_COUNT = 5

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MEDIUM_ROCK_SPIN = -2
MEDIUM_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2

RENDER = 255

class Point:
    """
    A base class that initializes the position of objects in the game. 
    """
    def __init__(self):
        self.x = 0
        self.y = 0

       
class Velocity:
    """
    A base class that initializes the velocity of objects in the game.
    """
    def __init__(self):
        self.dx = 0
        self.dy = 0


class FlyingObjects(ABC):
    """ 
    A base class for any flying object in the game. 
    """
    def __init__(self, img):
        self.center = Point()
        self.velocity = Velocity()
        self.alive = True
        self.radius = 0
        self.angle = 0
        self.speed = 0
        self.direction = 1
        self.velocity.dx += math.cos(math.radians(self.direction)) * self.speed
        self.velocity.dy -= math.sin(math.radians(self.direction)) * self.speed
        self.image = img
        self.texture = arcade.load_texture(self.image)
        self.width = self.texture.width
        self.height = self.texture.height

    def advance(self):
        self.wrap()
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy

    def is_alive(self):
        return self.alive

    @abstractmethod
    def draw(self):
        pass

    """ Objects can wrap around and cross edges of the screen through this function. """
    def wrap(self):
        if self.center.x > SCREEN_WIDTH:
            self.center.x = 0
        if self.center.x < 0:
            self.center.x = SCREEN_WIDTH
        if self.center.y > SCREEN_HEIGHT:
            self.center.y = 0
        if self.center.y < 0:
            self.center.y = SCREEN_HEIGHT


class Ship(FlyingObjects):
    """ 
    Class used to create our ship. Inherited from FlyingObjects class.
    """
    def __init__(self):
        super().__init__('images/arwing_base.png')
        self.center.x = SCREEN_WIDTH / 2
        self.center.y = SCREEN_HEIGHT / 2
        self.radius = SHIP_RADIUS

    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height,
                                      self.texture, self.angle, RENDER)

    """ Below methods control the movements of the ship. """
    def left(self):
        self.angle += SHIP_TURN_AMOUNT

    def right(self):
        self.angle -= SHIP_TURN_AMOUNT

    def thrust(self):
        self.velocity.dx -= math.sin(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        self.velocity.dy += math.cos(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        return self.velocity.dx, self.velocity.dy

    def reverse(self):
        self.velocity.dx += math.sin(math.radians(self.angle)) * SHIP_THRUST_AMOUNT
        self.velocity.dy -= math.cos(math.radians(self.angle)) * SHIP_THRUST_AMOUNT


class Bullets(FlyingObjects):
    """ 
    Sets the conditions and creates the bullets fired from the ship. 
    """
    def __init__(self, angle, x, y):
        super().__init__('images/laserBlue01.png')
        self.speed = BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.life = BULLET_LIFE
        self.angle = angle
        self.center.x = x
        self.center.y = y

    def fire(self, ship_speed):
        self.velocity.dx = (math.cos(math.radians(self.angle + 90)) * self.speed) + ship_speed.dx # Accounts for the ships velocity in "dx".
        self.velocity.dy = (math.sin(math.radians(self.angle + 90)) * self.speed) + ship_speed.dy # Accounts for the ships velocity in "dy".

    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height,
                                      self.texture, self.angle + 90, RENDER)

    def advance(self):
        super().advance()
        self.life -= 1
        if self.life <= 0:
            self.alive = False


class Asteroid(FlyingObjects):
    """ 
    A base class for the three types of asteroids used in the game.
    """
    def __init__(self, img):
        super().__init__(img)

    def draw(self):
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height, 
                                      self.texture, self.angle, RENDER)

    def advance(self):
        super().advance()
        pass


class LargeRock(Asteroid):
    """
    Creates our large asteroids and its properties.
    """
    def __init__(self):
        super().__init__('images/meteorGrey_big1.png')
        self.center.x = random.randint(1, 50)
        self.center.y = random.randint(1, 150)
        self.direction = random.randint(1, 50)
        self.speed = BIG_ROCK_SPEED
        self.radius = BIG_ROCK_RADIUS
        self.velocity.dx = math.cos(math.radians(self.direction)) * self.speed
        self.velocity.dy = math.sin(math.radians(self.direction)) * self.speed

    def advance(self):
        super().advance()
        self.angle += BIG_ROCK_SPIN

    def split(self, asteroids):
        """ These conditions create two medium and one small asteroid after a large rock is destroyed. """
        medium1 = MediumRock()
        medium1.center.x = self.center.x
        medium1.center.y = self.center.y
        medium1.velocity.dy = self.velocity.dy + 2
        
        medium2 = MediumRock()
        medium2.center.x = self.center.x
        medium2.center.y = self.center.y
        medium2.velocity.dy = self.velocity.dy - 2

        small = SmallRock()
        small.center.x = self.center.x
        small.center.y = self.center.y
        small.velocity.dy = self.velocity.dy + 5 

        asteroids.append(medium1)
        asteroids.append(medium2)
        asteroids.append(small)
        self.alive = False


class MediumRock(Asteroid):
    """
    Creates our medium asteroids and its properties.
    """
    def __init__(self):
        super().__init__('images/meteorGrey_med1.png')
        self.radius = MEDIUM_ROCK_RADIUS
        self.speed = BIG_ROCK_SPEED
        self.velocity.dx = math.cos(math.radians(self.direction)) * self.speed
        self.velocity.dy = math.sin(math.radians(self.direction)) * self.speed

    def advance(self):
        super().advance()
        self.angle += MEDIUM_ROCK_SPIN

    def split(self, asteroids):
        """ These conditions create two small asteroids after a medium rock is destroyed. """
        small1 = SmallRock()
        small1.center.x = self.center.x
        small1.center.y = self.center.y
        small1.velocity.dx = self.velocity.dx + 2 
        small1.velocity.dy = self.velocity.dy + 2 

        small2 = SmallRock()
        small2.center.x = self.center.x
        small2.center.y = self.center.y
        small1.velocity.dx = self.velocity.dx - 2 
        small1.velocity.dy = self.velocity.dy - 2 

        asteroids.append(small1)
        asteroids.append(small2)
        self.alive = False


class SmallRock(Asteroid):
    """
    Creates our small asteroids and its properties.
    """
    def __init__(self):
        super().__init__('images/meteorGrey_small1.png')
        self.radius = SMALL_ROCK_RADIUS
        self.speed = BIG_ROCK_SPEED

    def advance(self):
        super().advance()
        self.angle += SMALL_ROCK_SPIN

    def split(self, asteroids):
        self.alive = False


class Game(arcade.Window):
    """
    This class handles all the game callbacks and interaction
    This class will then call the appropriate functions of
    each of the above classes.
    You are welcome to modify anything in this class.
    """

    def __init__(self, width, height):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.SMOKY_BLACK)

        self.held_keys = set()

        self.background = arcade.load_texture('images/space_background.png')

        self.ship = Ship()

        self.bullets = []

        self.asteroids = []
        for asteroid in range(5):
            asteroid = LargeRock()
            self.asteroids.append(asteroid)

    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """

        # clear the screen to begin drawing
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        for asteroid in self.asteroids:
            asteroid.draw()

        for bullet in self.bullets:
            if bullet.alive:
                bullet.draw()

        if self.ship.alive:
            self.ship.draw()
        
        if not self.ship.alive:
            arcade.draw_text('GAME OVER!', (SCREEN_WIDTH / 2) - 170, SCREEN_HEIGHT / 2, font_size=80, 
                                            font_name='Kenney Pixel', color=arcade.color.RED)
        
        if len(self.asteroids) <= 0:
                arcade.draw_text('WINNER!', (SCREEN_WIDTH / 2) - 130, SCREEN_HEIGHT / 2, font_size=80, 
                                            font_name='Kenney Pixel', color=arcade.color.GREEN)

    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        """
        self.check_keys()

        for asteroid in self.asteroids:
            asteroid.advance()
            if len(self.asteroids) <= 0:
                arcade.draw_text('WINNER!', (SCREEN_WIDTH / 2) - 170, SCREEN_HEIGHT / 2, font_size=80, 
                                            font_name='Kenney Pixel', color=arcade.color.GREEN)          

        if self.ship.alive:
            self.ship.advance()         

        for bullet in self.bullets:
            bullet.advance()

        self.clear_deadObjects()
        self.check_collisions()


    def clear_deadObjects(self):
        """ 
        This class removes 'dead' objects from their respective lists. 
        """
        for bullet in self.bullets:
            if not bullet.alive:
                self.bullets.remove(bullet)

        for asteroid in self.asteroids:
            if not asteroid.alive:
                self.asteroids.remove(asteroid)

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            self.ship.left()

        if arcade.key.RIGHT in self.held_keys:
            self.ship.right()

        if arcade.key.UP in self.held_keys:
            self.ship.thrust()

        if arcade.key.DOWN in self.held_keys:
            self.ship.reverse()

    def check_collisions(self):
        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if bullet.alive and asteroid.alive:
                    distance_x = abs(asteroid.center.x - bullet.center.x)
                    distance_y = abs(asteroid.center.y - bullet.center.y)
                    maximum = asteroid.radius + bullet.radius
                    if (distance_x < maximum) and (distance_y < maximum):
                        asteroid.split(self.asteroids)
                        bullet.alive = False
        
        for asteroid in self.asteroids:
            if self.ship.alive and asteroid.alive:
                distance_x = abs(asteroid.center.x - self.ship.center.x)
                distance_y = abs(asteroid.center.y - self.ship.center.y)
                maximum = asteroid.radius + self.ship.radius
                if (distance_x < maximum) and (distance_y < maximum):
                    self.ship.alive = False

    def on_key_press(self, key: int, modifiers: int):
        """
        Puts the current key in the set of keys that are being held.
        You will need to add things here to handle firing the bullet.
        """
        if self.ship.alive:
            self.held_keys.add(key)

            if key == arcade.key.SPACE:
                bullet = Bullets(self.ship.angle, self.ship.center.x, self.ship.center.y)
                self.bullets.append(bullet)
                bullet.fire(self.ship.velocity)

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key in self.held_keys:
            self.held_keys.remove(key)


# Creates the game and starts it going
window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
arcade.run()