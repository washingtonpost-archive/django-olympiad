from django.core.management.base import BaseCommand
from olympiad.models import (Event, Athlete, Country, OlympicGame,
    Sport, AthleteOlympicGame, CountryOlympicGame)


class Command(BaseCommand):
    """ The Comamnd() class is instantiated when the management command
    is executed with manage.py or django-admin.py.
    """

    integrity_errors = []

    def handle(self, *args, **kwargs):
        """ handle() is executed when the management command is run."""

        # self.aggregate_athlete_totals()
        # self.aggregate_country_totals()
        self.aggregate_athlete_games()
        # self.aggregate_country_games()
        print self.integrity_errors

    def aggregate_athlete_games(self):

        AthleteOlympicGame.objects.all().delete()

        for game in OlympicGame.objects.all():
            for athlete in Athlete.objects.all():
                ag = AthleteOlympicGame()
                ag.athlete = athlete
                ag.olympic_game = game
                ag.country = None

                for event in Event.objects.filter(athlete=athlete, olympic_game=game):
                    if event.medal.lower() == 'gold':
                        ag.total_gold += 1
                    if event.medal.lower() == 'silver':
                        ag.total_silver += 1
                    if event.medal.lower() == 'bronze':
                        ag.total_bronze += 1

                    if not ag.country:
                        ag.country = event.country

                if ag.country:
                    ag.save()
                    print ag, ag.medals
                else:
                    self.integrity_errors.append(ag.__dict__)

    def aggregate_country_games(self):

        CountryOlympicGame.objects.all().delete()

        for game in OlympicGame.objects.all():
            for country in Country.objects.all():
                cg = CountryOlympicGame()
                cg.country = country
                cg.olympic_game = game

                for event in Event.objects.filter(country=country, olympic_game=game):
                    if event.medal.lower() == 'gold':
                        cg.total_gold += 1
                    if event.medal.lower() == 'silver':
                        cg.total_silver += 1
                    if event.medal.lower() == 'bronze':
                        cg.total_bronze += 1

                cg.save()
                print cg, cg.medals

    def aggregate_athlete_totals(self):
        for athlete in Athlete.objects.all():
            for event in Event.objects.filter(athlete=athlete):
                if event.medal.lower() == 'gold':
                    athlete.total_gold += 1
                if event.medal.lower() == 'silver':
                    athlete.total_silver += 1
                if event.medal.lower() == 'bronze':
                    athlete.total_bronze += 1
            athlete.save()
            print athlete, athlete.medals

    def aggregate_country_totals(self):
        for country in Country.objects.all():
            for event in Event.objects.filter(country=country):
                if event.medal.lower() == 'gold':
                    country.total_gold += 1
                if event.medal.lower() == 'silver':
                    country.total_silver += 1
                if event.medal.lower() == 'bronze':
                    country.total_bronze += 1

            country.save()
            print country, country.medals
