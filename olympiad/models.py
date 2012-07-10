from django.db import models


CLASSIFICATION_CHOICES = (
    ('team', 'Team sport'),
    ('individual', 'Individual sport')
)

SEASON_CHOICES = (
    ('summer', 'Summer Olympic Games'),
    ('winter', 'Winter Olympic Games')
)

RECORD_CHOICES = (
    ('world_record', 'World Record'),
    ('olympic_record', 'Olympic Record'),
)

MEDAL_CHOICES = (
    ('gold', 'Gold medal'),
    ('silver', 'Silver medal'),
    ('bronze', 'Bronze medal')
)


class Sport(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    classification = models.CharField(
        max_length=255,
        choices=CLASSIFICATION_CHOICES)
    olympic_detail_url = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class OlympicGame(models.Model):
    year = models.IntegerField()
    location = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    season = models.CharField(
        max_length=255,
        choices=SEASON_CHOICES)
    olympic_detail_url = models.TextField(blank=True, null=True)
    olympic_id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.year, self.location)


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    olympic_detail_url = models.TextField(blank=True, null=True)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class Athlete(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name


class AthleteOlympicGame(models.Model):
    athlete = models.ForeignKey(Athlete)
    country = models.ForeignKey(Country)
    olympic_game = models.ForeignKey(OlympicGame)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s %s' % (self.athlete, self.country, self.olympic_game)


class CountryOlympicGame(models.Model):
    country = models.ForeignKey(Country)
    olympic_game = models.ForeignKey(OlympicGame)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s' % (self.country, self.olympic_game)


class Event(models.Model):
    date = models.DateField()
    olympic_game = models.ForeignKey(OlympicGame)
    sport = models.ForeignKey(Sport)
    record = models.CharField(
        max_length=255,
        choices=RECORD_CHOICES)
    medal = models.CharField(
        max_length=255,
        choices=MEDAL_CHOICES)
    athlete = models.ForeignKey(Athlete, blank=True, null=True)
    country = models.ForeignKey(Country)

    def __unicode__(self):
        return u'%s: %s %s' % (
            self.medal,
            self.olympic_game,
            self.country
        )
