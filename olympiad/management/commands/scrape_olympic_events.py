import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from olympiad.models import Event, Athlete, Country, OlympicGame, Sport

class Command(BaseCommand):

    olympic_ids = []
    olympic_css = '#ctl00_mainContent_TopAthletesBlock1_AllAthletesLink_LinkText'

    def handle(self, *args, **kwargs):

        self.build_olympic_id_list()
        print self.olympic_ids
        print len(self.olympic_ids)

    def build_olympic_id_list(self):
        all_games_url = u'http://www.olympic.org/olympic-games'
        request = requests.get(all_games_url)
        soup = BeautifulSoup(request.content)

        link_list = soup.select('.iocRiaContent')[0].select('li span a')

        for link in link_list:
            olympic_url = link.attrs['href']

            request = requests.get(olympic_url)
            soup = BeautifulSoup(request.content)

            olympic_id = soup.select(self.olympic_css)[0].attrs['href']
            olympic_id = olympic_id.split('games=')[1].split('&')[0]

            try:
                olympic_id = int(olympic_id)
                self.olympic_ids.append(olympic_id)
            except ValueError:
                print u'%s is not an integer.' % olympic_id
