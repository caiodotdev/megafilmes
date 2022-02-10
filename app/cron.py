import time

from django_cron import CronJobBase, Schedule

from app.views.channel import get_m3u8_channels
from app.views.megapack import MegaPack
from app.views.movie import get_m3u8_movies, updator_movies_server
from app.views.serie import get_m3u8_episodes, updator_series_server


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
            mega = MegaPack()
            print('---- Starting: ' + str(i))
            print(time.asctime())
            get_m3u8_channels({}, mega)
            get_m3u8_movies({}, mega)
            get_m3u8_episodes({}, mega)
            updator_movies_server()
            updator_series_server()
            print(time.asctime())
            print('---- Finish CRON JOB: ' + str(i))
            time.sleep(60 * 60 * 2)
            i = i + 1
            mega.close()
