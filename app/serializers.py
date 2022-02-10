from rest_framework import serializers

from app.models import Movie, Serie, Channel, Episodio, Source


class MovieSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Movie
        fields = ("id", "title", "year", "rating", "image", "url", "selected", "link_m3u8")


class SerieSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Serie
        fields = ("id", "title", "year", "rating", "image", "url")


class ChannelSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Channel
        fields = ("id", "title", "image", "code", "url", "link_m3u8", "custom_m3u8", "category")


class EpisodioSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Episodio
        fields = ("id", "title", "image", "url", "selected", "serie", "link_m3u8")


class SourceSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Source
        fields = ("id", "title", "image", "source")
