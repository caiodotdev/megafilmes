import time

from django_cron import CronJobBase, Schedule

from app.views.channel import get_m3u8_channels
from app.views.movie import get_m3u8_movies


def my_cron_job():
    print('---- Run CRON JOB my_cron_job')
    req = get_m3u8_channels({})
    print(req)
    return req


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.MyCronJob'  # a unique code

    def do(self):
        print('---- Run CRON JOB CLASS')
        i = 0
        while True:
            print('---- Starting: ' + str(i))
            print(time.asctime())
            get_m3u8_channels({})
            get_m3u8_movies({})
            print(time.asctime())
            print('---- Finish CRON JOB: ' + str(i))
            time.sleep(60 * 60 * 2)
            i = i + 1
