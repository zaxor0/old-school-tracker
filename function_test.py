#!/usr/bin/python3

def func1():
    return 'green is or'

test_dict = { 
    'h' : { 'text' : 'Hello!', 'func' : func1 }, 
    'w' : { 'text' : 'Welcome!' }, 
    }

for letter in test_dict:
    print(f"{letter}, {test_dict[letter]['text']}")

# ok so after some testing, you can do this thing but the function refernce in the test dict CANNOT include the () as that calls it
print(test_dict['h']['func']())
