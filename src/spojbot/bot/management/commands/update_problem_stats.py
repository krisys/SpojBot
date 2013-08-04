from django.core.management.base import BaseCommand
from bot.models import SpojProblem


class Command(BaseCommand):
    args = 'No args'
    help = 'Updates problem stats'

    def handle(self, *args, **options):
        problems = SpojProblem.objects.all()
        for problem in problems:
            try:
                problem.fetch_stats()
            except:
                pass
