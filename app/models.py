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
        return self.title

    def __unicode__(self):
        return self.title


class Program(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class LinkChannel(TimeStamp):
    url = models.TextField(blank=True, null=True)
    m3u8 = models.TextField(blank=True, null=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.url

    def __unicode__(self):
        return "%s" % self.url


class Channel(TimeStamp):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    link_m3u8 = models.TextField(blank=True, null=True)
    program = models.ForeignKey(Program, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title
