release: python manage.py migrate; python manage.py collectstatic --noinput
web: gunicorn factum_humanum.wsgi --bind 0.0.0.0:$PORT
