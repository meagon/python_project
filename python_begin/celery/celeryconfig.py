

CELERY_IMPORTS = ('tasks',)
BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'amqp://'
