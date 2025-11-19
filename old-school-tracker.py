#!/usr/bin/python3
import os
import random
import yaml

with open('encounters.yaml','r') as f:
    encounter_table = yaml.safe_load(f)

# torches, spells, so on
class Trackable():
    def __init__(self, kind, name=None, total_turns=None, turns_passed=-1):
        # kinds should be one of torch, latern, spell
        self.active = True
        self.kind = kind
        self.name = name
        # need to fix this so that turns dont increment when torches are lit
        self.turns_passed = turns_passed
        if not total_turns:
            self.total_turns = self.set_turns(total_turns)
        else:
            self.total_turns = total_turns

    def set_turns(self,turns):
        if self.kind == "torch":
            turn_lifespan = 6
        if self.kind == "lantern":
            turn_lifespan = 24
        if self.kind == "spell":
            turn_lifespan = turns
        return turn_lifespan

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
            if self.kind == "spell":
                print(f"{self.name.title()}: {meter} \t {turns_left} of {self.total_turns} remaining")
            else:
                print(f"{self.kind}: {meter} \t {turns_left} of {self.total_turns} remaining")

# umbrella to hold all the objects and time passed
class Session():
    save_directory = "saves/"
    historical_data = []
    def __init__(self, turns=1, time_passed='0m', rolls=None, encounters=None, tracked_objects=None, progress=None):
        self.turns = turns
        self.time_passed = time_passed
        if not rolls:
            self.rolls = []
        else:
            self.rolls = rolls
        if not encounters:
            self.encounters = []
        else:
            self.encounters = encounters
        if not tracked_objects:
            self.tracked_objects = []
        else:
            self.tracked_objects = tracked_objects
        if not progress:
            self.progress = []
        else:
            self.progress = progress

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

    @classmethod
    def start_session(cls):
        print("Welcome to the Old School Tracker\n") 
        print("Available save files:")
        if os.listdir(Session.save_directory): 
            for num, sf in enumerate(os.listdir(Session.save_directory)): 
               print(f"  {num+1}. {sf}")
        else:
            print("...")
        option = input("\nPress [n] to start a new session, or [l] to load a save file: ")
        if option in ['n', 'l']:
            if option == 'n':
                return cls(0,"0m")
            if option == 'l':
                save_select = int(input("Which save file? Enter a number: ")) - 1
                save_file = os.listdir(Session.save_directory)[save_select]
                save_file = os.path.join(Session.save_directory, save_file)
                with open(save_file, 'r') as file:
                    saved_session = yaml.safe_load(file)
                last_session = saved_session[-1]
                trackables = []
                for t in last_session['tracked_objects']:
                    new_tracked = Trackable(t['kind'], t['name'], t['total_turns'], t['turns_passed'])
                    trackables.append(new_tracked)
                return cls(last_session['turns'], last_session['time_passed'], last_session['rolls'], last_session['encounters'], trackables)

    def save_progress(self):
        progress_data = {
            "turns" : self.turns,
            "time_passed" : self.time_passed,
            "rolls" : list(self.rolls),
            "encounters" : list(self.encounters)
            }
        session_trackables = []
        for to in self.tracked_objects:
            if to.active:
                thing = { 
                    "kind" : to.kind, 
                    "name" : to.name, 
                    "turns_passed" : to.turns_passed, 
                    "total_turns" : to.total_turns 
                    }
                session_trackables.append(thing)
        progress_data["tracked_objects"] = session_trackables
        # update self object
        self.historical_data.append(progress_data)
        # save to file
        with open("saves/saved.yaml", 'w') as file:
            file.write(yaml.dump(self.historical_data))

    def load_progress(self):
        ...

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
        print(f"\nSpent Torches: {new_game.spent_torches()}")
        if new_game.tracked_objects:
            for to in new_game.tracked_objects:
                if to.kind != "spell":
                    to.print_meter()
        print(f"\nActive Spells:")
        if new_game.tracked_objects:
            for to in new_game.tracked_objects:
                if to.kind == "spell":
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
            user_keys = user_keys + s + "  "
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
    return(result)

def main():
    new_game = Session.start_session()
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
        if key == 's':
            spell_name = input("What spell has been cast? ")
            turns = int(input("How many turns will it last? "))
            spell = Trackable("spell",spell_name,turns)
            new_game.tracked_objects.append(spell)
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
            if dice > 1:
                monster += 's'
            new_game.encounters.append(f"{dice} {monster.title()}")
        # SAVE
        new_game.save_progress()
        # quit
        if key == 'q':
            q = input('Are you sure you want to quit? ')
            if q.lower() in ['y', 'ye', 'yes', 'ya', 'yup', 'yeah']:
                quit()
        if key == 'qy':
                quit()

main()
