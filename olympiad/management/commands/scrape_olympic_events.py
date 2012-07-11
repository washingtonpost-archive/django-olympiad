import requests
import datetime
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from olympiad.models import Event, Athlete, Country, OlympicGame, Sport

class Command(BaseCommand):
    """ The Comamnd() class is instantiated when the management command
    is executed with manage.py or django-admin.py.
    """

    # This is the list of all 47 IOC IDs for the Olympic games.
    # You don't want to scrape these yourself, though you can.
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

    # CSS ID of the DOM object where we can harvest the ID. Same on every page.
    olympic_css = '#ctl00_mainContent_TopAthletesBlock1_AllAthletesLink_LinkText'

    # CSS ID of the DOM object that contains the result count. Same on every page.
    result_css = '#ctl00_mainContent_ResultsDataSearchResultsBlock_lblResultsCount'

    # The terribly long base URL we'll be modifying.
    base_detail_url = "http://www.olympic.org/medallists-results?athletename=&category=1&sport=&event=&mengender=false&womengender=false&mixedgender=false&continent=&country=&goldmedal=false&silvermedal=false&bronzemedal=false&targetresults=true&worldrecord=false&olympicrecord=false&resultspageipp=250"

    def handle(self, *args, **kwargs):
        """ handle() is executed when the management command is run."""

        # You don't have to make 47 requests to the IOC anymore; we
        # got that covered in the list above.
        # However, if you're a purist, just uncomment this line and
        # go to town. Have fun!

        # self.build_olympic_id_list()

        # This function scrapes the olympic events.
        self.scrape_olympic_events()

    def scrape_olympic_events(self):
        """ This function scrapes Olympic events. Here's the logic:
        1. Loop through the list of IDs above.
        2. Loop through the team sports, then individual sports.
        3. Make an URL request for the current classification (e.g,
            team or individual.)
        4. Parse the request with BeautifulSoup.
        5. Get the result count.
        6. Paginate the result count at 250 objects per page.
        7. Loop through the page numbers.
        8. For each page number, make a request.
        9. Parse the request with BeautifulSoup.
        10. Loop through the odd and even rows of the results.
        11. In each row, loop through the cells.
        12. Look for Athlete(), Sport() and Country() info in the cells.
            When possible, get the object; otherwise, save a new one.
        13. Lookup or create the OlympicGame.
        14. Lookup or create the event; if created, attach Athlete(), Sport(),
            OlympicGame() and Country().
        """

        # Loop through the IDs.
        for game_id in self.olympic_ids:

            # Valid searches need two checkboxes checked; I chose:
            # 1.) This particular Olympic game and
            # 2.) Team/Individual sports.
            # These are called "classifications" by the IOC.
            # We'll loop through the two classifications here to build
            # valid URLs.
            for classification in ["team", "individual"]:

                # Set the result count to 0. We'll update this soon.
                result_count = 0

                # Set the page number to 1. We'll update this soon.
                # The site paginates at a max of 250 events.
                pages = 1

                # Set the proper URL parameters.
                if classification == "individual":
                    classy_url = "&teamclassification=false&individualclassification=true"
                else:
                    classy_url = "&teamclassification=true&individualclassification=false"

                # Make the request.
                request = requests.get(
                    self.base_detail_url\
                    + classy_url\
                    + '&games=%s' % game_id)

                # Parse the request.
                soup = BeautifulSoup(request.content)

                # Get the result count.
                # We need this to figure out how many pages to request.
                result_count = int(soup.select(self.result_css)[0].get_text())

                # Divide the results by 250. That's the max number of events
                # that the IOC Web site will return.
                pages = result_count / 250

                # Do modulo division to see if there's a remainder.
                # If there is a remainder, add 1 to the page list.
                if result_count % 250 > 0:
                    pages += 1

                # Create a range for the page list.
                # Loop through it.
                for page in range(1, pages + 1):

                    # Make a request for each page in the range.
                    request = requests.get(
                        self.base_detail_url\
                        + classy_url\
                        + '&games=%s' % game_id\
                        + '&resultspage=%s' % page)

                    # Parse the request
                    soup = BeautifulSoup(request.content)

                    # Different classes for even and odd rows.
                    # Cute.
                    odd_rows = soup.select('tr.iocResultsDataSearchResultsTableLine')
                    even_rows = soup.select('tr.iocResultsDataSearchResultsTableAlternateLine')

                    # Loop through the even/odd classes.
                    for set_of_rows in [odd_rows, even_rows]:

                        # Loop through this set of rows.
                        for row in set_of_rows:

                            # Let's set an intermediate data store for this event.
                            event_dict = {}

                            # Select all of the cells in this row.
                            cells = row.select('td')

                            # Grab the medal information.
                            event_dict['medal'] = str(cells[4].select('img')[0].attrs['alt']).lower()

                            # Grab the date information and make a datetime.date()
                            # object for it.
                            year = int(cells[0].get_text().split('/')[2])
                            month = int(cells[0].get_text().split('/')[0])
                            day = int(cells[0].get_text().split('/')[1])
                            event_dict['date'] = datetime.date(year, month, day)

                            # See if this event is a world/olympic record.
                            try:
                                event_dict['record'] = str(cells[3].select('img')[0].attrs['alt']).lower()
                            except:
                                pass

                            # Go ahead and get/create this Olympic game.
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

                            # Find and get/create the sport.
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

                            # Find and get/create the athlete.
                            # Note: We skip this step for team sports.
                            # They have totally non-reasonable athlete
                            # names for the teams.
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

                            # Find and get/create the country.
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

                            # Now that we have all the pieces, try to get/create
                            # this particular event. They should ALL fail and
                            # create a new one, unless you're re-running this
                            # script.
                            # Note: We do not update events here. Just get/create.
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
        """ This function will make a call to the IOC Web site to get a
        list of URLs for each of the 47 Olympic games. Then, for each one,
        it will follow the URL and scrape the IOC ID for that game.

        Note: This function is for bootstrapping only. The IDs you're looking
        for are in self.olympic_ids.
        """

        # Get the URL where all the games are and parse it.
        all_games_url = u'http://www.olympic.org/olympic-games'
        request = requests.get(all_games_url)
        soup = BeautifulSoup(request.content)

        # Find the list of links.
        link_list = soup.select('.iocRiaContent')[0].select('li span a')

        # Loop through that list.
        for link in link_list:

            # For each Olympic game, get the URL of the detail page.
            olympic_url = link.attrs['href']

            # Request it and parse it.
            request = requests.get(olympic_url)
            soup = BeautifulSoup(request.content)

            # Grab the olympic_css DOM object.
            # Parse out the ID from the href.
            olympic_id = soup.select(self.olympic_css)[0].attrs['href']
            olympic_id = olympic_id.split('games=')[1].split('&')[0]

            # Try to append this to the olympic_ids list.
            # Fail if it's not an integer for some reason.
            try:
                olympic_id = int(olympic_id)
                self.olympic_ids.append(olympic_id)
            except ValueError:
                print u'%s is not an integer.' % olympic_id
