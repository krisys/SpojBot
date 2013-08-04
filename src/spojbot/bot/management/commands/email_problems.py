from django.core.management.base import BaseCommand
from bot.models import *
from django.core.mail import send_mail
from datetime import datetime


content = """
Problem for the day : http://www.spoj.com/problems/%s/

You can change your email notifications from the settings page: http://www.spojbot.com/settings

Spojbot
https://www.facebook.com/spojbot
"""


class Command(BaseCommand):
    args = 'No args'
    help = 'Email problem to users'

    def handle(self, *args, **options):
        suggestions = SuggestedProblem.objects.filter(notified=False)
        for suggestion in suggestions:
            email_ids = []
            for user in suggestion.group.groupmember_set.filter(receive_emails=True):
                email_ids.append(user.user.email)

            if email_ids:
                subject = 'Problem for the day - %s - %s' % (datetime.now().strftime("%A (%d-%B-%Y)"), suggestion.problem)
                try:
                    send_mail(subject, content % (suggestion.problem), 'SpojBot <noreply@spojbot.com>', email_ids, fail_silently=True)
                    suggestion.notified = True
                    suggestion.save()
                except:
                    pass
            else:
                suggestion.notified = True
                suggestion.save()
