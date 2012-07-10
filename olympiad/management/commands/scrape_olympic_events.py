import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from olympiad.models import Event, Athlete, Country, OlympicGame, Sport

class Command(BaseCommand):

    olympic_ids = []

    def handle(self, *args, **kwargs):

        self.build_olympic_id_list()

    def build_olympic_id_list(self):
        all_games_url = u'http://www.olympic.org/olympic-games'
        request = requests.get(all_games_url)
        soup = BeautifulSoup(request.content)

        link_list = soup.select('iocRiaContent').select('li').select('a')
        print link_list
