release: python discoreg/manage.py migrate
web: gunicorn --pythonpath discoreg discoreg.wsgi --log-file -
nextupbot: python discoreg/manage.py nextupbot
rolebot: python discoreg/manage.py rolebot
