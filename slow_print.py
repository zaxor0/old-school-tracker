#!/usr/bin/python3
from os import sys
import time

some_string = f"hello world!"

def slow_print(*text, end='\n'):
    for word in text:
        for letter in word:
            sys.stdout.write(letter)
            sys.stdout.flush()
            time.sleep(.015)
    sys.stdout.write(end)


slow_print(some_string, end='')
