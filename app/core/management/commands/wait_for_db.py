"""
Django command for waiting for database to be available.
"""
from django.core.management.base import BaseCommand

# BaseCommand has a check method that we can use to test if the database is available. 
class Command(BaseCommand):
    """Django command for waiting for database """

    def handle(self,*args,**options):
        pass
