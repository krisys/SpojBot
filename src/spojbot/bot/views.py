from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from models import *
from forms import SpojUserForm, CodeGroupForm
from django.core.mail import send_mail
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_exempt


class Story(object):

    def __init__(self, user, submission=None):
        self.user = user
        self.submissions = []

        if submission:
            self.submissions.append(submission)
        self.count = len(self.submissions)

    def duration(self):
        if len(self.submissions) == 1:
            return self.submissions[0].timestamp.strftime('%d %b %Y')
        else:
            start = self.submissions[-1].timestamp.strftime('%d %b %Y')
            end = self.submissions[0].timestamp.strftime('%d %b %Y')
            return start + ' - ' + end


def format_feed(feed):
    story = []
    for item in feed:
        if story:
            if item.user == story[-1].user:
                story[-1].submissions.append(item)
                story[-1].count = len(story[-1].submissions)
            else:
                story.append(Story(user=item.user, submission=item))
        else:
            story.append(Story(user=item.user, submission=item))

    return story


def index(request, template_name='index.html'):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/spoj')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def update_jobs(request):
    belongs_to = GroupMember.objects.filter(user_email=request.user.email, user=None)
    for group in belongs_to:
        group.user = request.user
        group.receive_emails = True
        group.save()

    belongs_to = GroupMember.objects.filter(user=request.user)

    if not belongs_to:
        group = CodeGroup.objects.create(name='My group', notifications=1)
        GroupMember.objects.create(user_email=request.user.email, user=request.user, group=group, is_owner=True, receive_emails=True)


@login_required
def spoj(request, template_name='spoj.html'):
    update_jobs(request)
    groups = [x.group for x in GroupMember.objects.filter(user=request.user)]

    users = [request.user]
    users += [x.user for x in GroupMember.objects.filter(group__in=groups)]

    feed = Submission.objects.filter(user__in=users).order_by('-timestamp')[:300]
    feed = format_feed(feed)

    suggested_problems = ProblemSuggestion.objects.filter(user=request.user)

    solved_by_me = SpojProblem.objects.filter(submission__user=request.user)

    friend_suggestions = UserSuggestion.objects.filter(group__in=groups)
    friend_suggestions = friend_suggestions.exclude(problem__in=solved_by_me)
    todo = suggested_problems.exclude(problem__in=solved_by_me)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@login_required
def config(request, template_name='settings.html'):
    user, created = SpojUser.objects.get_or_create(user=request.user)

    form = SpojUserForm(request.POST or None, instance=user)
    # SettingsFormSet = modelformset_factory(GroupMember, fields=['receive_emails'], extra=0)
    # formset = SettingsFormSet(request.POST or None, queryset=GroupMember.objects.filter(user=request.user))
    # if formset.is_valid():
    #     formset.save()

    if form.is_valid():
        form.save()
        user.fetch_spoj_data()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@login_required
def create_group(request):
    group = CodeGroup.objects.create(name=request.POST['group'])
    GroupMember.objects.create(user_email=request.user.email, user=request.user, group=group, is_owner=True, receive_emails=True)
    return HttpResponseRedirect("/group/%d/" % (group.id))


def user_belongs_to_group(user, group_members):
    for member in group_members:
        if member.user == user:
            return True
    return False


@login_required
def view_group(request, id, template_name="group.html"):
    try:
        group = CodeGroup.objects.get(id=id)
        group_members = GroupMember.objects.filter(group=group).order_by('user__spojuser__rank')
        if request.user.is_superuser:
            pass
        elif not user_belongs_to_group(request.user, group_members):
            return HttpResponseRedirect("/")

    except:
        return HttpResponseRedirect("/")

    groups = [x.group for x in GroupMember.objects.filter(user=request.user)]

    group_users = []
    for member in group_members:
        if member.is_owner and member.user == request.user:
            is_owner = True
        group_users.append(member.user)

    feed = Submission.objects.filter(user__in=group_users).order_by('-timestamp')[:300]
    feed = format_feed(feed)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


@login_required
def view_group_members(request, id, template_name="group_members.html"):
    try:
        group = CodeGroup.objects.get(id=id)
        group_members = GroupMember.objects.filter(group=group)

        if not user_belongs_to_group(request.user, group_members):
            return HttpResponseRedirect("/")

        current_user = GroupMember.objects.get(user=request.user, group=group)

        if not current_user.is_owner:
            return HttpResponseRedirect("/")

        if request.POST:
            email = request.POST['email']
            if validateEmail(email):
                user = get_or_none(User, email=email)
                g = GroupMember.objects.create(user_email=email, user=user, group=group)

                group_members = GroupMember.objects.filter(group=group)
                if not user:
                    try:
                        subject = 'I just added you to my SpojBot Group!'
                        content = 'Check this out.. This site emails one problem everyday to all members of the group. http://www.spojbot.com '
                        send_mail(subject, content, '%s <noreply@spojbot.com>' % (request.user.get_full_name()), [email], fail_silently=False)
                    except:
                        pass
                else:
                    g.receive_emails = True
                    g.save()

        form = CodeGroupForm(request.POST or None, instance=group)
        if form.is_valid():
            form.save()

    except:
        return HttpResponseRedirect("/")

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@login_required
def delete_member(request, id, template_name="delete_member.html"):
    member = GroupMember.objects.get(id=id)
    group = member.group
    current_user = GroupMember.objects.get(user=request.user, group=group)

    if not current_user.is_owner:
        return HttpResponseRedirect("/")
    if request.POST:
        member.delete()
        return HttpResponseRedirect("/group/%d/" % group.id)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@login_required
@csrf_exempt
def delete_group(request):
    response = {'status': 'Error'}

    group = CodeGroup.objects.get(id=request.POST['id'])
    current_user = GroupMember.objects.get(user=request.user, group=group)

    if current_user.is_owner:
        group.delete()
        response['status'] = 'OK'
        return HttpResponse(json.dumps(response))

    return HttpResponse(json.dumps(response))


@login_required
@csrf_exempt
def leave_group(request):
    response = {'status': 'Error'}

    try:
        group = CodeGroup.objects.get(id=request.POST['id'])
        current_user = GroupMember.objects.get(user=request.user, group=group)
        current_user.delete()
        response['status'] = 'OK'
    except:
        pass

    return HttpResponse(json.dumps(response))


@login_required
def suggest_problem(request):
    response = {'status': 'Error'}

    try:
        group = CodeGroup.objects.get(id=request.GET.get('id'))
        current_user = GroupMember.objects.get(user=request.user, group=group)
        if current_user:
            # belongs to this group
            problem = request.GET.get('problem')
            if '/' in problem:
                return HttpResponse(json.dumps(response))
            problem, created = SpojProblem.objects.get_or_create(problem=problem)
            if not created:
                problem.source = 'user_suggestion'
                problem.save()
            try:
                UserSuggestion.objects.get(group=group, problem=problem)
            except:
                UserSuggestion.objects.get_or_create(group=group, problem=problem, user=request.user)
            response['status'] = 'OK'
            return HttpResponse(json.dumps(response))
    except:
        pass

    return HttpResponse(json.dumps(response))
