from django.db import models
from django.contrib.auth.models import User
import requests
from datetime import datetime
from BeautifulSoup import BeautifulSoup
import re

SPOJ_ENDPOINT = "http://www.spoj.com/status/%s/signedlist/"


class SpojUser(models.Model):
    user = models.OneToOneField(User)
    spoj_handle = models.CharField(max_length=50)
    points = models.FloatField(default=0)
    rank = models.IntegerField(default=10000000)
    problems_solved = models.IntegerField(default=0)

    notify_via_email = models.BooleanField(default=True)
    last_notified = models.DateTimeField(null=True, blank=True)

    FREQUENCY_CHOICES = (
        (1, 'Daily'),
        (2, 'Once in 2 days'),
        (3, 'Once in 3 days'),
        (7, 'Weekly'),
        (15, 'Fortnightly'),
        (30, 'Monthly')
    )

    frequency = models.IntegerField(default=2,
        verbose_name='Problem Suggestion Frequency',
        choices=FREQUENCY_CHOICES)

    def __unicode__(self):
        return '%s (%s)' % (self.spoj_handle, self.user.email)

    def ppp(self):
        if self.problems_solved == 0:
            return 'NA'
        return str((self.points * 1.0) / self.problems_solved)[0:6]

    def fetch_spoj_data(self):
        if not self.spoj_handle:
            return
        response = requests.get(SPOJ_ENDPOINT % (self.spoj_handle))

        for line in response.text.split('\n'):
            if line and line[0] == '|':
                fields = line.split('|')
                if fields[4].strip() == 'AC':
                    problem, created = SpojProblem.objects.get_or_create(
                        problem=fields[3].strip())
                    dt = datetime.strptime(fields[2].strip(),
                        "%Y-%m-%d %H:%M:%S")

                    try:
                        Submission.objects.get(user=self.user,
                            problem=problem)
                    except:
                        Submission.objects.create(user=self.user,
                            problem=problem, timestamp=dt)

        self.fetch_spoj_stats()

    def fetch_spoj_stats(self):
        response = requests.get('http://www.spoj.com/users/%s/' % (
            self.spoj_handle))
        rank = re.search('>#\d+', response.text)
        points = re.search('(.* points)', response.text)
        if not rank:
            return
        self.rank = rank.group(0)[2:]

        if not points:
            return

        points = points.group()

        try:
            self.points = float(re.search("\d+.\d+", points).group())
        except:
            self.points = float(re.search("\d+", points).group())

        soup = BeautifulSoup(response.text)
        stats = soup.find("table", {"class": "problems"})
        for index, row in enumerate(stats.findAll('tr')):
            if index == 0:
                continue
            cols = []
            for col in row.findAll('td'):
                cols.append(int(col.text))

            self.problems_solved = cols[0]
        self.save()


class CodeGroup(models.Model):
    name = models.CharField(max_length=100)
    notifications = models.IntegerField(default=2,
        verbose_name='Problem Notification Frequncy')
    last_notified = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.name)


class GroupMember(models.Model):
    group = models.ForeignKey(CodeGroup)
    user = models.ForeignKey(User, null=True, blank=True)
    user_email = models.EmailField(verbose_name='Email')
    invite_accepted = models.BooleanField(default=False)
    receive_emails = models.BooleanField(default=False,
        verbose_name='Send email notifications')
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'user_email',)

    def __unicode__(self):
        return '%s - %s' % (self.group, self.user_email)


class SpojProblem(models.Model):
    problem = models.CharField(max_length=40, unique=True)
    solved_by = models.IntegerField(default=0)
    category = models.CharField(max_length=100, null=True, blank=True)
    is_tutorial = models.BooleanField(default=False)

    SOURCE_CHOICES = (
        ('problem_classifier', 'Problem Classifier'),
        ('curated', 'Curated'),
    )

    source = models.CharField(max_length=50, null=True, blank=True,
        choices=SOURCE_CHOICES)

    difficulty = models.IntegerField(default=0, null=True, blank=True)

    def __unicode__(self):
        return self.problem

    def fetch_stats(self):
        if self.is_tutorial:
            return

        response = requests.get('http://www.spoj.com/ranks/%s/' % (
            self.problem))

        soup = BeautifulSoup(response.text)
        stats = soup.find("table", {"class": "problems"})
        for index, row in enumerate(stats.findAll('tr')):
            if index == 0:
                continue
            cols = []
            for col in row.findAll('td'):
                cols.append(int(col.text))

            self.solved_by = int(cols[0])
        self.save()
        self.categorize_tutorial_problems()

    def categorize_tutorial_problems(self):
        if self.is_tutorial:
            return

        response = requests.get('http://www.spoj.com/problems/%s/' % (
            self.problem))
        if '(tutorial)' in response.text:
            self.is_tutorial = True
            self.save()


class Submission(models.Model):
    problem = models.ForeignKey(SpojProblem)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return '%s - %s' % (self.problem, self.user.email)


class ProblemSuggestion(models.Model):
    user = models.ForeignKey(User)
    problem = models.ForeignKey(SpojProblem)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'problem',)

    def __unicode__(self):
        return '%s - %s' % (self.group, self.problem)


class UserSuggestion(models.Model):
    group = models.ForeignKey(CodeGroup)
    problem = models.ForeignKey(SpojProblem)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'problem',)

    def __unicode__(self):
        return '%s' % (self.problem)


class Discussion(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(null=True, blank=True)
    group = models.ForeignKey(CodeGroup)
    owner = models.ForeignKey(User)

    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class Reply(models.Model):
    discussion = models.ForeignKey(Discussion)
    content = models.TextField()
    user = models.ForeignKey(User)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.content[:200]
