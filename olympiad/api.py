from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.api import Api
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from olympiad.models import Athlete, Country, OlympicGame, Sport, Event


class SportResource(ModelResource):
    class Meta:
        queryset = Sport.objects.all()
        resource_name = 'sport'
        allowed_methods = ['get', ]


class OlympicGameResource(ModelResource):
    class Meta:
        queryset = OlympicGame.objects.all()
        resource_name = 'game'
        allowed_methods = ['get', ]


class AthleteResource(ModelResource):
    class Meta:
        queryset = Athlete.objects.all()
        resource_name = 'athlete'
        allowed_methods = ['get', ]


class CountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all()
        resource_name = 'country'
        allowed_methods = ['get', ]


class EventResource(ModelResource):
    athlete = fields.ForeignKey('olympiad.api.AthleteResource',
        'athlete',
        null=True,
        full=True)
    country = fields.ForeignKey('olympiad.api.CountryResource',
        'country',
        null=True,
        full=True)
    sport = fields.ForeignKey('olympiad.api.SportResource',
        'sport',
        null=True,
        full=True)
    olympic_game = fields.ForeignKey('olympiad.api.OlympicGameResource',
        'olympic_game',
        null=True,
        full=True)

    class Meta:
        queryset = Event.objects.all()
        resource_name = 'event'
        allowed_methods = ['get', ]
        filtering = {
            'athlete': ALL_WITH_RELATIONS,
            'country': ALL_WITH_RELATIONS,
            'sport': ALL_WITH_RELATIONS,
            'olympic_game': ALL_WITH_RELATIONS,
            'medal': ALL,
            'record': ALL,
        }

v1 = Api(api_name='v1')
v1.register(EventResource())
v1.register(CountryResource())
v1.register(SportResource())
v1.register(AthleteResource())
v1.register(OlympicGameResource())
