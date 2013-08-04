from django.core.management.base import BaseCommand
from bot.models import *
from datetime import datetime, timedelta, date


class Command(BaseCommand):
    args = 'No args'
    help = 'Move problems from SuggestedProblem to ProblemSuggestion'

    def handle(self, *args, **options):
        for spojuser in SpojUser.objects.all():
            user_belongs_to = [x.group for x in GroupMember.objects.filter(user=spojuser.user)]
            for problem in SuggestedProblem.objects.filter(group__in=user_belongs_to).order_by('timestamp'):
                try:
                    ProblemSuggestion.objects.create(user=spojuser.user, problem=problem.problem)
                except:
                    pass
