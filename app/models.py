from django.db import models

import datetime


# Create your models here.


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Movie(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    rating = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    link_m3u8 = models.TextField(blank=True, null=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Serie(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    rating = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.title

    def __unicode__(self):
        return "%s" % self.title


class Episodio(TimeStamp):
    serie = models.ForeignKey(Serie, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    number = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    date = models.CharField(max_length=100, blank=True, null=True)
    is_assistido = models.BooleanField(default=False)
    link_m3u8 = models.TextField(blank=True, null=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.title

    def __unicode__(self):
        return "%s" % self.title


class LinkChannel(TimeStamp):
    url = models.TextField(blank=True, null=True)
    m3u8 = models.TextField(blank=True, null=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.url

    def __unicode__(self):
        return "%s" % self.url


class Category(TimeStamp):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return self.name


class Channel(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    link_m3u8 = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    custom_m3u8 = models.TextField(blank=True, null=True)
    program_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Playlist(TimeStamp):
    serie = models.ForeignKey(Serie, blank=True, null=True, on_delete=models.CASCADE)
    titulos = models.TextField()

    def __str__(self):
        return self.serie.title

    def __unicode__(self):
        return self.serie.title


class UrlPlaylist(TimeStamp):
    playlist = models.ForeignKey(Playlist, blank=True, null=True, on_delete=models.CASCADE)
    url = models.TextField()

    def __str__(self):
        return self.url

    def __unicode__(self):
        return self.url


class ProgramDay(TimeStamp):
    channel = models.ForeignKey(Channel, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    date_formatted = models.DateField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.title

    def format_date(self):
        if self.title and type(self.title) == str:
            array_strings = [st.strip() for st in self.title.split(',')]
            date_string = array_strings[1] + "/" + str(datetime.datetime.now().year)
            return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
        return None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.date_formatted = self.format_date()
        return super(ProgramDay, self).save(force_insert, force_update, using, update_fields)


class ProgramItem(TimeStamp):
    program_day = models.ForeignKey(ProgramDay, blank=True, null=True, on_delete=models.CASCADE)
    hour = models.CharField(max_length=255, blank=True, null=True)
    hour_formatted = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)  # category
    description = models.TextField(blank=True, null=True, default="")
    start = models.CharField(max_length=255, blank=True, null=True)
    stop = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s" % self.title

    def get_hour_formatted(self):
        if self.hour and type(self.hour) == str:
            program_date = self.program_day.date_formatted.strftime("%d-%m-%Y")
            return datetime.datetime.strptime(str(program_date + " " + self.hour), "%d-%m-%Y %H:%M")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.hour_formatted = self.get_hour_formatted()
        self.start = self.hour_formatted.strftime("%Y%m%d%H%M%S %Z") + "-0300"
        return super(ProgramItem, self).save(force_insert, force_update, using, update_fields)
