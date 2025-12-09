#!/usr/bin/python3
import os
import random
import yaml
# import specific module based on OS
if os.name == 'nt':
    import msvcrt
else:
    import tty, termios, sys

# load encounter tables file
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
        turn_lifespans = { "torch" : 6, "lantern" : 24, "spell" : turns }
        return turn_lifespans[self.kind]

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

    def return_dict(self):
        return { "kind" : self.kind, "name" : self.name, "turns_passed" : self.turns_passed, "total_turns" : self.total_turns }

# umbrella to hold all the objects and time passed
class Session():
    save_directory = "saves"
    def __init__(self, save_file, turns=1, time_passed='0m', rolls=None, encounters=None, tracked_objects=None, progress=None, messages=None):
        self.save_file = os.path.join(self.save_directory, save_file)
        self.turns = turns
        self.time_passed = time_passed
        # pythonic way to assign empty array if value is None
        self.rolls = [] if not rolls else rolls 
        self.encounters = [] if not encounters else encounters
        self.tracked_objects = [] if not tracked_objects else tracked_objects
        self.progress = [] if not progress else progress
        self.messages = [ "Welcome to your new session" ] if not messages else messages 
        self.redo = {}

    def update_time(self):
        self.turns += 1
        # time not counting the current turn
        t = self.turns - 1
        hours = (t * 10) // 60
        minutes = (t * 10) % 60
        if t < 6:
            self.time_passed = f"{minutes}m"
        else:
            self.time_passed = f"{hours}h {minutes}m"
        # update objects turn counters
        for to in self.tracked_objects:
            to.update_turns()
    
    def new_light_source(self):
        kind = input("Are you lighting a [t]orch or a [l]antern? ")
        if kind in ['t','l']:
            if kind == 'l':
                kind = 'lantern'
            if kind == 't':
                kind = 'torch'
            light_source= Trackable(kind)
            self.tracked_objects.append(light_source)
            self.messages.append(f"You lit a {kind}.")

    def encounter_check(self):
        print("Encounter Tables:")
        tables = list(encounter_table.keys())
        for n,table in enumerate(encounter_table):
            print(f"  {n+1}. {table}")
        selection = int(input("Which table to roll on? ")) - 1
        selected_table = tables[selection]
        encounter = random.choice(encounter_table[selected_table])
        monster = list(encounter.keys())[0]
        dice = encounter[monster]
        dice = self.roll_dice(int(dice.split('d')[0]), int(dice.split('d')[1]))
        if dice > 1:
            monster += 's'
        encounter_text = f"{dice} {monster.title()}"
        self.encounters.append(encounter_text)
        self.messages.append(f"Encounter with {encounter_text}!")

    def cast_spell(self):
        spell_name = input("What spell has been cast? ")
        turns = int(input("How many turns will it last? "))
        spell = Trackable("spell",spell_name,turns)
        self.tracked_objects.append(spell)
        self.messages.append(f"The spell {spell_name} was cast!")

    def spent_torches(self):
        st = 0
        for to in self.tracked_objects:
            if to.kind == "torch" and to.active == False:
                st += 1
        return st

    def roll_dice(self, count, sides):
        return sum(random.randint(1,sides) for _ in range(count))

    def user_roll_dice(self):
        dice = input('What would you like to roll, in 1d6 format? ')
        if 'd' in dice:
            count = int(dice.split('d')[0])
            sides = int(dice.split('d')[1])
            result = self.roll_dice(count, sides)
            self.rolls.append(result)
        self.messages.append(f"{dice} dice were rolled with a result of {result}.")

    def undo_turn(self):
        self.redo = self.progress.pop()
        last_turn = self.progress[-1]
        self.load_turn_dict(last_turn)
        self.messages.append(f"You just undid your last turn, you can redo that turn by pressing [r]")

    def load_turn_dict(self, new_turn):
        self.turns = new_turn['turns'] 
        self.time_passed = new_turn['time_passed'] 
        self.rolls = new_turn['rolls']
        self.encounters = new_turn['encounters']
        self.tracked_objects = []
        for t in new_turn['tracked_objects']:
            new_tracked = Trackable(t['kind'], t['name'], t['total_turns'], t['turns_passed'])
            self.tracked_objects.append(new_tracked)

    @classmethod
    def start_session(cls):
        while True:
            UserInterface.clear()
            print("Welcome to the Old School Tracker\n") 
            print("Available save files:")
            save_file_options =[]
            if os.listdir(Session.save_directory): 
                for num, sf in enumerate(os.listdir(Session.save_directory)): 
                    save_file_options.append(num)
                    print(f"  {num+1}. {sf}")
            else:
                print("...")
            option = input("\nPress [n] to start a new session, or [l] to load a save file: ")
            if option == 'n':
                sf = input("Starting a new session!\nWhat should we name this save file? " ) + '.yml'
                return cls(sf, 0,"0m")
            if option == 'l':
                save_num = int(input("Which save file number? ")) - 1
                save_file_name = os.listdir(Session.save_directory)[save_num]
                save_file_to_load = os.path.join(Session.save_directory, save_file_name)
                with open(save_file_to_load, 'r') as file:
                    saved_session = yaml.safe_load(file)
                last_sess = saved_session[-1]
                trackables = []
                for t in last_sess['tracked_objects']:
                    new_tracked = Trackable(t['kind'], t['name'], t['total_turns'], t['turns_passed'])
                    trackables.append(new_tracked)
                return cls(save_file_name, last_sess['turns'], last_sess['time_passed'], last_sess['rolls'], last_sess['encounters'], trackables, saved_session)
            else:
                input("Not an option, press any key")
            
    def save_progress(self):
        turn_data = {
            "turns" : self.turns,
            "time_passed" : self.time_passed,
            "rolls" : list(self.rolls),
            "encounters" : list(self.encounters),
            "tracked_objects" : []
            }
        for tracked in self.tracked_objects:
            if tracked.active:
                tracked_dict = tracked.return_dict()
                turn_data["tracked_objects"].append(tracked_dict)
        # update self object
        self.progress.append(turn_data)
        # save to file as yaml
        with open(self.save_file, 'w') as file:
            file.write(yaml.dump(self.progress))

    def quit_game(self):
        q = input('Are you sure you want to quit? ')
        if q.lower() in ['y', 'ye', 'yes', 'ya', 'yup']:
            self.save_progress()
            quit()

# Terminal User Interface
class UserInterface():
    def __init__(self):
        self.heading = "Old School Turn Tracker"

    def main_screen(self,session):
        self.clear()
        title_box = self.text_box(self.heading)
        print(title_box)
        print(f"Time passed:  {session.time_passed}")
        print(f"Current turn: {session.turns}")
        print(f"\nSpent Torches: {session.spent_torches()}")
        if session.tracked_objects:
            for to in session.tracked_objects:
                if to.kind != "spell":
                    to.print_meter()
        print(f"\nActive Spells:")
        if session.tracked_objects:
            for to in session.tracked_objects:
                if to.kind == "spell":
                    to.print_meter()
        print(f"\nEncounters: {session.encounters}")
        print(f"\nRolls made: {session.rolls}")
        print(f"\nLog:\n  {session.messages[-1]}\n")

    def user_input(self, session):
        user_keys = {
            'd' : {'menu' : '[d]ice roll',        'function' : session.user_roll_dice   },
            't' : {'menu' : '[t]urn passed',      'function' : session.update_time      },
            'n' : {'menu' : '[n]ew light source', 'function' : session.new_light_source },
            'e' : {'menu' : '[e]ncounter check',  'function' : session.encounter_check  },
            's' : {'menu' : '[s]pell',            'function' : session.cast_spell       },
            'u' : {'menu' : '[u]ndo last action',   'function' : session.undo_turn        },
            'q' : {'menu' : '[q]uit',             'function' : session.quit_game        }
        }
        # print keys the user can press to interact with the game
        for k in user_keys:
            print(f"{user_keys[k]['menu']}  ", end='')
        print()
        key = self.getch()
        if key == 'r' and session.redo:
            session.load_turn_dict(session.redo)
            session.redo = {}
        elif key in user_keys.keys():
            user_keys[key]['function']()
            session.save_progress()
        else:
            session.messages.append(f"The key {key} is not a valid key")

    @classmethod
    def clear(self):
        clear = 'clear'
        if os.name == 'nt':
            clear = 'cls'
        os.system(clear)

    # I got this function from https://gist.github.com/jfktrey/8928865, but I need to test it on a windows machine
    def getch(self):
        if os.name == 'nt':
            return bytes.decode(msvcrt.getch())
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def text_box(self, text):
        w = '-' * len(text)
        line = '+-' + w + '-+'
        box = line + '\n' + '| ' + text + ' |\n' + line
        return box

# main function to run the program
def main():
    new_game = Session.start_session()
    ui = UserInterface()
    while True:
        ui.main_screen(new_game)
        ui.user_input(new_game)

main()
