"""
Text RPG

a simple terminal based RPG.
"""

import curses
import time
import gdax  # crypto prices for game currencies lol
import argparse  # maybe later
from curses import KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from random import randint


class Player:
    """
    Choose your character (literally your 'char' ex. '@', '0', '#')

    This is the player class. Moves the player around the world. Contains
    player attributes n other goodies such as items.

    -- maybe luck could be fun
    """

    def __init__(self, y, x, dimensions, money, knowledge, strength):
        self.y = y
        self.x = x
        self.dimensions = dimensions
        self.money = money
        self.knowledge = knowledge
        self.strength = strength
        self.character = '@'
        self.name = "tab"
        self.in_building = False
        self.building = None
        self.employed = False
        self.wage = 8

    def move(self, key):
        if key == KEY_RIGHT and self.x < self.dimensions[1] - 2:
            self.x = self.x + 1
        if key == KEY_LEFT and self.x > 1:
            self.x = self.x - 1
        if key == KEY_UP and self.y > 1:
            self.y = self.y - 1
        if key == KEY_DOWN and self.y < self.dimensions[0] - 1:
            self.y = self.y + 1
        return self.y, self.x

    def manage_event(self, event):
        if event == "c":  # class
            self.knowledge += 2
            self.money -= 20
        if event == "e":  # exercise
            self.strength += 1
        if event == "s":  # study
            self.knowledge += 1
        if event == "w":  # work
            self.money += (self.wage * 4)  # shifts are 4 hours long


class Citizen:
    """
    Sheeple. Sheeple everywhere.
    """
    def __init__(self, y, x, c):
        self.y = y
        self.x = x
        self.character = c


class Information:
    """
    This class will display world information to the player on the screen.
    """
    def __init__(self, y, x, player):
        self.y = y
        self.x = x
        self.player = player
        # initialize gdax public client for crypto prices
        self.coins = ["BTC-USD", "ETH-USD", "LTC-USD", "BCH-USD"]
        self.public_client = gdax.PublicClient()
        self.price_list = ["", "", "", ""]

    def __str__(self):
        return "money: {} Knowledge: {} Strength: {}".format(
                                                        self.player.money,
                                                        self.player.knowledge,
                                                        self.player.strength)

    def price(self, coin="BTC-USD"):
        tkr = self.public_client.get_product_ticker(coin)
        return tkr["price"]

    def _refresh_prices(self):
        self.price_list = []
        for coin in self.coins:
            self.price_list.append(self.price(coin))

    def prices(self):
        self._refresh_prices()
        return "BTC: {}\nETH: {}\nLTC: {}\nBCH: {}".format(self.price_list[0],
                                                           self.price_list[1],
                                                           self.price_list[2],
                                                           self.price_list[3])


class Building:
    """
    Who wants to be outside??
    """
    def __init__(self, y, x, size, purpose, appearance, o):
        self.y = y
        self.x = x
        #self.size = size  forget it for now
        self.purpose = purpose
        self.appearance = appearance
        self.inside_options = o

    def __str__(self):
        return purpose

    def draw(self, w):
        """
        string = self.appearance * self.size
        for i in xrange(0, self.size):
            w.addstr(self.y+i, self.x, string)
        """
        w.addstr(self.y, self.x, self.appearance)

    def display_options(self):
        string = " What do you want to do?\n (Press the number on the keyboard)\n"
        for count, option in enumerate(self.inside_options):
            string += " {}: {}\n".format(count, option)
        return string


class Day:
    """
    A day consists of 24 hours.

    Events take up hours but earn you money or knowledge.
    """
    def __init__(self, player):
        self.player = player
        self.length = 24
        self.display_day = []
        self.day = []
        self.events = {"work": ["w", 4],
                       "class": ["c", 2],
                       "study": ["s", 1],
                       "exercise": ["e", 1],
                       "sleep": ["z", 8]}

    def __str__(self):
        return " ".join(self.display_day)

    def real_day(self):
        return " ".join(self.day)

    def add_event(self, e):
        event = self.events[e]
        if event[1] + len(self.day) - 1 < self.length:
            self.player.manage_event(event[0])
            padding = self.display_day.index("_")
            for i in xrange(0, event[1]):
                self.display_day[padding+i] = event[0]
                self.day.append(event[0])


class DayManager:
    """
    A collection of days and advances days when necesary.
    """
    def __init__(self, player):
        self.day_list = []
        self.today = None
        self.player = player

    def add_day(self):
        self.day_list.append(Day(self.player))
        self.today = self.day_list[-1]
        for i in xrange(0, 24):
            self.today.display_day.append("_")

        self.today.add_event("sleep")

    def day_number(self):
        return len(self.day_list)


def format_time(start):
    return int(time.time() - start)


def generate_map(dimensions):
    pass

def pregame():
    money = 100
    knowledge = randint(1, 10)
    strength = randint(1, 10)
    return [money, knowledge, strength]


def redraw_world(world, buildings):
    world.clear()
    world.border(0)
    world.addstr(0, 24, "Text RPG")
    for b in buildings:
        b.draw(world)


def game(rows, cols, y, x, stats):
    # Game Setup
    title = "Text RPG"
    curses.initscr()
    world = curses.newwin(rows, cols, y, x)
    world.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    world.border(0)
    world.nodelay(1)
    world.addstr(0, 24, title)
    max_days = 10
    bottom = 20
    dimensions = world.getmaxyx()
    dimensions = (bottom, dimensions[1])

    # Initialize Player
    player_y = 1
    player_x = 1
    player = Player(player_y, player_x, dimensions,
                    stats[0], stats[1], stats[2])

    # Initialize Day
    day_manager = DayManager(player)
    day_manager.add_day()

    # Initialize information
    info_y = 21
    info_x = 0
    info = Information(info_y, info_x, player)
    world.addstr(info.y, info.x, str(info))
    #world.addstr(info.y+1, info.x, info.prices())

    # Initialize buildings
    work = Building(15, 20, 4, "work", "W", ["work", "leave"])
    school = Building(10, 30, 5, "school", "S", ["class", "leave"])
    gym = Building(5, 5, 3, "gym", "G", ["exercise", "leave"])
    house = Building(2, 48, 2, "house", "H", ["sleep", "leave"])

    buildings = [work, school, gym, house]

    # draw buildings
    for b in buildings:
        b.draw(world)

    # Initialize various needed variables
    key = None
    gameover = False
    day = 0
    next_day = True
    start_time = time.time()

    # Game Loop
    while key != ord('q'):
        """
        # Timekeeping
        # This will be changed to event but... i think i can find a use for this
        seconds = format_time(start_time)
        if seconds == 10:
            next_day = True
        if seconds == 10 and next_day:  # go to the next day
            #world.addstr(info.y+1, info.x, info.prices())
            start_time = time.time()
            seconds = 0
            next_day = False
            day += 1
        """

        world.addstr(29, 0, "Day: {}".format(day_manager.day_number()))

        # rewrite info on screen... probably inefficient but will do for now
        world.addstr(info.y, info.x, str(info))
        world.addstr(bottom, 1, 'Events: ['+str(day_manager.today)+']')

        # player movement
        key = world.getch()
        if not player.in_building:
            world.addch(player.y, player.x, ord(' '))
            player.move(key)
            world.addch(player.y, player.x, player.character)

        # collision detection
            for b in buildings:
                if player.x == b.x and player.y == b.y:
                    player.in_building = True
                    player.building = b
                    world.clear()
                    world.addstr(1, 0, b.display_options())
                    world.border(0)
                    world.addstr(0, 24, b.purpose)
                    player.x += 1

        # exit building and return to world
        if player.in_building:
            if key == ord('0') and player.building.purpose != "house":  # do event
                event = player.building.inside_options[0]
                day_manager.today.add_event(event)
            if key == ord('0') and player.building.purpose == "house":
                day_manager.add_day()
                world.addstr(bottom, 1, 'Events: ['+str(day_manager.today)+']')
            if key == ord('1'):  # exit building
                player.in_building = False
                redraw_world(world, buildings)

        # Check if day limit has been reached
        if day_manager.day_number() > max_days:
            gameover = True
            key = ord('q')

    curses.beep()
    curses.endwin()
    print "Gameover."
    print "Knowledge: {}".format(player.knowledge)
    print "Wealth: {}".format(player.money)


if __name__ == "__main__":
    window = [30, 60, 0, 0]
    player_stats = pregame()
    game(window[0], window[1], window[2], window[3], player_stats)
