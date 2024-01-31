"""
Django command to check if the database is up and running.
"""
from typing import Any, Optional
from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Check if the database is up and running.'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        self.stdout.write(self.style.NOTICE('Waiting for database...'))
        db_up = False
        while db_up is False:
            time.sleep(1)
            try:
                self.check(databases=['default'])
                db_up=True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
        self.stdout.write(self.style.SUCCESS('Database available!'))
