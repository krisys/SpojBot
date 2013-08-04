from django import forms
from models import *


class SpojUserForm(forms.ModelForm):

    class Meta:
        model = SpojUser
        exclude = ('user', 'rank', 'problems_solved', 'points', 'last_notified')
        fields = ['spoj_handle', 'frequency', 'notify_via_email']


class CodeGroupForm(forms.ModelForm):

    class Meta:
        model = CodeGroup
        exclude = ('last_notified',)
