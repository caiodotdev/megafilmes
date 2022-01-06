from django_cron import CronJobBase, Schedule

from app.views.channel import get_m3u8_channels


def my_cron_job():
    print('---- Run CRON JOB my_cron_job')
    req = get_m3u8_channels({})
    print(req)
    return req


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.cron.my_cron_job'  # a unique code

    def do(self):
        print('---- Run CRON JOB CLASS Do()')
        get_m3u8_channels({})
