#!/usr/bin/python3
import os
import random
import yaml

with open('encounters.yaml','r') as f:
    encounter_table = yaml.safe_load(f)

# torches, spells, so on
class Trackable():
    def __init__(self,kind):
        # kinds should be one of torch, latern, spell
        self.active = True
        self.kind = kind
        self.turns_passed = -1 # need to fix this so that turns dont increment when torches are lit
        self.total_turns = self.set_turns()

    def set_turns(self):
        turn_lifespan = {
            "torch" : 6,
            "spell" : 3, # place holder
            "lantern" : 24
        }
        return turn_lifespan[self.kind]

    def update_turns(self):
        passed = self.turns_passed + 1
        if self.total_turns - passed <= 1:
            self.active = False
        if self.active:
            self.turns_passed += 1

    def print_meter(self):
        if self.active:
            passed = self.turns_passed + 1
            turns_left = self.total_turns - passed
            meter = '[' + (passed * '.') + (turns_left * '|') +']'
            print(f"{self.kind}: {meter} \t {turns_left} of {self.total_turns} remaining")

# umbrella to hold all the objects and time passed
class Session():
    def __init__(self):
        self.time_passed = "0m"
        self.turns = 1
        self.rolls = []
        self.encounters = []
        self.tracked_objects = []

    def update_time(self):
        # time not counting the current turn
        t = self.turns - 1
        hours = (t * 10) // 60
        minutes = (t * 10) % 60
        if t < 6:
            self.time_passed = f"{minutes}m"
        else:
            self.time_passed = f"{hours}h {minutes}m"
        for to in self.tracked_objects:
            to.update_turns()

    def spent_torches(self):
        st = 0
        for to in self.tracked_objects:
            if to.kind == "torch" and to.active == False:
                st += 1
        return st

    def roll_dice(self):
        dice = input('What would you like to roll, in 1d6 format? ')
        if 'd' in dice:
            count = int(dice.split('d')[0])
            sides = int(dice.split('d')[1])
            result = dice_roller(count,sides)
            self.rolls.append(result)

# Terminal User Interface
class UserInterface():
    def __init__(self):
        self.heading = "Old School Turn Tracker"
        self.keys = {
            'd' : '[d]ice roll',
            't' : '[t]urn passed',
            'n' : '[n]ew light source',
            'e' : '[e]ncounter check',
            's' : '[s]pell',
            'q' : '[q]uit'
        }

    def main_screen(self,new_game):
        self.clear()
        title_box = self.text_box(self.heading)
        print(title_box)
        print(f"Time passed:  {new_game.time_passed}")
        print(f"Current turn: {new_game.turns}")
        print(f"Spent Torches: {new_game.spent_torches()}")
        if new_game.tracked_objects:
            for to in new_game.tracked_objects:
                to.print_meter()
        print(f"\nEncounters: {new_game.encounters}")
        print(f"\nRolls made: {new_game.rolls}")
        if new_game.rolls:
            print(f"Last roll: {new_game.rolls[-1]}")
        else:
            print()
        print()
        user_keys = ""
        for s in self.keys.values():
            user_keys = user_keys + s + "\t"
        print(user_keys)

    def user_input(self):
        key = input(f"Enter a key: ")
        return key

    def clear(self):
        clear = 'clear'
        if os.name == 'nt':
            clear = 'cls'
        os.system(clear)

    def text_box(self, text):
        w = '-' * len(text)
        line = '+-' + w + '-+'
        box = line + '\n' + '| ' + text + ' |\n' + line
        return box


def dice_roller(count,sides):
    result = sum(random.randint(1,sides) for _ in range(count))
#    for i in range(dieCount):
#        roll = random.randint(1,dieSides)
#        result += roll
    return(result)

def main():
    new_game = Session()
    ui = UserInterface()
    while True:
        ui.main_screen(new_game)
        key = ui.user_input()
        if key == 't':
            new_game.turns += 1
            new_game.update_time()
        if key == 'd':
            new_game.roll_dice()
        if key == 'n':
            kind = input("Are you lighting a [t]orch or a [l]antern? ")
            if kind in ['t','l']:
                if kind == 'l':
                    kind = 'lantern'
                if kind == 't':
                    kind = 'torch'
                light_source= Trackable(kind)
                new_game.tracked_objects.append(light_source)
        if key == 'e':
            print("Encounter Tables:")
            tables = list(encounter_table.keys())
            for n,table in enumerate(encounter_table):
                print(f"  {n+1}. {table}")
            selection = int(input("Which table to roll on? ")) - 1
            selected_table = tables[selection]
            encounter = random.choice(encounter_table[selected_table])
            monster = list(encounter.keys())[0]
            dice = encounter[monster]
            dice = dice_roller(int(dice.split('d')[0]), int(dice.split('d')[1]))
            new_game.encounters.append(f"{dice} {monster}")
        if key == 'q':
            q = input('Are you sure you want to quit? ')
            if q.lower() in ['y', 'ye', 'yes', 'ya', 'yup', 'yeah']:
                quit()
        if key == 'qy':
                quit()

main()
