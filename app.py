from textual.app import App, ComposeResult
from textual.widgets import Input, Pretty, Label, Button, DataTable, SelectionList
from textual import on
from textual.validation import Function
from datetime import datetime, timedelta, date
from create import dbConnect
from sqlmodel import Session, select
from textual.events import Mount
from textual.widgets.selection_list import Selection
import portion as P
from create import createPremier, createSearch
from models import Premier, Genre, Search, Rating
import csv

class myApp(App):
    def compose(self) -> ComposeResult:
        yield Pretty([], id = "format")
        yield Input(id = "date1", placeholder = "DD-MM-YYYY", validators = [Function(isDate, "Date format not valid")])
        yield Input(id = "date2", placeholder = "DD-MM-YYYY", validators = [Function(isDate, "Date format not valid")])
        yield Button("Retrieve", disabled = True)
        yield SelectionList(id = "countries")
        yield SelectionList(id = "languages")
        yield SelectionList(id = "genres")
        yield DataTable()
        yield Button("Export", id = "export", disabled = True)

    @on(Mount)
    def initialView(self, event: Mount):
        self.date1 = None
        self.date2 = None
        self.columnKeys = self.query_one(DataTable).add_columns(*["firstAired", "premierDate", "season", "title", "year", "country", "language", "rating"])
        self.rowKeys = []
        self.query_one(Pretty).update("Enter start and end dates")

    @on(Input.Changed)
    def vaildateDates(self, event: Input.Changed) -> None:
        date1 = self.query_one("#date1")
        date2 = self.query_one("#date2")
        pretty = self.query_one(Pretty)
        button = self.query_one(Button)
        if event.input.id == "date1":
            if not event.validation_result.is_valid:
                pretty.update(event.validation_result.failure_descriptions)
                self.date1 = None
                button.disabled = True
            else:
                self.date1 = datetime.strptime(event.value, "%d-%m-%Y").date()
                pretty.update("Enter start and end dates")
        if event.input.id == "date2":
            if not event.validation_result.is_valid:
                pretty.update(event.validation_result.failure_descriptions)
                self.date2 = None
                button.disabled = True
            else:
                self.date2 = datetime.strptime(event.value, "%d-%m-%Y").date()
                pretty.update("Enter start and end dates")
        if self.date1 != None and self.date2 != None and areOrdered(self.date1, self.date2):
            pretty.update("Success!")
            button.disabled = False
        if self.date1 != None and self.date2 != None and not areOrdered(self.date1, self.date2):
            pretty.update("Start date must be less than end date")
            button.disabled = True
    
    @on(Button.Pressed)
    def selectButton(self, event: Button.Pressed) -> None:
        if event.button.id == "export":
            self.exportData()
        else:
            self.importData()

    def importData(self):
        minn = date.max
        maxx = date.min
        day = timedelta(days = 1)
        intervals = []
        engine = dbConnect()
        with Session(engine) as session:
            for search in session.exec(select(Search)):
                minn = min(minn, search.start)
                maxx = max(maxx, search.end)
            if minn == datetime.max or maxx == datetime.min:
                createSearch(session, self.date1, self.date2)
                intervals.append([self.date1, self.date2])
            elif self.date2 == minn:
                createSearch(session, self.date1, self.date2 - day)
                intervals.append([self.date1, self.date2 - day])
            elif self.date2 < minn:
                createSearch(session, self.date1, self.date2)
                intervals.append([self.date1, self.date2])
            elif self.date1 == maxx:
                createSearch(session, self.date1 + day, self.date2)
                intervals.append([self.date1 + day, self.date2])
            elif self.date1 > maxx:
                createSearch(session, self.date1, self.date2)
                intervals.append([self.date1, self.date2])
            elif self.date1 >= minn and self.date2 <= maxx:
                pass
            elif self.date1 < minn and self.date2 <= maxx:
                createSearch(session, self.date1, minn - day)
                intervals.append([self.date1, minn - day])
            elif self.date2 > maxx and self.date1 >= minn:
                createSearch(session, maxx + day, self.date2)
                intervals.append([maxx + day, self.date2])
            else:
                createSearch(session, self.date1, minn - day)
                createSearch(session, maxx + day, self.date2)
                intervals.append([self.date1, minn - day], [maxx + day, self.date2])            
            for interval in intervals:
                date1, date2 = interval[0], interval[1]
                createPremier(session, date1, (date2 - date1 + day).days)
            session.commit()
            self.populateCountries(session)
            self.populateLanguages(session)
            self.populateGenres(session)
            self.populateTable(session)
        self.query_one(Pretty).update("Created!")

    def exportData(self):
        with open("export.txt", "w") as file:
            writer = csv.writer(file)
            for rowKey in self.rowKeys:
                row = self.query_one(DataTable).get_row(rowKey)
                writer.writerow(row)

    def populateCountries(self, session):
        self.countries = set()
        for premier in session.exec(select(Premier).where(self.date1 <= Premier.premierDate).where(Premier.premierDate <= self.date2)):
            self.countries.add(premier.country)
        try:
            self.countries.remove(None)
        except KeyError:
            pass
        self.countries = sorted(self.countries)
        countriesList = self.query_one("#countries")
        for i, country in enumerate(self.countries):
            countriesList.add_option((country, i))

    def populateLanguages(self, session):
        self.languages = set()
        for premier in session.exec(select(Premier).where(self.date1 <= Premier.premierDate).where(Premier.premierDate <= self.date2)):
            self.languages.add(premier.language)
        try:
            self.languages.remove(None)
        except KeyError:
            pass
        self.languages = sorted(self.languages)
        languagesList = self.query_one("#languages")
        for i, language in enumerate(self.languages):
            languagesList.add_option((language, i))

    def populateGenres(self, session):
        self.genres = set()
        for premier, genre in session.exec(
            select(Premier, Genre).where(Genre.premier == Premier.id).where(self.date1 <= Premier.premierDate).where(Premier.premierDate <= self.date2)
            ):
            self.genres.add(genre.genre)
        try:
            self.genres.remove(None)
        except KeyError:
            pass
        self.genres = sorted(self.genres)
        genresList = self.query_one("#genres")
        for i, genre in enumerate(self.genres):
            genresList.add_option((genre, i))

    def populateTable(self, session):
        table = self.query_one(DataTable)
        for premier, rating in session.exec(
            select(Premier, Rating).where(Premier.id == Rating.premier).where(self.date1 <= Premier.premierDate).where(Premier.premierDate <= self.date2)
        ):
            self.rowKeys.append(table.add_row(*[premier.firstAired, premier.premierDate, premier.season, premier.title, premier.year, premier.country, premier.language, rating.rating]))
        self.query_one("#export").disabled = False

    # @on(DataTable.HeaderSelected)
    # def fu(self, event: DataTable.HeaderSelected) -> None:
    #     table = self.query_one(DataTable)
    #     table.sort(self.ckeys[event.column_index])

def isDate(date):
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def areOrdered(date1, date2):
    if  date1 >= date2:
        return False
    else:
        return True

if __name__ == "__main__":
    app = myApp()
    app.run()