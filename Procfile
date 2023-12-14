release: python discoreg/manage.py migrate
web: gunicorn --pythonpath discoreg discoreg.wsgi --log-file -
worker: python discoreg/manage.py nextupbot
worker: python discoreg/manage.py rolebot
