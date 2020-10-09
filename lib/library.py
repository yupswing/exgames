from enum import Enum, auto
import dateutil.parser
import dateutil.tz
from datetime import datetime
import re
from lib.hubs import steam, gog
from lib.guid import makeGuid


class Store(Enum):
    STEAM = "Steam"
    GOG = "GOG"


class Library(object):
    def __init__(self):
        self.__games = {}  # {title:Game,...}

    def print_stats(self):
        print()
        print("# Statistics")
        stats = {'playtime': sum(game.playtime for game in self.__games.values()),
                 'games': len(self.__games.keys())}
        print("  %d games" % stats['games'])
        print("  %d hours played" % (stats['playtime']/60))
        return stats

    def print_achievements(self):
        print()
        print("# Achievements completion")
        games = [game for game in self.__games.values() if game.achievements]
        games = sorted(games, key=lambda k: k.achievements, reverse=True)
        for game in games:
            print("  % 4d%% %s" % (game.achievements, game.title))
        return games

    def print_listgames(self):
        print()
        print("# Games")
        i = 0
        # [game for game in self.__games.values() if game.playtime]
        games = self.__games.values()
        games = sorted(games, key=lambda k: (
            k.playtime, k.title), reverse=True)
        for g in games:
            i += 1
            playtime = g.playtime
            print("  % 4d - % 4d:%02d - %s - %s" % (i,
                                                    g.playtime/60,
                                                    g.playtime % 60,
                                                    g.title,
                                                    [k.name for k in g.stores.keys()]))
        return games

    def getGame(self, title=None, guid=None):
        if not title and not guid:
            return None
        if not guid:
            guid = makeGuid(title)
        return self.__games.get(guid, None)

    def __load(self, id, params, method, store):
        result = method(id, params)
        if not result[0]:
            print("  ERROR: %s" % result[1])
            return
        addgames = result[1]
        for addgame in addgames:
            game = self.getGame(title=addgame['title'])
            if game:
                game.addStore(store, addgame)
            else:
                game = Game(addgame['title'])
                game.addStore(store, addgame)
                self.__games[game.guid] = game

    def loadSteam(self, id, params):
        self.__load(id, params, steam.get, Store.STEAM)

    def loadGOG(self, id, params):
        self.__load(id, params, gog.get, Store.GOG)

    @property
    def games(self):
        return self.__games


class Game(object):

    def __init__(self, title):
        self.__title = title
        self.__guid = makeGuid(title)
        # {Store:{id:ID,url:URL,logo:URL,playtime:INT,achievements:BOOL,last_session:DATETIME}}
        self.__stores = {}

    def addStore(self, store, data):

        new_data = {"id": data.get('id'),
                    "url": data.get('url'),
                    "logo": data.get('logo'),
                    # 0-100 or NONE
                    "achievements": data.get('achievements', None),
                    "playtime": int(data.get('playtime', 0)),
                    "last_session": data.get('last_session', None)
                    }

        old_data = self.__stores.get(store)
        if old_data:
            # game with the same name and same store already present
            # prioritize playtime
            warning = {
                'title': self.title,
                'store': store,
                'oldId': old_data.get('id'),
                'newId': new_data.get('id')
            }
            if old_data.get('playtime', 0) >= new_data.get('playtime', 0):
                # keep old data, higher playtime
                print("  WARNING: Duplicate '%(title)s'\n           ID:%(newId)s in store '%(store)s' is ignored; kept previous entry ID:%(oldId)s" % warning)
                return # exit to keep
            else:
                # use new data, higher playtime
                print("  WARNING: Duplicate '%(title)s'\n           ID:%(newId)s in store '%(store)s' has overwritten previous entry ID:%(oldId)s" % warning)
                # continue to overwrite

        self.__stores[store] = new_data

    @ property
    def guid(self):
        return self.__guid

    @ property
    def title(self):
        return self.__title

    @ property
    def achievements(self):
        try:
            return next(item['achievements'] for item in self.stores.values() if item['achievements'] is not None)
        except:
            return None

    @ property
    def stores(self):
        return self.__stores

    @ property
    def playtime(self):
        return sum(int(item['playtime']) for item in self.stores.values() if item['playtime'] is not None)

    @ property
    def last_session(self):
        return max(item['last_session'] for item in self.stores.values() if item['last_session'] is not None)
