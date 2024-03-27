import pygame
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)  # light blue
RED = (188, 39, 50)  # custom red
DARK_GREY = (80, 78, 81)
BLACK = (0, 0, 0)

FONT = pygame.font.SysFont("comicsans", 16)


# Planet class
class Planet:
    AU = 149.6e6 * 1000  # Astronomical Unit = distance earth to sun in meters
    G = 6.67428e-11  # Gravitional constant
    SCALE = 250 / AU  # scale factor: 1 AU = 100 pixels
    # 250 -> 200: zoom out!
    # 250 -> 300: zoom in!
    TIMESTEP = 3600 * 24  # timestamp: 1 day

    def __init__(self, name, x, y, radius, color, mass):
        self.name = name  # PP: added name of planet
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color  # one color for the moment
        self.mass = mass  # for calculations, so kg

        self.orbit = []  # to keep track of orbit

        # to indicate this is a planet
        # no drawing of an orbit of the sun
        self.sun = False
        self.distance_to_sun = 0

        # velocity
        self.x_vel = 0
        self.y_vel = 0

    # draw planet onscreen
    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2  # centered
        y = self.y * self.SCALE + HEIGHT / 2

        # draw orbit of myself if it has at least 3 positions
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))
            # draw the orbit
            pygame.draw.lines(win, self.color, False, updated_points, 2)

        # draw the planet
        pygame.draw.circle(win, self.color, (x, y), self.radius)

        # draw the distance to the sun on top of myself
        if not self.sun:
            # distance_text = FONT.render(
            #    f"{self.name}: {round(self.distance_to_sun/1000, 1)} km", 1, WHITE
            # )
            # PP: draw also planet name
            planet_text = FONT.render(f"{self.name}", 1, WHITE)
            distance_text = FONT.render(
                f"{round(self.distance_to_sun/1000, 1)} km", 1, WHITE
            )
            # draw text at a nice position
            name_text_x = x - planet_text.get_width() / 2
            name_text_y = y - 2 * planet_text.get_height() - 5
            distance_text_x = x - distance_text.get_width() / 2
            distance_text_y = y - distance_text.get_height() - 10
            win.blit(planet_text, (name_text_x, name_text_y))
            win.blit(distance_text, (distance_text_x, distance_text_y))

    # calculate the attraction (gravity law + trigonometry)
    # Remember: real-world numbers!
    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        # trigonometry
        theta = math.atan2(distance_y, distance_x)  # remember: "y" over "x"
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    # update my position using all other objects
    def update_position(self, planets):
        total_fx = total_fy = 0  # total force of all the planets
        for planet in planets:
            if self == planet:  # do not take into account myself
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        # update velocity
        # physics: F = m * a  => a = F / m
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        # update position
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP

        # add position to orbit
        self.orbit.append((self.x, self.y))


def main():
    run = True
    clock = pygame.time.Clock()  # for game refresh rate

    # create sun and planets
    sun = Planet("Sun", 0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    # Note: initial x (first parameter) is opposite y_vel
    #       to let the planet orbit the sun!
    earth = Planet("Earth", -1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000  # initial y-vel in m/s

    mars = Planet("Mars", -1.524 * Planet.AU, 0, 12, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000

    mercury = Planet("Mercury", 0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30 * 10**23)
    mercury.y_vel = -47.4 * 1000

    venus = Planet("Venus", 0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000

    # collect all the planets
    planets = [sun, earth, mars, mercury, venus]

    while run:
        # clock.tick(60)  # frame rate 60 maximum
        clock.tick(30)  # frame rate
        # redraw background in WINdow
        # to erase planerts on old positions
        WIN.fill(BLACK)

        # stop program
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # solar system simulation
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        # update the scene
        pygame.display.update()

    # quit program
    pygame.quit()


# execute main
main()
