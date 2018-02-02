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
    """

    def __init__(self, y, x, dimensions, money, knowledge, strength, charm):
        self.y = y
        self.x = x
        self.dimensions = dimensions
        self.money = money
        self.knowledge = knowledge
        self.strength = strength
        self.charm = charm
        self.character = '@'
        self.name = "tab"
        self.in_building = False
        self.building = None
        self.employed = False
        self.bank = BankAccount()
        self.positions = {0: ["Unemployed", 0],
                          20: ["janitor", 8],
                          30: ["mailclerk", 10],
                          45: ["salesman", 15],
                          75: ["manager", 30],
                          120: ["executive", 60],
                          180: ["vice president", 120],
                          250: ["ceo", 200]}
        self.job = self.positions[0]
        self.alarm_clock = False
        self.pill = 0

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
            self.money += (self.job[1] * 4)  # shifts are 4 hours long
        if event == "b":
            self.charm += 2
            self.money -= 20

    def check_promotion(self):
        if self.knowledge >= 250:
            return self.positions[250]
        if self.knowledge >= 180:
            return self.positions[180]
        if self.knowledge >= 120:
            return self.positions[120]
        if self.knowledge >= 75:
            return self.positions[75]
        if self.knowledge >= 45:
            return self.positions[45]
        if self.knowledge >= 30:
            return self.positions[30]
        if self.knowledge >= 20:
            return self.positions[20]
        return self.positions[0]


class Citizen:
    """
    Sheeple. Sheeple everywhere.
    """
    def __init__(self, y, x, c):
        self.y = y
        self.x = x
        self.character = c


class BankAccount:
    """
    A general bank account class.

    +Deposits ((fixed or variable?) interest rate, compounded daily)
    +Withdrawals
    +Loans ((fixed or variable) interest rate, compounded daily)
    +Investment Account (like a brokerage acct or ira.)
    """
    def __init__(self):
        self._balance = 0
        self.interest_rate = 0.015
        self.loan = None

    def deposit(self, amount):
        self._balance += amount

    def withdraw(self, amount):
        if amount <= self._balance:
            self._balance -= amount

    def balance(self):
        return self._balance

    def get_interest_rate(self):
        return self.interest_rate * 100

    def compound_balance(self):
        interest = self._balance * self.interest_rate
        self._balance += interest

    def create_loan(self, a, l):
        self.loan = Loan(a, l)

    def loan_balance(self):
        return self.loan.get_balance() if self.loan else 0

    def loan_interest_rate(self):
        return self.loan.get_interest_rate() if self.loan else 0

    def repay_loan(self, amount):
        if self.loan:
            self.loan.make_payment(amount)
        return

    def destroy_loan(self):
        self.loan = None

class Loan:
    """
    Easier to manage when its in a class on its own
    """
    def __init__(self, amount, life, ir = .095, vi = False):
        self.amount = amount
        self.balance = amount
        self.life = life  # number of days to payback loan
        self.vi = vi  # variable interest rate
        self.interest_rate = ir

    def __str__(self):
        return "{}".format(self.balance)

    def get_balance(self):
        return self.balance

    def get_interest_rate(self):
        return self.interest_rate * 100

    def daily_payment(self):
        pass

    def make_payment(self, payment):
        self.balance -= payment

    def compound_loan(self):
        interest = self.balance * self.interest_rate
        self.balance += interest

    def change_interest_rate(self):
        self.interest_rate = randint(0, 10)
        self.interest_rate = self.interest_rate/100


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
        return "Cash: {} Knowledge: {}  Strength: {} Charm: {}  ".format(
                                                        self.player.money,
                                                        self.player.knowledge,
                                                        self.player.strength,
                                                        self.player.charm)

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

    def bank_info(self):
        return "Balance: {0:.2f} @ {1:.2f}% | Loan balance: {2:.2f} @ {3:.2f}%".format(
                                        self.player.bank.balance(),
                                        self.player.bank.get_interest_rate(),
                                        self.player.bank.loan_balance(),
                                        self.player.bank.loan_interest_rate())


class Building:
    """
    Who wants to be outside??
    """
    def __init__(self, y, x, purpose, appearance, o):
        self.y = y
        self.x = x
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

    def display_options(self, player):
        string = " What do you want to do?\n (Press the number on the keyboard)\n"
        for count, option in enumerate(self.inside_options):
            if option == "ask for promotion" and player.job[1] == 0:
                option = "ask for job"
            string += " {}: {}\n".format(count+1, option)
        if self.purpose == "school":
            string += "\n\n Class costs $20"
        if self.purpose == "pub":
            string += "\n\n Beer costs $20"
        if self.purpose == "store":
            string += "\n\n Pills costs $45, Clock costs $200"
        return string

    def player_input(self, key, world, player, day_manager, buildings):
        for i in xrange(1, len(self.inside_options)+1):
            if key == ord(str(i)):
                event = player.building.inside_options[i-1]
                do_event = day_manager.today.add_event(event)
                if event == "sleep":  # creates new day
                    day_manager.add_day()
                    world.addstr(20, 1, 'Today : ['+str(day_manager.today)+']')
                    if player.pill >= 1:
                        player.pill -= 1
                if event == "leave":
                    player.in_building = False
                    redraw_world(world, buildings)
                # this needs to become its own function
                if event == "deposit":
                    world.addstr(10, 5, "Enter amount to deposit, then hit space:       ")
                    key = None
                    amount = ""
                    valid = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'),
                             ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
                    while key != ord(' '):
                        key = world.getch()
                        if key in valid:
                            amount += str(chr(key))
                        world.addstr(11, 5, amount)
                    world.addstr(11, 5, " "*len(amount))
                    if player.money >= int(amount):
                        player.money -= int(amount)
                        player.bank.deposit(int(amount))
                        world.addstr(10, 5, " "*50)
                        world.border(0)
                        world.addstr(10, 5, "Funds Deposited.")
                    else:
                        world.addstr(10, 5, " "*50)
                        world.border(0)
                        world.addstr(10, 5, "Not Enough Funds!")
                if event == "withdraw":
                    world.addstr(10, 5, "Enter amount to withdraw, then hit space:      ")
                    key = None
                    amount = ""
                    valid = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'),
                             ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
                    while key != ord(' '):
                        key = world.getch()
                        if key in valid:
                            amount += str(chr(key))
                        world.addstr(11, 5, amount)
                    world.addstr(11, 5, " "*len(amount))
                    if player.bank.balance() >= int(amount):
                        player.money += int(amount)
                        player.bank.withdraw(int(amount))
                        world.addstr(10, 5, " "*50)
                        world.border(0)
                        world.addstr(10, 5, "Funds Withdrawn.")
                    else:
                        world.addstr(10, 5, " "*50)
                        world.border(0)
                        world.addstr(10, 5, "Negative balance not allowed!")
                if event == "get loan":
                    world.addstr(10, 5, "Enter loan amount, then hit space (max: 1000): ")
                    key = None
                    amount = ""
                    valid = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'),
                             ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
                    while key != ord(' '):
                        key = world.getch()
                        if key in valid:
                            amount += str(chr(key))
                        world.addstr(11, 5, amount)
                    world.addstr(11, 5, " "*len(amount))
                    if amount != "":
                        if int(amount) <= 1000 and player.bank.loan is None:
                            player.bank.create_loan(int(amount), 10)  # 1000 dollars, 10 days to repay
                            player.money += int(amount)
                            world.addstr(10, 5, " "*50)
                            world.border(0)
                            world.addstr(10, 5, "Money has been loaned. {} days left to repay".format(player.bank.loan.life))
                        else:
                            world.addstr(10, 5, " "*50)
                            world.border(0)
                            world.addstr(10, 5, "Sorry thats too much or you already have a loan.")
                    else:
                        world.addstr(10, 5, "Please try again.                              ")
                if event == "repay loan":
                    if player.bank.loan:
                        world.addstr(10, 5, "Enter loan amount, then hit space (max: 1000): ")
                        key = None
                        amount = ""
                        valid = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'),
                                 ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
                        while key != ord(' '):
                            key = world.getch()
                            if key in valid:
                                amount += str(chr(key))
                            world.addstr(11, 5, amount)
                        world.addstr(11, 5, " "*len(amount))
                        if amount != "":
                            if int(amount) <= player.money:
                                player.money -= int(amount)
                                player.bank.repay_loan(int(amount))
                                world.addstr(10, 5, " "*50)
                                world.border(0)
                                world.addstr(10, 5, "Payment received")
                                if player.bank.loan_balance() <= 0:
                                    player.bank.destroy_loan()
                            else:
                                world.addstr(10, 5, "Not enough funds. (withdraw from bank first)")
                        else:
                            world.addstr(10, 5, "Please try again.                              ")
                    else:
                        world.addstr(10, 5, "you do not currently have a loan.")
                if event == "ask for promotion":
                    job = player.job
                    player.job = player.check_promotion()
                    if job != player.job:
                        world.addstr(10, 5, "New position: {}".format(player.job[0]))
                        world.addstr(11, 5, "Pay per Hour: {}".format(player.job[1]))
                    else:
                        world.addstr(10, 5, "Gain more knowledge to get promoted")
                if event == "buy caffiene pill":
                    if player.money >= 45:
                        player.money -= 45
                        player.pill += 1
                        world.addstr(10, 5, "                                      ")
                        world.addstr(10, 5, "Purchased 1 pill.")
                    else:
                        world.addstr(10, 5, "You need 45 dollars to buy that.")
                if event == "buy alarm clock":
                    if not player.alarm_clock:
                        if player.money >= 200:
                            player.money -= 200
                            player.alarm_clock = True
                            world.addstr(10, 5, "Purchased alarm clock.")
                        else:
                            world.addstr(10, 5, "You need 200 dollars to buy that.")
                    else:
                        world.addstr(10, 5, "You already own an alarm clock.      ")
                if event == "coin flip":
                    world.addstr(9, 5, "10 dollars to place a bet.              ")
                    world.addstr(13, 5, "Your Choice:                           ")
                    world.addstr(14, 5, "Result:                                ")
                    world.addstr(15, 5, "                                       ")
                    world.addstr(10 , 5, "Choose one then press space to submit:")
                    world.addstr(11, 5, "1. Heads")
                    world.addstr(12, 5, "2. Tails")
                    key = None
                    valid = [ord("1"), ord("2")]
                    choice = 1
                    results = {1: "Heads", 2: "Tails", "": ""}
                    while key != ord(' '):
                        key = world.getch()
                        if key in valid:
                            choice = int(str(chr(key)))
                        world.addstr(13, 5, "Your Choice: {}".format(results[choice]))
                    result = coin_toss()
                    if choice == result:
                        player.money += 10
                        world.addstr(14, 5, "Result: {}, You Win! ".format(results[result]))
                        world.addstr(15, 5, "Press 1 to play again, 2 to Exit")
                    else:
                        player.money -= 10
                        world.addstr(14, 5, "Result: {}, You Lose!".format(results[result]))
                    world.addstr(15, 5, "Press 1 to play again, 2 to Exit")
                    choice = ""
                if event == "drink beer" and do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "Delicious. Charm +2")
                if event == "personal training" and do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "Arnold would be proud! Strength +2")
                if event == "class" and do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "Brain blast! Knowledge +2")
                if event == "study" and do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "Knowledge is Power. Knowledge +1")
                if event == "exercise" and do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "No Pain. No Gain. Strength +1")
                if event == "bar fight":
                    world.addstr(10, 5, "No one to fight rn. please leave.")
                if not do_event:
                    world.addstr(10, 5, "                                      ")
                    world.addstr(10, 5, "You can't afford this.")


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
                       "study": ["s", 2],
                       "exercise": ["e", 2],
                       "personal training": ["t", 2],
                       "sleep": ["z", 8],
                       "deposit": ["d", 0],
                       "withdraw": ["W", 0],
                       "get loan": ["l", 0],
                       "repay loan": ["r", 0],
                       "ask for promotion": ["p", 0],
                       "buy caffiene pill": ["a", 0],
                       "buy alarm clock": ["k", 0],
                       "bar fight": ["f", 0],
                       "drink beer": ["b", 2],
                       "coin flip": ["h", 0]}

    def __str__(self):
        return " ".join(self.display_day)

    def real_day(self):
        return " ".join(self.day)

    def add_event(self, e):
        ignore = ["leave", "deposit", "withdraw", "get loan", "repay loan",
        "ask for promotion", "buy caffiene pill", "buy alarm clock",
        "coin flip", "bar fight"]
        if e == "class" and self.player.money < 20:
            return False
        if e == "coin flip" and self.player.money < 10:
            return False
        if e == "drink beer" and self.player.money < 20:
            return False
        if e == "personal training" and self.player.money < 20:
            return False
        if e not in ignore:
            event = self.events[e]
            if event[1] + len(self.day) - 1 < self.length:
                self.player.manage_event(event[0])
                padding = self.display_day.index("_")
                if e == "sleep":
                    if self.player.alarm_clock and self.player.pill == 0:
                        for i in xrange(0, 6):
                            self.display_day[padding+i] = event[0]
                            self.day.append(event[0])
                    if self.player.alarm_clock and self.player.pill >= 1:
                        for i in xrange(0, 4):
                            self.display_day[padding+i] = event[0]
                            self.day.append(event[0])
                    if not self.player.alarm_clock and self.player.pill >= 1:
                        for i in xrange(0, 6):
                            self.display_day[padding+i] = event[0]
                            self.day.append(event[0])
                    if not self.player.alarm_clock and self.player.pill == 0:
                        for i in xrange(0, event[1]):
                            self.display_day[padding+i] = event[0]
                            self.day.append(event[0])
                else:
                    for i in xrange(0, event[1]):
                        self.display_day[padding+i] = event[0]
                        self.day.append(event[0])
        return True


class DayManager:
    """
    A collection of days and advances days when necesary.
    """
    def __init__(self, player):
        self.day_list = []
        self.today = None
        self.player = player

    def add_day(self):
        self.player.bank.compound_balance()
        if self.player.bank.loan:
            self.player.bank.loan.compound_loan()
        self.day_list.append(Day(self.player))
        self.today = self.day_list[-1]
        for i in xrange(0, 24):
            self.today.display_day.append("_")

        self.today.add_event("sleep")

    def day_number(self):
        return len(self.day_list)


def coin_toss():
    return randint(1, 2)

def format_time(start):
    return int(time.time() - start)


def generate_map(dimensions):
    """
    Want to write a function that randomly places buildings around the map,
    including all core buildings (bank, school, work, )
    """
    pass


def pregame():
    money = 25
    knowledge = randint(1, 5)
    strength = randint(1, 5)
    charm = randint(1, 5)
    return [money, knowledge, strength, charm]


def redraw_world(world, buildings):
    world.clear()
    world.border(0)
    world.addstr(0, 24, "Text RPG")
    for b in buildings:
        b.draw(world)


def end_game_rating(player, day_manager):
    rating = ""
    total_assets = player.money + player.bank.balance() - player.bank.loan_balance()
    history = "Wealth: {}, Knowledge: {}, Strength: {}, Charm: {}, Days: {}".format(
        total_assets,
        player.knowledge,
        player.strength,
        player.charm,
        day_manager.day_number()
    )
    print "Knowledge: {}".format(player.knowledge)
    print "Wealth: {}".format(total_assets)
    with open("game_history.txt", "a") as filewriter:
        filewriter.write(history)
    if total_assets < 101 and player.knowledge < 20:
        return "Poor and Stupid"
    else:
        return "Not Poor and Stupid. I'll add more later"


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
    bottom = 20
    dimensions = world.getmaxyx()
    dimensions = (bottom, dimensions[1])

    world.addstr(10, 5, "Choose game length then hit space.\n     Default is 15 days.")
    world.addstr(12, 5, "1. 15 Days")
    world.addstr(13, 5, "2. 40 Days")
    world.addstr(14, 5, "3. 100 Days")
    world.border(0)
    key = None
    choice = 1
    day_dict = {1: 15, 2: 40, 3: 100}
    valid = [ord('1'), ord('2'), ord('3')]
    while key != ord(' '):
        key = world.getch()
        if key in valid:
            choice = int(str(chr(key)))
        world.addstr(15, 5, "Your Choice: {} days ".format(day_dict[choice]))
    max_days = day_dict[choice]
    world.clear()
    world.border(0)
    world.addstr(0, 24, "Text RPG")
    intro = "You wake up in a small town. \n " + \
            "    No memory of how you got here. \n " + \
            "    Someone gives you a key and says \n     you stay at their house (H)\n" + \
            "     They also tell you to go to work (W) \n     if you need money.\n\n\n" + \
            "     Hit space to play"
    world.addstr(5, 5, intro)
    world.border(0)
    key = None
    while key != ord(' '):
        key = world.getch()

    world.clear()
    world.border(0)
    world.addstr(0, 24, "Text RPG")
    # Initialize Player
    player_y = 1
    player_x = 35
    player = Player(player_y, player_x, dimensions,
                    stats[0], stats[1], stats[2], stats[3])

    # Initialize Day
    day_manager = DayManager(player)
    day_manager.add_day()

    # Initialize information
    info_y = 21
    info_x = 1
    info = Information(info_y, info_x, player)
    world.addstr(info.y, info.x, str(info))

    # Initialize buildings
    work = Building(15, 20, "work", "W", ["work", "ask for promotion", "leave"])
    school = Building(10, 30, "school", "S", ["study", "class", "leave"])
    gym = Building(5, 5, "gym", "G", ["exercise", "personal training", "leave"])
    house = Building(2, 48, "house", "H", ["sleep", "leave"])
    bank = Building(15, 30, "bank", "B", ["deposit", "withdraw", "get loan", "repay loan", "leave"])
    store = Building(15, 50, "store", "C", ["buy caffiene pill", "buy alarm clock", "leave"])
    pub = Building(9, 6, "pub", "P", ["drink beer", "bar fight", "leave"])
    casino = Building(3 , 30, "casino", "X", ["coin flip", "leave"])
    buildings = [work, school, gym, house, bank, store, pub, casino]

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
        # Display information to the player
        world.addstr(29, 0, "Day: {}".format(day_manager.day_number()))
        world.addstr(info.y, info.x, str(info))
        world.addstr(info.y+1, info.x, info.bank_info())
        world.addstr(info.y+2, info.x, "Job: {} Pay: {}".format(
                                                          info.player.job[0],
                                                          info.player.job[1]))
        world.addstr(info.y+3, info.x, "Pills: {}".format(player.pill))
        clock = "Yes" if player.alarm_clock else "No"
        world.addstr(info.y+4, info.x, "Alarm Clock: {}".format(clock))
        world.addstr(bottom, 1, 'Today : ['+str(day_manager.today)+']')

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
                    world.addstr(1, 0, b.display_options(player))
                    world.border(0)
                    world.addstr(0, 24, b.purpose)
                    player.x += 1

        # exit building and return to world
        if player.in_building:
            player.building.player_input(key, world, player,
                                         day_manager, buildings)

        # Check if day limit has been reached
        if day_manager.day_number() > max_days:
            gameover = True
            key = ord('q')

    curses.beep()
    curses.endwin()
    print "Gameover."
    print(end_game_rating(player, day_manager))


if __name__ == "__main__":

    window = [30, 60, 0, 0]
    player_stats = pregame()
    game(window[0], window[1], window[2], window[3], player_stats)
