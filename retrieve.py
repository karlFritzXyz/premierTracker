from urllib.request import Request, urlopen
from datetime import date
from dotenv import load_dotenv
import os

def retrievePremiers(start, days):
    load_dotenv()
    apiKey = os.getenv("API_KEY")
    headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': apiKey
    }
    request = Request(f'https://api.trakt.tv/calendars/all/shows/premieres/{start.strftime("%Y-%m-%d")}/{days}?extended=full', headers = headers)
    responseBody = urlopen(request).read()
    return responseBody

def retrieveRatings():
    request = Request("https://datasets.imdbws.com/title.ratings.tsv.gz")
    responseBody = urlopen(request).read()
    return responseBody

if __name__ == "__main__":
    # print(retrieveRatings())
    # print(retrieveShows(date(2020, 1, 1), 5))
    pass