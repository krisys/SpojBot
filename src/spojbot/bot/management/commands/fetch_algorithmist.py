from django.core.management.base import BaseCommand
from bot.models import SpojProblem
import requests
import re


class Command(BaseCommand):
    args = 'No args'
    help = 'Fetches problems from Algorithmist'

    def handle(self, *args, **options):
        ALGORITHMIST_ENDPOINT = 'http://www.algorithmist.com/index.php/SPOJ_Volume_'
        PAGES = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VII']

        for page in PAGES:
            url = ALGORITHMIST_ENDPOINT + page
            try:
                response = requests.get(url).text
                for problem in re.findall('/problems/[A-Z]*/', response):
                    try:
                        SpojProblem.objects.create(problem=problem.split('/')[2])
                    except:
                        pass
            except:
                pass
