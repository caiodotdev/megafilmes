import html

import unidecode

from app.models import Channel, ProgramItem
from app.views.movie import remove_accents


def make_xml():
    text = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n<tv generator-info-name="MasterTV">{}\n</tv>'
    return text.format(make_channels() + make_programs())


def make_channels():
    text = ''
    for channel in Channel.objects.all().order_by('title'):
        text += make_xml_by_channel(channel)
    return text


def make_programs():
    text = ''
    for pi in ProgramItem.objects.all():
        text += make_xml_by_program(pi)
    return text


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    # text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    text = html.escape(text)
    return text


def make_xml_by_channel(channel: Channel):
    pattern = '\n<channel id="{id}">' \
              '\n<display-name lang="en">{display_name}</display-name>' \
              '\n<icon src="{icon}"/>' \
              '\n</channel>'
    pattern = pattern.format(id=channel.id,
                             display_name=unicodeToHTMLEntities(unidecode.unidecode(remove_accents(channel.title))),
                             icon=channel.image)
    return pattern


def make_xml_by_program(program: ProgramItem):
    pattern = '\n<programme start="{start}" stop="{stop}" channel="{channel_id}">' \
              '\n<title lang="en">{title}</title>' \
              '\n<desc lang="en">{desc}</desc>' \
              '\n</programme>'
    if program.stop:
        stop = program.stop
    else:
        stop = program.start
    pattern = pattern.format(start=program.start, stop=stop, channel_id=program.program_day.channel.id,
                             title=unicodeToHTMLEntities(unidecode.unidecode(remove_accents(program.title))),
                             desc=unicodeToHTMLEntities(unidecode.unidecode(remove_accents(program.subtitle))))
    return pattern


def builder_file():
    f = open("epg.xml", "a")
    f.truncate(0)
    f.write(make_xml())
    f.close()
