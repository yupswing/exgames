#!/usr/bin/env python3

from lib.library import Library
import sys

if len(sys.argv) == 1:
    print("No steamid/gogid selected")
    sys.exit()

# params
steamId = sys.argv[1]
gogId = sys.argv[1]
loadFromCache = False
ignoreZeroPlaytime = False # useful to filter DLCs

# execution
l = Library()

print("# Loading Steam...")
l.loadSteam(steamId, {"loadFromCache": loadFromCache,
                      "ignoreZeroPlaytime": ignoreZeroPlaytime})

print("# Loading GOG...")
l.loadGOG(gogId, {"loadFromCache": loadFromCache,
                  "ignoreZeroPlaytime": ignoreZeroPlaytime})

print('-----')
l.print_listgames()
l.print_achievements()
l.print_stats()

# for k, game in l.games.items():
#   print(game.title)
