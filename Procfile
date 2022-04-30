web: gunicorn megafilmes.wsgi --log-file -

beat: celery -A app beat -l INFO
worker: celery -A app worker -l INFO -c 1
