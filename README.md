# Info

Retrive game statistics (how many games, playtime for each, achievements percentage [only GOG]...) from Steam and GOG public profiles.

This is just a proof of concept, you can build on top whatever you need :)

# Requirements

python: version 3.x

```sh
pip3 install -r requirements.txt
```

# Launch

```sh
python3 pyexgame.py USERNAME
```

-   where USERNAME is SteamID and GOG ID (if you want to use two different ID just hack the code in `pyexgame.py`)
-   be sure you've set your steam and gog profile as `Public` or you will not get any data.

# How to get your ID

-   Open your profile on GOG
-   Your ID is written in the url
    -   https://www.gog.com/u/**USERNAME**

-   Open your profile on Steam
-   Your ID is written in the url
    -   https://steamcommunity.com/id/**USERNAME**/games/
