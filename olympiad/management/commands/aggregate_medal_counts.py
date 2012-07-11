from django.core.management.base import BaseCommand
from olympiad.models import (Event, Athlete, Country, OlympicGame,
    Sport, AthleteOlympicGame, CountryOlympicGame)


class Command(BaseCommand):
    """ The Comamnd() class is instantiated when the management command
    is executed with manage.py or django-admin.py.
    """

    def handle(self, *args, **kwargs):
        """ handle() is executed when the management command is run."""

        self.aggregate_athlete_totals()
        self.aggregate_country_totals()
        self.aggregate_country_games()
        self.aggregate_athlete_games()

    def aggregate_athlete_games(self):
        """ Function to create AthleteGames. An AthleteGame is one athlete's
        performance in a single OlympicGame, e.g., Michael Phelps in Beijing
        2008 and his medal count.
        """

        # Nuke all of the previous games so that there are no duplicates.
        AthleteOlympicGame.objects.all().delete()

        # Loop through every game.
        for game in OlympicGame.objects.all():

            # For each game, loop through all of the athletes.
            # Everyone is fair game for any particular Olympics because
            # athletes aren't tied to an OlympicGame by default.
            for athlete in Athlete.objects.all():

                # Create the stub of an AthleteOlympicGame.
                ag = AthleteOlympicGame()
                ag.athlete = athlete
                ag.olympic_game = game
                ag.country = None

                # Loop through all of the events associated with this athlete
                # in this particular game. Increment the medal counts appropriately.
                for event in Event.objects.filter(athlete=athlete, olympic_game=game):
                    if event.medal.lower() == 'gold':
                        ag.total_gold += 1
                    if event.medal.lower() == 'silver':
                        ag.total_silver += 1
                    if event.medal.lower() == 'bronze':
                        ag.total_bronze += 1

                    # Tie the country loosely. This is for people who appeared
                    # for different countries in different years, e.g., USSR in
                    # 1984 and then Russia in 1988 or some such.
                    if not ag.country:
                        ag.country = event.country

                # If this athlete didn't earn any medals, don't save.
                if ag.total_gold == ag.total_silver == ag.total_bronze == 0:
                    pass
                else:
                    # Otherwise, save.
                    ag.save()
                    print ag, ag.medals

    def aggregate_country_games(self):
        """ Function to create CountryGames. A CountryGame is one country's
        performance in a single OlympicGame, e.g., Germany in Beijing 2008 and
        their medal count.
        """

        # Nuke all of the previous games so that there are no duplicates.
        CountryOlympicGame.objects.all().delete()

        # Loop through every game.
        for game in OlympicGame.objects.all():

            # For each game, loop through all of the countries.
            # Any country is fair game for any particular Olympics because
            # a country isn't tied to an Olympics by default.
            for country in Country.objects.all():

                # Create the stub of a CountryGame.
                cg = CountryOlympicGame()
                cg.country = country
                cg.olympic_game = game

                # Loop through all of the events associated with this country
                # in this particular game. Increment the medal counts appropriately.
                for event in Event.objects.filter(country=country, olympic_game=game):
                    if event.medal.lower() == 'gold':
                        cg.total_gold += 1
                    if event.medal.lower() == 'silver':
                        cg.total_silver += 1
                    if event.medal.lower() == 'bronze':
                        cg.total_bronze += 1

                # If the country didn't earn a medal, don't save.
                if cg.total_gold == cg.total_silver == cg.total_bronze == 0:
                    pass
                else:
                    # Otherwise, save.
                    cg.save()
                    print cg, cg.medals

    def aggregate_athlete_totals(self):
        """ Function to add up total medals for each Athlete across
        all games.
        """

        # Loop through each of the athletes.
        for athlete in Athlete.objects.all():

            # Loop through all of the events associated with this athlete.
            # Note: Across all games.
            for event in Event.objects.filter(athlete=athlete):

                # Increment medal counts.
                if event.medal.lower() == 'gold':
                    athlete.total_gold += 1
                if event.medal.lower() == 'silver':
                    athlete.total_silver += 1
                if event.medal.lower() == 'bronze':
                    athlete.total_bronze += 1

            # Save the athlete.
            athlete.save()
            print athlete, athlete.medals

    def aggregate_country_totals(self):

        # Loop through each of the countries.
        for country in Country.objects.all():

            # Loop through the events associated with this country.
            # Note: Across all games.
            for event in Event.objects.filter(country=country):

                # Increment medal counts.
                if event.medal.lower() == 'gold':
                    country.total_gold += 1
                if event.medal.lower() == 'silver':
                    country.total_silver += 1
                if event.medal.lower() == 'bronze':
                    country.total_bronze += 1

            # Save the country.
            country.save()
            print country, country.medals
