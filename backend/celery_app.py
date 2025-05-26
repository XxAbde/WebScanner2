#!/usr/bin/env python3
"""
Celery application entry point
Usage: celery -A celery_app.celery worker --loglevel=info
"""
from app import create_app
from app.tasks.celery_config import make_celery

app = create_app()
celery = make_celery(app)

if __name__ == '__main__':
    celery.start()