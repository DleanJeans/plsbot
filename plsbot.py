import pyautogui
import random
import discord
import asyncio
import re
import math

from const import *

import multimer
import phonecontrol
import plstrivia
import plscout

from discord.ext import tasks, commands

bot = commands.Bot(BOT_PREFIX)
multimer = multimer.Multimer()
phonecontrol.add_to(bot, multimer)

multimer.set_flag(AUTOMATE, ENABLE_AUTOMATE)
multimer.set_flag(BET, AUTO_BETTING)
multimer.set_flag(SELL, AUTO_SELLING)
multimer.set_flag(SCOUT, AUTO_SCOUTING)
multimer.set_flag(TRIVIA, AUTO_TRIVIA)
multimer.set_flag(POSTMEMES, AUTO_POSTMEME)

message_history = []

automated_channel = None

@bot.event
async def on_message(msg):
    global automated_channel
    if not automated_channel:
        automated_channel = discord.utils.get(msg.channel.guild.channels, name=CHANNEL_NAME)
    await bot.process_commands(msg)

@bot.command()
async def history(context, index=1):
    await context.trigger_typing()
    history = await automated_channel.history(limit=index * 2).flatten()
    dank_history = list(filter(lambda m: m.author.name == DANK_MEMER, history))
    msg = dank_history[::-1][-index]
    await context.send(content=msg.content, embed=msg.embeds[0] if msg.embeds else None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(DANK_MEMER))
    print('Logged in as', bot.user)

def read_cooldown_from_message(message):
    if message.embeds:
        embed = message.embeds[0]
        if 'cooldown' not in embed.description:
            return 0
        match = re.search(COOLDOWN_PATTERN, embed.description).groups()
        minutes, seconds = map(lambda x: float(x) if x != None else 0, match)
        return minutes * 60 + seconds
    return 0

async def wait_for_cooldown(default):
    msg = await wait_for_message()
    if msg == TIMEOUT:
        return TIMEOUT
    elif msg.embeds:
        return read_cooldown_from_message(msg)
    return default

@tasks.loop(seconds=2.5)
async def automate():
    if not multimer.over(AUTOMATE):
        return

    if not bot.is_ready():
        await bot.wait_until_ready()

    if automated_channel:
        dank_bot = automated_channel.guild.get_member_named(DANK_MEMER)
        if dank_bot.status != discord.Status.online:
            return

    automate_order = [automate_trivia, automate_beg, automate_meme, automate_scout, automate_sell]

    try:
        for command in automate_order:
            await automate_bet()
            await play_event()
            await command()
            await play_event()
    except Exception as e:
        import traceback
        traceback.print_exc()

async def play_event():
    last_message = automated_channel.last_message
    match = re.findall('Type `(.+)`', last_message.content)
    if match:
        match = match[0].replace(INVISIBLE_TRAP, '')
        print('[Event] Type', match)
        await send(match)

plslots_amount = START_SLOTS
plsbet_amount = START_BET

last_balance = 0, 0

async def withdraw_enough(coins):
    global last_balance
    last_balance = await read_balance()
    wallet, bank = last_balance
    if coins == ALL:
        await withdraw(coins)
        return True
    elif wallet < coins and wallet + bank >= coins:
        await withdraw(coins - wallet)
        return True
    elif wallet + bank < coins:
        return False
    return True

async def automate_bet():
    if not multimer.over(BET): return

    global plsbet_amount, plslots_amount
    amounts = [plslots_amount, plsbet_amount]
    start_coins = [START_SLOTS, START_BET]
    
    zipped = zip(BET_GAMES, amounts, MULTIPLIERS_ON_LOST, start_coins)
    for game, bet_amount, multiplier, start_coin in zipped:
        if WITHDRAW_IF_NOT_ENOUGH_FOR_BET and not await withdraw_enough(bet_amount):
            bet_amount = start_coin
            if game == SLOTS and sum(last_balance) < plsbet_amount:
                break
            else:
                continue

        msg = await bank(game, bet_amount, msg_content='You', try_again_cooldown=True)


        if 'bluff' in msg.content:
            bet_amount = start_coin

        if multiplier == DEFAULT_MULTIPLIER: continue

        won = await read_won_status(msg)
        if won == WON:
            bet_amount = start_coin
        elif won in [LOST, TIE]:
            if multiplier == 2 and bet_amount >= 1024 and (bet_amount % 2 == 0 or bet_amount % 2.5 == 0):
                multiplier = 2.5
            bet_amount *= multiplier
            bet_amount = math.ceil(bet_amount)
            if bet_amount > MAX_BEFORE_RESET:
                bet_amount = start_coin
        
        if game == SLOTS:
            plslots_amount = bet_amount
        elif game == BET:
            plsbet_amount = bet_amount
    
    multimer.start(BET, BET_COOLDOWN)

async def read_won_status(msg):
    if TIE in msg.content: return TIE
    if msg.embeds:
        desc = msg.embeds[0].description
        while 'coins' not in desc:
            for c in ['*', '>', '<', ' ']:
                desc = desc.replace(c, '')
            for c in desc:
                if desc.count(c) > 1:
                    return WON
            return LOST
        for status in [WON, LOST]:
            if status in desc:
                return status

async def automate_trivia():
    if not multimer.over(TRIVIA): return
    
    while True:
        await pls(TRIVIA)
        msg = await wait_for_message(content=None, timeout=5)
        if msg == TIMEOUT or msg.embeds[0].author and TRIVIA not in msg.embeds[0].author.name:
            continue
        else:
            cooldown = read_cooldown_from_message(msg)
            if cooldown:
                multimer.start(TRIVIA, cooldown)
                return
        trivia = plstrivia.read(msg.embeds[0].description)
        break
    
    worth = plstrivia.read_worth(msg)

    print(f'\n[Trivia - {worth} coins]', trivia.question)
    answer = plstrivia.try_answer(trivia)
    print('[Answer Data]', answer)

    new_trivia = not answer
    if new_trivia or worth == 50:
        answer = random.randint(1, 4)
        if worth == 50:
            print('[Worth = 50] Randomizing')
    else:
        answer = trivia.answers.index(answer)
        if worth == 10:
            print('[Worth = 10] Avoiding option', answer)
            options = [i+1 for i in range(4) if i+1 != answer]
            answer = random.choice(options)
    await send(answer)
    
    multimer.start(TRIVIA, TRIVIA_COOLDOWN)

    msg = await wait_for_message(timeout=10)
    if new_trivia and msg != TIMEOUT:
        if TRIVIA_CORRECT in msg.content:
            trivia.correct_answer = trivia.answers[answer]
        elif TRIVIA_INCORRECT in msg.content:
            correct_answer = re.findall(TRIVIA_ANSWER_PATTERN, msg.content)[0]
            trivia.correct_answer = correct_answer
        plstrivia.log_new(trivia)

        print('[Correct Answer]', trivia.correct_answer)

async def automate_scout():
    if not multimer.over(SCOUT): return

    await deposit(ALL, try_again_cooldown=True)
    while True:
        await pls(SCOUT)
        area = await wait_for_best_scout_option()
        cooldown = SCOUT_COOLDOWN

        if area == TIMEOUT:
            continue
        elif type(area) is str:
            await send(area)
        elif type(area) is float:
            cooldown = area

        multimer.start(SCOUT, cooldown)
        break
    if AFTER_SCOUT_WITHDRAWAL == ALL:
        await withdraw(ALL)
    else:
        await withdraw_enough(AFTER_SCOUT_WITHDRAWAL)

async def wait_for_best_scout_option():
    msg = await wait_for_message(SEARCH)
    if msg == TIMEOUT:
        return TIMEOUT
    if msg.embeds:
        return read_cooldown_from_message(msg)
    else:
        areas = msg.content.split('\n')[1].replace('`', '').split(', ')
        area = plscout.choose_best_area(areas)
        return area

async def automate_meme():
    if not multimer.over(POSTMEMES): return
    
    while True:
        await pls(POSTMEMES)
        cooldown = await wait_for_meme_option(POSTMEME_COOLDOWN)
        if cooldown == TIMEOUT:
            continue
        elif cooldown == BUY_LAPTOP:
            if await withdraw_enough(LAPTOP_COST):
                await pls(BUY_LAPTOP)
                continue
            else:
                cooldown = POSTMEME_COOLDOWN
                break

        await send('d')
        break
    multimer.start(POSTMEMES, cooldown)

async def wait_for_meme_option(default):
    msg = await wait_for_message(MEME)
    if msg == TIMEOUT:
        return TIMEOUT
    elif msg.embeds:
        return read_cooldown_from_message(msg)
    elif NEED_LAPTOP in msg.content:
        return BUY_LAPTOP
    return default

async def automate_beg():
    if not multimer.over(BEG): return
    
    while True:
        await pls(BEG)
        cooldown = await wait_for_cooldown(BEG_COOLDOWN)
        if cooldown == TIMEOUT:
            continue
        break
    multimer.start(BEG, cooldown)

async def automate_sell():
    if not multimer.over(SELL): return
    
    while True:
        await pls(INVENTORY)
        msg = await wait_for_message(PLS + SHOP) # in case of empty inventory
        if msg == TIMEOUT:
            continue
        break
        
    items = msg.embeds[0].fields[0].value if msg.embeds else ''
    items = re.findall(INVENTORY_PATTERN, items)
    for count, item_name, item_type in items:
        if item_name in ITEMS_NOT_FOR_SALE:
            continue
        action = USE if item_name in ITEMS_TO_USE else SELL
        await bank(f'{action} {item_name}', count, msg_content='')
        break

    multimer.start(SELL, SELL_COOLDOWN)

async def read_balance():
    msg = await bank(BALANCE, try_again_cooldown=True)
    description = msg.embeds[0].description.replace(',', '')
    balances = re.findall(BALANCE_PATTERN, description)[0]
    balances = map(int, balances)
    return balances

async def withdraw(coins, try_again_cooldown=True):
    await bank(WITHDRAW, coins, msg_content=WITHDRAW, try_again_cooldown=try_again_cooldown)

async def deposit(coins, try_again_cooldown=True):
    await bank(DEPOSIT, coins, msg_content=DEPOSIT, try_again_cooldown=try_again_cooldown)

async def bank(action, amount='', timeout=3, msg_content=None, try_again_cooldown=False):
    while True:
        await pls(f'{action} {amount}')
        msg = await wait_for_message(msg_content, timeout)
        if msg == TIMEOUT:
            continue
        elif try_again_cooldown:
            cooldown = read_cooldown_from_message(msg)
            if cooldown:
                await asyncio.sleep(cooldown)
                continue
        break
    return msg

async def wait_for_message(content='', timeout=5, embed_author=''):
    def check(m):
        in_set_channel = m.channel.name == CHANNEL_NAME
        right_msg_content = content != None and content in m.content
        return in_set_channel and (right_msg_content or m.embeds)

    try:
        return await bot.wait_for('message', check=check, timeout=timeout)
    except:
        last_message = automated_channel.last_message
        if check(last_message):
            preview = read_message_preview(last_message)
            print('[TIMEOUT] Returning last message:\n', preview)
            return last_message
        return TIMEOUT

def read_message_preview(msg):
    if type(msg) is str: return msg
    preview = msg.content if msg.content else '[Embed]'
    if msg.embeds:
        title = msg.embeds[0].title
        author = msg.embeds[0].author
        if title:
            preview += ' ' + title
        elif author:
            preview += ' ' + author.name
    return preview

async def pls(action, wait=True):
    msg = PLS + action
    await send(msg, wait)
    
import mouse

async def send(content, wait=True):
    if CLICK_BEFORE_TYPING:
        mouse.steal()
        pyautogui.click(*CLICK_POSITION)
        mouse.restore()

    content = str(content).strip()
    pyautogui.typewrite(content)
    pyautogui.press('enter')
    if wait:
        await wait_for_message(content, timeout=None)

if __name__ == '__main__':
    automate.start()
    bot.run(BOT_TOKEN)