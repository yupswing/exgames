import requests
import json
from datetime import datetime
import dateutil.tz
import os.path

# STEAM
# {"appid":440,
#  "name":"Team Fortress 2",
#  "logo":"https:\/\/steamcdn-a.akamaihd.net\/steamcommunity\/public\/images\/apps\/440\/07385eb55b5ba974aebbe74d3c99626bda7920b8.jpg",
#  "has_adult_content":1,
#  "friendlyURL":"TF2",
#  "availStatLinks": {"achievements":true,
#                     "global_achievements":true,
#                     "stats":true,
#                     "gcpd":true,
#                     "leaderboards":true,
#                     "global_leaderboards":true},
#  "hours_forever":"873",
#  "last_played":1535795203},

# id = STEAM USER ID
# params = {
#     "loadFromCache": False, # load data from cached results
#     "ignoreZeroPlaytime": False, # ignores games with 0 minutes playtime
# }


def get(id=None, params={}):

    # params
    loadFromCache = params.get('loadFromCache', False)
    ignoreZeroPlaytime = params.get('ignoreZeroPlaytime', False)

    cache_filename = os.path.join("cache", "data_steam")

    if loadFromCache:
        if not os.path.isfile(cache_filename):
            return [False, "File not found"]
        print(" - %s" % cache_filename)
        with open(cache_filename, 'r') as file:
            contents = file.read()
    else:
        try:
            url = 'https://steamcommunity.com/id/%s/games/?tab=all' % id
            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
            print(" - %s" % url)
            r = requests.get(url, headers=headers)
        except:
            return [False, "No connection"]

        if r.status_code == 200:
            contents = r.text
        else:
            return [False, "%s Status (Response is not 200)" % r.status_code]

        # ---

        text_file = open(cache_filename, "wb")
        text_file.write(contents.encode('ascii', 'ignore'))
        text_file.close()

    # ---

    if "<title>Steam Community :: Error</title>" in contents:
        return [False, "SteamID not found"]

    if '<div class="profile_private_info">' in contents:
        return [False, "Private profile"]

    first = "var rgGames"
    last = "var rgChangingGames"

    try:
        start = contents.index(first) + len(first)
        end = contents.index(last, start)
    except:
        return [False, "Parsing Error"]

    data = []
    data_json = contents[start:end]
    data_json = json.loads(data_json.strip().lstrip("=").rstrip(";").strip())
    for box in data_json:
        title = box['name'].encode('ascii', 'ignore').decode('ascii').strip()
        last_played = box.get("last_played", None)
        # if last_played is None:
        # print("rejected %s" % title)
        # continue
        if last_played and last_played > 1000000000:
            # sometimes data is missing, sometimes is 86400 (1 day after 1/1/1970)
            last_played = datetime.fromtimestamp(
                int(last_played)).replace(tzinfo=dateutil.tz.UTC)

        playtime = int(float(box.get('hours_forever', 0))*60)  # minutes

        if playtime == 0 and ignoreZeroPlaytime:
            # print("rejected because 0 playtime: %s" % title)
            continue

        game_data = {
            "id": str(box['appid']).strip(),
            "title": title,
            "logo": str(box.get('logo', '')),
            "url": "" + str(box.get('friendlyURL')),
            "playtime": playtime,
            "last_session": last_played  # datetime
        }
        # print(game_data)
        data.append(game_data)

    if len(data) == 0:
        return [False, "Profile is empty or private"]

    return [True, data]
