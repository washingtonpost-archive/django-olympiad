from django.db import models
from django.template.defaultfilters import slugify

CLASSIFICATION_CHOICES = (
    ('team', 'Team sport'),
    ('individual', 'Individual sport')
)

SEASON_CHOICES = (
    ('summer', 'Summer Olympic Games'),
    ('winter', 'Winter Olympic Games')
)

RECORD_CHOICES = (
    ('world', 'World Record'),
    ('olympic', 'Olympic Record'),
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
    sport_detail_url = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.__unicode__())
        return super(Sport, self).save(*args, **kwargs)


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
        return self.location

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.__unicode__())
        return super(OlympicGame, self).save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    country_detail_url = models.TextField(blank=True, null=True)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.__unicode__())
        return super(Country, self).save(*args, **kwargs)

    @property
    def medals(self):
        return {
            'total': self.total_gold + self.total_silver + self.total_bronze,
            'gold': self.total_gold,
            'silver': self.total_silver,
            'bronze': self.total_bronze
        }


class Athlete(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    athlete_detail_url = models.TextField(blank=True, null=True)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.__unicode__())
        return super(Athlete, self).save(*args, **kwargs)

    @property
    def medals(self):
        return {
            'total': self.total_gold + self.total_silver + self.total_bronze,
            'gold': self.total_gold,
            'silver': self.total_silver,
            'bronze': self.total_bronze
        }


class AthleteOlympicGame(models.Model):
    athlete = models.ForeignKey(Athlete)
    country = models.ForeignKey(Country, null=True)
    olympic_game = models.ForeignKey(OlympicGame)
    total_gold = models.IntegerField(default=0)
    total_silver = models.IntegerField(default=0)
    total_bronze = models.IntegerField(default=0)
    total_world_records = models.IntegerField(default=0)
    total_olympic_records = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s %s' % (self.athlete, self.country, self.olympic_game)

    @property
    def medals(self):
        return {
            'total': self.total_gold + self.total_silver + self.total_bronze,
            'gold': self.total_gold,
            'silver': self.total_silver,
            'bronze': self.total_bronze
        }


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

    @property
    def medals(self):
        return {
            'total': self.total_gold + self.total_silver + self.total_bronze,
            'gold': self.total_gold,
            'silver': self.total_silver,
            'bronze': self.total_bronze
        }


class Event(models.Model):
    date = models.DateField()
    olympic_game = models.ForeignKey(OlympicGame)
    sport = models.ForeignKey(Sport)
    athlete = models.ForeignKey(Athlete, blank=True, null=True)
    country = models.ForeignKey(Country)
    record = models.CharField(
        max_length=255,
        choices=RECORD_CHOICES)
    medal = models.CharField(
        max_length=255,
        choices=MEDAL_CHOICES)

    def __unicode__(self):
        return u'%s: %s %s %s' % (
            self.medal,
            self.sport,
            self.date,
            self.country
        )
