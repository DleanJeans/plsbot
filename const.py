DANK_MEMER = 'Dank Memer'

SEARCH = 'search?'

TIMEOUT = 'timeout'
BUY_LAPTOP = 'buy laptop'
MEME = 'meme'
NEED_LAPTOP = 'oi'
TRIVIA_CORRECT = 'earned'
TRIVIA_INCORRECT = 'correct answer'

ALL = 'all'
PLS = 'pls '
BEG = 'beg'
SCOUT = 'scout'
POSTMEMES = 'pm'
BET = 'bet'
SLOTS = 'slots'
INVENTORY = 'inv'
SELL = 'sell'
USE = 'use'
BALANCE = 'bal'
TRIVIA = 'trivia'
SHOP = 'shop'
WITHDRAW = 'withdraw'
DEPOSIT = 'deposit'

INVISIBLE_TRAP = '﻿'
AUTOMATE = 'automate'
TIE = 'tie'
WON = 'won'
LOST = 'lost'
COINS = 'coins'

LAPTOP_COST = 1000

COLLECTABLE = 'Collectable'
INVENTORY_PATTERN = '(\d+)\\n\*ID\* `(\w+)` ─ (\w+)'
COOLDOWN_PATTERN = '\*+(?:(\d)m)?(?: and )?(?:([0-9.]+) *\w+)?\*+'
TRIVIA_ANSWER_PATTERN = '`([^`]+)`' 
BALANCE_PATTERN = '(\d+)\s.+ (\d+)'

from dotenv import dotenv_values

def try_convert(value, classtype):
    try: value = classtype(value)
    except: pass
    return value

def try_convert_bool(value):
    if type(value) == str:
        if value.lower() == 'on':
            value = True
        elif value.lower() == 'off':
            value = False
    return value

def try_convert_const(value):
    value = value.strip()
    if value.isdigit():
        value = int(value)
    else:
        value = try_convert(value, float)
    if ',' in str(value):
        value = list(map(str.strip, value.split(',')))
    value = try_convert_bool(value)
    return value

for key, value in dotenv_values().items():
    value = try_convert_const(value)
    globals()[key] = value

OTHERS = 'others'
SCOUT_AREA_PROSPECTS.append(OTHERS)
SCOUT_AREA_RISKS.append(OTHERS)
SCOUT_AREA_PROSPECTS = SCOUT_AREA_PROSPECTS[::-1]
SCOUT_AREA_RISKS = SCOUT_AREA_RISKS[::-1]
CLICK_POSITION = list(map(int, CLICK_POSITION))

BET_GAMES = [SLOTS, BET]
MULTIPLIERS_ON_LOST = [MULTIPLY_ON_SLOTS_LOST, MULTIPLY_ON_BET_LOST]
DEFAULT_MULTIPLIER = 1