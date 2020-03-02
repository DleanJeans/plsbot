# plsbot
Grind Dank Memer bot on Discord, using your computer to type the commands and a Discord bot to read the messages.

## Setup

### Downloading

1. Download and setup [Python.](https://www.python.org/downloads/)
2. [Download](https://github.com/DleanJeans/plsbot/archive/master.zip) or clone this repo.
3. Install prequisite Python libraries with command-line in the downloaded folder (type `cmd` in the address bar):
```
py -m pip install -r requirements.txt
```

### Meanwhile: Discord Server and Bot setup
4. Create a [private server.](https://support.discordapp.com/hc/en-us/articles/204849977-How-do-I-create-a-server-)
5. Create a channel for the automation (recommended name: `dank-memer`, change it in `.env` if you choose another name)
6. Create a [bot and invite it.](https://discordpy.readthedocs.io/en/latest/discord.html)
7. Copy the bot token to `BOT_TOKEN` inside `.env`

![](https://discordpy.readthedocs.io/en/latest/_images/discord_bot_user_options.png)

### After everything is setup
8. Run `plsbot.py` or `run.bat`, either should work

## Features
#### Auto-bet
Expand your bank capacity by spamming `pls bet` and `pls slots`. Default: 1 coin.

Comes with Martingale betting system (a bit risky!).

#### Auto-scout
Choose the best area, deposit all coins before in case of dying and withdraw some after (for auto-betting).

#### Auto-postmeme
Post memes and buy new laptop as long as you got 1000 coins in your balance.

#### Auto-sell
Use candy and boxes, clear collectables (breads, pills, cookies,...).

#### Auto-trivia
Answer trivia questions with 550+ already recorded. Disabled by default.

**WARNING**: running this might get you banned winning thousands of questions.

#### Bot commands
Toggle above features on the fly, recommended to run in another channel, run `.help` to see them.

### Advanced Settings
Check `.env`

- Bot prefix
- Click before typing (focusing)
- Channel name
- Flags for above features
- Items not for sale
- Items to `pls use` (instead of `pls sell`)
- Scouting areas priorities
- Bet amount and multipliers
- Cooldowns
