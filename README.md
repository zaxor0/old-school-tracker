# old-school-tracker
CLI tool for Old School TTRPGs

## Explanation of the Script
This script is intended to aid a Dungeon Master running an old school or OSR style RPG game where the "tracking of player turns" is necessary.

This script is specifically meant for the Basic / Expert versions of Dungeons and Dragons, or the modern version "Old School Essentials."

## Included Files

- `requirements.txt` this contains a list of all requred modules, which is just `pyyaml`
- `saves/` directory, to store any sessions from your DnD game, a sample session `borderlands.yml` is located within.
- `encounters.yaml` a sample set of encounter tables, where the monster is the key and the amount seen is the value, in `1d6` style formatting.

## Requirements
This requires yaml support, via the `pyyaml` module

### On Windows:
1. Get python, install via the manager, https://www.python.org/downloads
2. Make sure you have pip: `python3 -m ensurepip --upgrade`
3. Install the requirements via: `python3 -m pip install -r requirements.txt`

### On Ubuntu
On Ubuntu, install via the package manager:
`sudo apt install python3-pyyaml`

### Other OSes 
On OSes where the system does not manage python packages:
`pip3 install pyyaml` OR `pip3 install -r requirements.txt`


## How to use

- You need an `encounters.yaml` file, one is provided based on the first two level of "Keep on the Borderlands" this must be in the same directory.
- You need a `saves/` directory to save your sessions to.
- The program wont take any arguments, simply run with like `python3 old-school-tracker.py`
