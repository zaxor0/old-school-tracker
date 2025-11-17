#!/usr/bin/python3
import os
import random
import yaml

heading = "Old School Turn Tracker"

with open('encounters.yaml','r') as f:
    encounter_table = yaml.safe_load(f)

def clear():
    clear = 'clear'
    if os.name == 'nt':
        clear = 'cls'
    os.system(clear)

def text_box(text):
    w = '-' * len(text)
    line = '+-' + w + '-+'
    box = line + '\n' + '| ' + text + ' |\n' + line
    return box

def time_passed(t):
    t -= 1
    hours = (t * 10) // 60
    minutes = (t * 10) % 60
    if t < 6:
        return f"{minutes}m"
    else:
        return f"{hours}h {minutes}m"

def diceRoll(dieCount,dieSides):
    result = 0
    for i in range(dieCount):
        roll = random.randint(1,dieSides)
        result += roll
    return(result)

def torch_ascii(t):
    turns_passed = (t - 1) % 6
    turns_left = 6 - turns_passed
    torch = '[' + (turns_passed * '.') + (turns_left * '|') +']'
    return 'Torchlight:  ' + torch

def main():
    turns = 1
    rolls = []
    while True:
        clear()
        print(text_box(heading))
        time = time_passed(turns)
        print(f"Time passed:  {time}")
        print(f"Current turn: {turns}")
        print(torch_ascii(turns))
        print()
        print(f"Rolls made: {rolls}")
        if rolls:
            print(f"Last roll: {rolls[-1]}")
        else:
            print()
        print()
        print(f"[t]urn passed    [n]ew torch    [d]ice roll   [e]ncounter check    [q]uit")
        key = input(f"Enter a key: ")
        if key == 't':
            turns += 1
        if key == 'n':
            print('new torch')
        if key == 'd':
            dice = input('What would you like to roll, in 1d6 format? ')
            if 'd' in dice:
                count = int(dice.split('d')[0])
                sides = int(dice.split('d')[1])
                rolls.append(diceRoll(count,sides))
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
            dice = diceRoll(int(dice.split('d')[0]), int(dice.split('d')[1]))
            input(f"{dice}, {monster}")
        if key == 'q':
            q = input('Are you sure you want to quit?')
            if q.lower() in ['y', 'ye', 'yes', 'ya', 'yup', 'yeah']:
                quit()

main()
