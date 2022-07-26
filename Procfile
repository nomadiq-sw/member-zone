web: gunicorn config.wsgi --log-file - --log-level info
worker: celery -A config.celery_app worker -l info -P eventlet
beat: celery -A config.celery_app beat -l info
