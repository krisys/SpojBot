from django.core.management.base import BaseCommand
from bot.models import SpojUser


class Command(BaseCommand):
    args = 'No args'
    help = 'Updates user stats'

    def handle(self, *args, **options):
        users = SpojUser.objects.all()
        for user in users:
            try:
                user.fetch_spoj_data()
            except:
                pass
