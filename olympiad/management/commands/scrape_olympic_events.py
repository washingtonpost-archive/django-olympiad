import requests
import datetime
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from olympiad.models import Event, Athlete, Country, OlympicGame, Sport

class Command(BaseCommand):

    olympic_ids = [
        31374, 31377, 31373,
        146888, 31360, 31371,
        31359, 31370, 31358,
        31367, 31355, 31363,
        31352, 31361, 31351,
        146892, 31350, 31387,
        31349, 31385, 31348,
        31382, 31347, 31381,
        43831, 31379, 31346,
        31376, 31357, 31375,
        31356, 31372, 31354,
        31368, 31353, 31364,
        31345, 134245, 31344,
        31138, 31339, 30769,
        151944, 30767, 30772,
        126789, 154975
    ]

    olympic_css = '#ctl00_mainContent_TopAthletesBlock1_AllAthletesLink_LinkText'
    result_css = '#ctl00_mainContent_ResultsDataSearchResultsBlock_lblResultsCount'
    base_detail_url = "http://www.olympic.org/medallists-results?athletename=&category=1&sport=&event=&mengender=false&womengender=false&mixedgender=false&continent=&country=&goldmedal=false&silvermedal=false&bronzemedal=false&targetresults=true&worldrecord=false&olympicrecord=false&resultspageipp=250"

    def handle(self, *args, **kwargs):

        # You don't have to make 47 requests to the IOC anymore; we
        # got that covered in the list above.
        # However, if you're a purist, just uncomment this line and
        # go to town. Have fun!

        # self.build_olympic_id_list()
        self.scrape_olympic_events()

    def scrape_olympic_events(self):
        for game_id in self.olympic_ids:
            for classification in ["team", "individual"]:

                result_count = 0
                pages = 1

                if classification == "individual":
                    classy_url = "&teamclassification=false&individualclassification=true"
                else:
                    classy_url = "&teamclassification=true&individualclassification=false"

                request = requests.get(
                    self.base_detail_url\
                    + classy_url\
                    + '&games=%s' % game_id)

                soup = BeautifulSoup(request.content)
                result_count = int(soup.select(self.result_css)[0].get_text())

                pages = result_count / 250
                if result_count % 250 > 0:
                    pages += 1

                for page in range(1, pages + 1):
                    request = requests.get(
                        self.base_detail_url\
                        + classy_url\
                        + '&games=%s' % game_id\
                        + '&resultspage=%s' % page)

                    soup = BeautifulSoup(request.content)

                    print self.base_detail_url\
                        + classy_url\
                        + '&games=%s' % game_id\
                        + '&resultspage=%s' % page

                    odd_rows = soup.select('tr.iocResultsDataSearchResultsTableLine')
                    even_rows = soup.select('tr.iocResultsDataSearchResultsTableAlternateLine')

                    for set_of_rows in [odd_rows, even_rows]:
                        for row in set_of_rows:
                            event_dict = {}
                            cells = row.select('td')

                            # Medal
                            event_dict['medal'] = str(cells[4].select('img')[0].attrs['alt']).lower()

                            # Date
                            year = int(cells[0].get_text().split('/')[2])
                            month = int(cells[0].get_text().split('/')[0])
                            day = int(cells[0].get_text().split('/')[1])
                            event_dict['date'] = datetime.date(year, month, day)

                            # Record
                            try:
                                event_dict['record'] = str(cells[3].select('img')[0].attrs['alt']).lower()
                            except:
                                pass

                            # Olympic Game
                            try:
                                olympic_game = OlympicGame.objects.get(id=game_id)
                                print u'* Game: %s' % olympic_game
                            except OlympicGame.DoesNotExist:
                                olympic_game_dict = {}
                                olympic_game_dict['id'] = game_id
                                olympic_game_dict['year'] = year
                                olympic_game_dict['olympic_detail_url'] = cells[1].select('a')[0].attrs['href']
                                olympic_game_dict['location'] = cells[1].select('a')[0].get_text()
                                if month in [3, 4, 5, 6, 7, 8, 9]:
                                    olympic_game_dict['season'] = 'summer'
                                else:
                                    olympic_game_dict['season'] = 'winter'
                                olympic_game = OlympicGame(**olympic_game_dict)
                                olympic_game.save()
                                print u'+ Game: %s' % olympic_game

                            # Sport
                            sport_name = cells[2].get_text()
                            try:
                                sport = Sport.objects.get(name=sport_name, classification=classification)
                                print u'* Sport: %s' % sport
                            except Sport.DoesNotExist:
                                sport_dict = {}
                                sport_dict['name'] = sport_name
                                sport_dict['classification'] = classification
                                try:
                                    sport_dict['sport_detail_url'] = cells[2].select('a')[0].attrs['href']
                                except:
                                    pass
                                sport = Sport(**sport_dict)
                                sport.save()
                                print u'+ Sport: %s' % sport

                            # Athlete
                            athlete = None
                            if classification == 'individual':
                                athlete_name = cells[5].get_text()
                                try:
                                    athlete = Athlete.objects.get(name=athlete_name)
                                    print u'* Athlete: %s' % athlete
                                except Athlete.DoesNotExist:
                                    athlete_dict = {}
                                    athlete_dict['name'] = athlete_name
                                    try:
                                        athlete_dict['athlete_detail_url'] = cells[5].select('a')[0].attrs['href']
                                    except:
                                        pass
                                    athlete = Athlete(**athlete_dict)
                                    athlete.save()
                                    print u'+ Athlete: %s' % athlete

                            # Country
                            country_name = cells[6].get_text()
                            try:
                                country = Country.objects.get(name=country_name)
                                print u'* Country: %s' % country
                            except Country.DoesNotExist:
                                country_dict = {}
                                country_dict['name'] = country_name
                                try:
                                    country_dict['country_detail_url'] = cells[6].select('a')[0].attrs['href']
                                except:
                                    pass
                                country = Country(**country_dict)
                                country.save()
                                print u'+ Country: %s' % country

                            # Save event.
                            try:
                                event = Event.objects.get(
                                    olympic_game=olympic_game,
                                    athlete=athlete,
                                    medal=event_dict['medal'],
                                    sport=sport,
                                    country=country)
                                print u'* Event: %s' % event
                            except Event.DoesNotExist:
                                event = Event(**event_dict)
                                event.olympic_game = olympic_game
                                event.sport = sport
                                event.country = country
                                if classification == 'individual':
                                    event.athlete = athlete
                                event.save()
                                print u'+ Event: %s' % event

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
