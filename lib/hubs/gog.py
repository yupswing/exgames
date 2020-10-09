import requests
import json
import dateutil
import os.path

# GOG
# v = {"game":
# {"id":"1495134320",
# "title":"The Witcher 3: Wild Hunt - Game of the Year Edition",
# "url":"\/game\/the_witcher_3_wild_hunt_game_of_the_year_edition",
# "achievementSupport":true,
# "image":"https:\/\/images.gog.com\/7b5017a1e70bde6e4129aeb6770e77bc9798bc2f239cde2432812d0dbdae9fe1.png"},
# "stats":{"46988294404410132":{"achievementsPercentage":61,
#                               "playtime":7250,
#                               "lastSession":"2018-10-11T19:26:14+00:00"}}}

# id = GOG USER ID
# params = {
#     "loadFromCache": False, # load data from cached results
#     "ignoreZeroPlaytime": False, # ignores games with 0 minutes playtime
# }

def get(id=None, params={}):

    page = 1
    data = []

    while True:
        result = getpage(id, page, params)
        # print(result)
        if not result[0]:
            if page == 1:
                # first page error is a real error
                return result
            break
        data.extend(result[1])
        page += 1

    if len(data) == 0:
        return [False, "Is your profile public?"]

    return [True, data]


def getpage(id, page, params):

    # params
    loadFromCache = params.get('loadFromCache', False)
    ignoreZeroPlaytime = params.get('ignoreZeroPlaytime', False)

    # ---
    cache_filename = os.path.join("cache", "data_gog_page%s" % page)

    if loadFromCache:
        if not os.path.isfile(cache_filename):
            return [False, "File not found"]
        print(" - %s" % cache_filename)
        with open(cache_filename, 'r') as file:
            contents = file.read()
    else:
        try:
            url = 'https://www.gog.com/u/%(id)s/games/stats?sort=total_playtime&order=desc&page=%(page)d' % {
                "id": id, "page": page}
            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
            print(" - %s" % url)
            r = requests.get(url, headers=headers)
        except:
            return [False, "No connection"]

        if r.status_code == 200:
            contents = r.text
        else:
            return [False, "Status %s (Response is not 200)" % r.status_code]

        text_file = open(cache_filename, "wb")
        text_file.write(contents.encode('ascii', 'ignore'))
        text_file.close()

    # print(contents)

    # ---

    data = []
    data_json = contents
    data_json = json.loads(data_json.strip().lstrip("=").rstrip(";").strip())
    for data_json_current in data_json["_embedded"]["items"]:
        if "game" in data_json_current:
            box = data_json_current["game"]
        else:
            continue
        title = box['title'].encode('ascii', 'ignore').decode('ascii').strip()

        stats = data_json_current.get("stats", None)
        playtime = 0
        achievements = None
        last_session = None
        if stats:
            stats = next(value for key, value in stats.items())
            last_session = stats.get("lastSession", None)
            if last_session:
                last_session = dateutil.parser.parse(last_session[:19]+"Z")
            else:
                last_session = None
            playtime = int(stats.get("playtime", 0))  # minutes
            achievements = stats.get("achievementsPercentage", None)
            if achievements:
                achievements = int(achievements)

        if playtime == 0 and ignoreZeroPlaytime:
            # print("rejected because 0 playtime: %s" % title)
            continue

        game_data = {
            "id": str(box['id']).strip(),
            "title": title,
            "logo": str(box.get('image', '')),
            "url": str(box.get('url')),
            "achievements": achievements,
            "playtime": playtime,  # minutes
            "last_session": last_session  # datetime
        }
        # print(game_data)
        data.append(game_data)

    return [True, data]
