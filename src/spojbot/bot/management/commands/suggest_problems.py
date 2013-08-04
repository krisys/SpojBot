from django.core.management.base import BaseCommand
from bot.models import *
from datetime import datetime


class Command(BaseCommand):
    args = 'No args'
    help = 'Suggest problem to users'

    def handle(self, *args, **options):
        spoj_users = SpojUser.objects.all()

        # Find the difficulty of problems in our DB
        all_problems_difficulty = [x.difficulty for x in SpojProblem.objects.filter(difficulty__gte=0, is_tutorial=False)]
        all_problems_count = [all_problems_difficulty.count(x) for x in range(5)]

        for spoj_user in spoj_users:
            if spoj_user.last_notified != None:
                now = datetime.now()
                diff = now - spoj_user.last_notified
                if diff.days < spoj_user.frequency:
                    continue

            # Get all submissions from the user
            submissions = Submission.objects.filter(user=spoj_user.user)

            # Find the difficulty of problems user has solved.
            problem_difficulty = [x.problem.difficulty for x in submissions if x.problem.difficulty > 0]

            # Find the count of problems a user has solved in each difficulty level.
            # if he/she has solved a level 3 problem. They need to get only level >= 3  suggestions.

            user_solved_count = [problem_difficulty.count(x) for x in range(5)]

            difficulty_range = 1

            minimum_solve_per_level = [0, 50, 90, 100, 100]

            for i in reversed(range(5)):
                if user_solved_count[i] > 0 and ((user_solved_count[i] * 100) / all_problems_count[i]) <= minimum_solve_per_level[i]:
                    difficulty_range = i
                    break

            suggestions = SpojProblem.objects.filter(difficulty__gte=difficulty_range)
            suggestions = suggestions.exclude(problem__in=[x.problem for x in submissions])
            suggestions = suggestions.order_by('-solved_by')
            print suggestions
            try:
                ProblemSuggestion.objects.create(user=spoj_user.user, problem=suggestions[0])
                spoj_user.last_notified = datetime.now()
                spoj_user.save()
            except:
                pass
