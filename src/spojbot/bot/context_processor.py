from bot.models import *


def user_info(request):
    if not request.user.is_authenticated():
        return {}

    spojuser, created = SpojUser.objects.get_or_create(user=request.user)

    if request.user.is_authenticated():
        my_groups = CodeGroup.objects.filter(groupmember__user=request.user)
    else:
        my_groups = None

    return {'my_groups': my_groups}
