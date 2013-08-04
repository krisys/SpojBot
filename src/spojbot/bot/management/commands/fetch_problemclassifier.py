from django.core.management.base import BaseCommand
from bot.models import SpojProblem
import requests
import re


class Command(BaseCommand):
    args = 'No args'
    help = 'Fetches problems from Problem classifier'

    def handle(self, *args, **options):
        PROBCLASSIFIER_ENDPOINT = 'http://problemclassifier.appspot.com/'

        try:
            response = requests.get(PROBCLASSIFIER_ENDPOINT).text
            for problem in re.findall('/problems/[A-Z]*', response):
                try:
                    p = problem.split('/')[2].trim()
                    if problem:
                        problem, created = SpojProblem.objects.get_or_create(problem=p)
                        problem.source = 'problem_classifier'
                        problem.save()
                except:
                    pass
        except:
            pass
