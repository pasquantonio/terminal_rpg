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

    def __init__(self, y, x, dimensions, wealth, knowledge, strength):
        self.y = y
        self.x = x
        self.dimensions = dimensions
        self.wealth = wealth
        self.knowledge = knowledge
        self.strength = strength
        self.character = '@'
        self.name = "tab"

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
        return "Wealth: {} Knowledge: {} Strength: {}".format(
                                                        self.player.wealth,
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
    def __init__(self, y, x, size, purpose, appearance):
        self.y = y
        self.x = x
        self.size = size
        self.purpose = purpose
        self.appearance = appearance

    def __str__(self):
        return purpose

    def draw(self, w):
        string = self.appearance * self.size
        for i in xrange(0, self.size):
            w.addstr(self.y+i, self.x, string)


def format_time(start):
    return int(time.time() - start)


def pregame():
    wealth = randint(1, 10)
    knowledge = randint(1, 10)
    strength = randint(1, 10)
    return [wealth, knowledge, strength]


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
    world.addstr(0, int(cols/2) - len(title), title)
    bottom = 20
    world.addstr(bottom, 0, '_'*60)
    dimensions = world.getmaxyx()
    dimensions = (bottom, dimensions[1])

    # Initialize Player
    player_y = 1
    player_x = 1
    player = Player(player_y, player_x, dimensions,
                    stats[0], stats[1], stats[2])

    # Initialize information
    info_y = 21
    info_x = 0
    info = Information(info_y, info_x, player)
    world.addstr(info.y, info.x, str(info))
    #world.addstr(info.y+1, info.x, info.prices())

    # Initialize buildings
    work = Building(15, 20, 4, "work", "W")
    school = Building(10, 30, 5, "school", "S")
    gym = Building(5, 5, 3, "gym", "G")
    house = Building(2, 48, 2, "house", "H")

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
        # Timekeeping
        seconds = format_time(start_time)
        if seconds == 30:
            next_day = True
        if seconds == 30 and next_day:  # go to the next day
            world.addstr(info.y+1, info.x, info.prices())
            start_time = time.time()
            seconds = 0
            next_day = False
            day += 1

        world.addstr(29, 0, "Day: {} Time: {} Start: {}".format(day, seconds, start_time))
        # player movement
        key = world.getch()
        world.addch(player.y, player.x, ord(' '))
        player.move(key)
        world.addch(player.y, player.x, player.character)


    curses.beep()
    curses.endwin()
    print "Gameover."


if __name__ == "__main__":
    window = [30, 60, 0, 0]
    player_stats = pregame()
    game(window[0], window[1], window[2], window[3], player_stats)

    """
    pc = gdax.PublicClient()
    tkr = pc.get_product_ticker("BTC-USD")
    print tkr
    """
