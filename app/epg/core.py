import datetime

from app.models import Channel, ProgramDay, ProgramItem
from app.utils import get_page


def get_hour(text):
    return text[0] + text[1] + ':' + text[3] + text[4]


def exists_program_day(text_program_day, channel):
    qs = ProgramDay.objects.filter(channel=channel, title=text_program_day)
    if qs.exists():
        return qs.last()
    return None


def collect_all():
    remove_older_program_day()
    for channel in Channel.objects.all().order_by('title'):
        collect_program_by_channel(channel)


def remove_older_program_day():
    qs = ProgramDay.objects.filter(date_formatted__lte=datetime.datetime.now().date())
    if qs.exists():
        print('--removendo Programação antiga')
        qs.delete()
    else:
        print('--Nao existe programação antiga')


def collect_program_by_channel(channel: Channel):
    if channel.program_url:
        print('-- Coletando programacao: ' + str(channel.title))
        page = get_page(channel.program_url, {})
        content = page.find('ul', {'class': 'mw'})
        lis = content.findAll('li')
        next_program_day = None
        previous_program_item = None

        for li in lis:
            if li.has_attr('class'):
                if 'subheader' in li['class']:
                    text_program_day = li.text
                    program_day = exists_program_day(text_program_day, channel)
                    if not program_day:
                        program_day = ProgramDay()
                        program_day.title = text_program_day
                        program_day.channel = channel
                        program_day.save()
                    next_program_day = program_day
            else:
                title = li.find('h2').text
                subtitle = li.find('h3').text
                hour = get_hour(li.find('div', {'class': 'time'}).text)
                if exists_program_item(title, subtitle, hour, next_program_day):
                    program_item = update_program_item(title, subtitle, hour, next_program_day, None)
                else:
                    program_item = ProgramItem()
                    program_item.title = title
                    program_item.subtitle = subtitle
                    program_item.hour = hour
                    program_item.program_day = next_program_day
                    program_item.save()
                if previous_program_item:
                    previous_program_item.stop = program_item.start
                    previous_program_item.save()
                previous_program_item = program_item


def exists_program_item(title, subtitle, hour, program_day):
    qs = ProgramItem.objects.filter(title=title, subtitle=subtitle, hour=hour, program_day=program_day)
    if qs.exists():
        return qs.last()
    return None


def update_program_item(title, subtitle, hour, program_day: ProgramDay, stop):
    program_item = exists_program_item(title, subtitle, hour, program_day)
    if program_item:
        program_item.title = title
        program_item.subtitle = subtitle
        program_item.program_day = program_day
        program_item.stop = stop
        program_item.save()
        return program_item
    return None
