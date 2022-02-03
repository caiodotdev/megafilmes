from django.db import models


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
