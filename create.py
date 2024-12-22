from sqlmodel import SQLModel, create_engine
from process import processPremiers, processRatings
from models import Premier, Genre, Rating, Search
from datetime import datetime

def dbConnect():
        engine = create_engine("sqlite:///database.db")
        SQLModel.metadata.create_all(engine)
        return engine

def createPremier(session, start, days):
    ratings = processRatings()
    for premier in processPremiers(start, days):
        premierDb = Premier(
            firstAired = datetime.fromisoformat(premier["firstAired"]).date() if premier["firstAired"] else None,
            premierDate = datetime.fromisoformat(premier["premierDate"]).date(),
            season = premier["season"],
            premierType = premier["premierType"],
            title = premier["title"],
            year = premier["year"],
            traktId = premier["traktId"],
            imdbId = premier["imdbId"],
            overview = premier["overview"],
            country = premier["country"],
            trailer = premier["trailer"],
            language = premier["language"]
        )
        session.add(premierDb)
        session.commit()
        for genre in premier["genres"]:
            session.add(
                Genre(
                genre = genre,
                premier = premierDb.id
                )
            )
        try:
            session.add(
                Rating(
                    rating = ratings[premierDb.imdbId]["rating"],
                    premier = premierDb.id
                )
            )
        except KeyError:
            pass

def createSearch(session, start, end):
    session.add(
        Search(
            start = start,
            end = end
        )
    )
if __name__ == "__main__":
    pass

# with open("2.json", "r") as f:
#     shows = json.load(f)

# for show in shows:
#     dbShow = Show(
#         title = show["title"],
#         traktId = show["traktId"],
#         imdbId = show["imdbId"],
#         country = show["country"],
#         language = show["language"]
#     )
#     dbShow.save()
#     dbPremier = Premier(
#         show = dbShow,
#         season = show["season"],
#         airTime = show["airTime"],
#         type = show["type"])
#     dbPremier.save()
#     for genre in show["genres"]:
#         dbGenre = Genre(
#             show = dbShow,
#             genre = genre
#             )
#         dbGenre.save()

# def createRatings():
#     shows = processRatings()
#     with db.atomic():
#         for batch in chunked(shows, 32766 // 3):
#             Rating.insert_many(batch).execute()