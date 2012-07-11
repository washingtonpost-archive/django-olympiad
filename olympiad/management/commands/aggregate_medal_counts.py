from django.core.management.base import BaseCommand
from olympiad.models import Event, Athlete, Country, OlympicGame, Sport


class Command(BaseCommand):
    """ The Comamnd() class is instantiated when the management command
    is executed with manage.py or django-admin.py.
    """

    def handle(self, *args, **kwargs):
        """ handle() is executed when the management command is run."""

        self.aggregate_athlete_totals()
        self.aggregate_country_totals()
        # self.aggregate_athlete_games()
        # self.aggregate_country_games()

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
            print athlete.medals

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
            print country.medals
