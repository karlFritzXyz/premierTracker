from json import loads
from gzip import decompress
from retrieve import retrieveRatings, retrievePremiers
from datetime import datetime, timedelta

def processPremiers(start, days):
    premiers = loads(retrievePremiers(start, days))
    premierData = []
    for premier in premiers:
        premierData.append(
            {
                "firstAired":premier["show"]["first_aired"],
                "premierDate":premier["episode"]["first_aired"],
                "season": premier["episode"]["season"],
                "premierType": premier["episode"]["episode_type"],
                "title": premier["show"]["title"],
                "year": premier["show"]["year"],
                "traktId": premier["show"]["ids"]["trakt"],
                "imdbId": premier["show"]["ids"]["imdb"],
                "overview": premier["show"]["overview"],
                "country": premier["show"]["country"],
                "trailer": premier["show"]["trailer"],
                "language": premier["show"]["language"],
                "genres": premier["show"]["genres"],
            }
        )
    return premierData

def processRatings():
    shows = decompress(retrieveRatings()).decode().split("\n")[1:-1]
    return {show.split("\t")[0]:{"rating": show.split("\t")[1], "votes": show.split("\t")[2]} for show in shows}

if __name__ == "__main__":
    # print(processRatings())
    # print(processPremiers(datetime.strptime("01-11-2024", "%d-%m-%Y").date(), timedelta(days = 1)))
    pass